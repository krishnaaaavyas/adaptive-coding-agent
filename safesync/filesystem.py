"""Local filesystem boundary. Links and special files are unsupported."""

import hashlib
import os
import stat
import tempfile
from fnmatch import fnmatchcase
from pathlib import Path, PureWindowsPath

from .models import FileEntry, SyncConfig


def reject_links(path: Path):
    # lstat also catches dangling links and Windows junction/reparse points.
    for component in (*reversed(path.parents), path):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"Symbolic links/reparse points are unsupported: {component}")


def validate_config(config: SyncConfig) -> SyncConfig:
    source = Path(os.path.abspath(config.source))
    destination = Path(os.path.abspath(config.destination))
    reject_links(source)
    reject_links(destination)
    source, destination = source.resolve(), destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Source and destination must be separate, non-nested directories")
    if not source.is_dir():
        raise ValueError("Source must be an existing directory")
    if destination.exists() and not destination.is_dir():
        raise ValueError("Destination must be a directory or absent")
    return SyncConfig(source, destination, config.delete_extra, config.ignore)


def validate_relative(path: str):
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        raise ValueError("Invalid relative file path")
    windows = PureWindowsPath(path)
    if path.startswith("/") or windows.drive or windows.root:
        raise ValueError(f"Absolute paths are forbidden: {path}")
    for part in path.split("/"):
        if part in ("", ".", "..") or ":" in part or part.endswith((".", " ")):
            raise ValueError(f"Unsafe relative path: {path}")
        # Reject device aliases on every platform so a plan is portable.
        base = part.split(".", 1)[0].upper()
        if base in {"CON", "PRN", "AUX", "NUL"} or (
            len(base) == 4 and base[:3] in {"COM", "LPT"} and base[3] in "123456789"
        ):
            raise ValueError(f"Device paths are forbidden: {path}")


def file_path(root: Path, relative: str) -> Path:
    validate_relative(relative)
    candidate = root.joinpath(*relative.split("/"))
    reject_links(candidate)
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("File path escapes configured root")
    return candidate


def ignored(path: str, patterns: tuple[str, ...]) -> bool:
    # Match each path and its directory prefixes; matching a directory excludes its tree.
    parts = path.split("/")
    prefixes = ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]
    return any(fnmatchcase(prefix, pattern) for prefix in prefixes for pattern in patterns)


def read_entry(root: Path, relative: str) -> FileEntry | None:
    path = file_path(root, relative)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"Expected ordinary file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return FileEntry(relative, info.st_size, digest.hexdigest())


def scan(root: Path, patterns: tuple[str, ...]) -> tuple[FileEntry, ...]:
    reject_links(root)
    if not root.exists():
        return ()
    entries = []

    def visit(directory):
        for path in sorted(directory.iterdir(), key=lambda p: p.name):
            relative = path.relative_to(root).as_posix()
            # Links are rejected even when they match ignore patterns.
            reject_links(path)
            info = path.lstat()
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise ValueError(f"Unsupported filesystem entry: {path}")
            if ignored(relative, patterns):
                continue
            if stat.S_ISDIR(info.st_mode):
                visit(path)
            else:
                entry = read_entry(root, relative)
                if entry is None:
                    raise ValueError(f"File disappeared during scan: {path}")
                entries.append(entry)

    visit(root)
    return tuple(sorted(entries, key=lambda entry: entry.path))


def write_file(config: SyncConfig, relative: str, expected: FileEntry):
    source = file_path(config.source, relative)
    destination = file_path(config.destination, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_path(config.destination, relative)
    temporary = None
    try:
        # Replace the destination inode; never truncate a potentially shared hard link.
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".safesync-",
                                         delete=False) as output:
            temporary = Path(output.name)
            digest = hashlib.sha256()
            size = 0
            with source.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        if size != expected.size or digest.hexdigest() != expected.sha256:
            raise ValueError("Source changed during copy; destination file was not replaced")
        file_path(config.destination, relative)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def delete_file(config: SyncConfig, relative: str):
    if not config.delete_extra:
        raise ValueError("Deletion requires delete_extra=true")
    file_path(config.destination, relative).unlink()
