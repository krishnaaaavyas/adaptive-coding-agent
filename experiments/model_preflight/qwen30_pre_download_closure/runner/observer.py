"""Scoped100ms observer. GPU queries only in an explicitly authorized native run."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import threading
import time

VERSION = 'qwen30-observer-v1'


def host_memory(pid):
    if os.name == 'nt':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [(n, ctypes.c_size_t) for n in [
                'PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage',
                'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage']]
        kernel, psapi = ctypes.WinDLL('kernel32', use_last_error=True), ctypes.WinDLL('psapi', use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
        if not handle:
            return None
        try:
            c = Counters()
            c.cb = ctypes.sizeof(c)
            if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(c), c.cb):
                return None
            return {'RSS_bytes': c.WorkingSetSize, 'process_peak_bytes': c.PeakWorkingSetSize}
        finally:
            kernel.CloseHandle(handle)
    rows = {}
    for line in Path(f'/proc/{pid}/status').read_text(encoding='utf-8').splitlines():
        if line.startswith(('VmRSS:', 'VmHWM:')):
            key, value = line.split(':', 1)
            rows[key] = int(value.split()[0]) * 1024
    if 'VmRSS' not in rows:
        return None
    result={'RSS_bytes': rows['VmRSS'], 'process_peak_bytes': rows.get('VmHWM')}
    try:
        for line in Path(f'/proc/{pid}/smaps_rollup').read_text(encoding='utf-8').splitlines():
            if line.startswith('Pss:'):result['PSS_bytes']=int(line.split()[1])*1024
        cg=next(s.split(':',2)[2] for s in Path(f'/proc/{pid}/cgroup').read_text(encoding='utf-8').splitlines() if s.startswith('0::'))
        root=Path('/sys/fs/cgroup')/cg.lstrip('/')
        for file in ['memory.current','memory.peak']:
            result['cgroup_'+file]=int((root/file).read_text(encoding='utf-8').strip())
        result['cgroup_path']=str(root)
    except (OSError,ValueError,StopIteration):
        result['cgroup_PSS_complete']=False
    else:result['cgroup_PSS_complete']=True
    return result


class Observer:
    def __init__(self, pid, path, selected_gpu_uuid=None):
        self.pid, self.path, self.uuid = pid, Path(path), selected_gpu_uuid
        self.stop = threading.Event()
        self.samples, self.errors = [], []
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def loop(self):
        while not self.stop.is_set():
            sample = {'monotonic_ns': time.monotonic_ns(), 'pid': self.pid, 'GPU_bytes': None}
            try:
                sample['host_memory'] = host_memory(self.pid)
                if self.uuid is not None:
                    text = subprocess.check_output(['nvidia-smi', '--id=' + self.uuid,
                        '--query-gpu=memory.used', '--format=csv,noheader,nounits'], timeout=2, text=True)
                    sample['GPU_bytes'] = int(text.strip()) * 1024 * 1024
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                sample['host_memory'] = None
                self.errors.append(type(exc).__name__)
            self.samples.append(sample)
            self.stop.wait(0.1)

    def start(self):
        self.thread.start()

    def finish(self):
        self.stop.set()
        self.thread.join(timeout=3)
        gaps = [(b['monotonic_ns'] - a['monotonic_ns']) / 1e6 for a, b in zip(self.samples, self.samples[1:])]
        hosts = [s['host_memory']['process_peak_bytes'] for s in self.samples if s.get('host_memory') and s['host_memory']['process_peak_bytes'] is not None]
        GPUs = [s['GPU_bytes'] for s in self.samples if s['GPU_bytes'] is not None]
        obj = {'version': VERSION, 'sample_interval_ms': 100, 'samples': self.samples, 'errors': self.errors,
            'max_gap_ms': max(gaps) if gaps else None, 'peak_host_RAM': max(hosts) if hosts else None,
            'peak_VRAM': max(GPUs) if GPUs else None,
            'coverage': 'PENDING' if not hosts or self.errors or any(g > 200 for g in gaps) else 'HOST_COUNTERS_AVAILABLE',
            'GPU_queries_performed': self.uuid is not None,
            'phase_complete_peak_proof': False,
            'limitations': 'RSS/HWM+polling alone do not certify phase-wide cgroup/PSS/GPU framework peaks; native executor requires target observer support receipts'}
        self.path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
        return obj
