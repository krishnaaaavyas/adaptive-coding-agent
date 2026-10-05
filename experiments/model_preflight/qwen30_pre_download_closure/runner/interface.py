"""Shared transport shape. No model is imported by this module."""
import hashlib
import json

VERSION = 'qwen30-runner-v1'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()


def token_bytes(ids, table):
    pieces = []
    for token in ids:
        if type(token) is not int or token < 0 or str(token) not in table:
            raise ValueError('unknown or ill-typed token ID')
        pieces.append(bytes.fromhex(table[str(token)]))
    return b''.join(pieces)


def native_byte_table(tokenizer_json):
    """Invert authenticated ByteLevel byte alphabet; special tokens remain UTF8."""
    visible = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    chars = visible.copy()
    other = 0
    for byte in range(256):
        if byte not in visible:
            visible.append(byte)
            chars.append(256 + other)
            other += 1
    inverse = {chr(char): byte for byte, char in zip(visible, chars)}
    special = {r['id']: r['content'] for r in tokenizer_json['added_tokens']}
    table = {}
    for text, token in tokenizer_json['model']['vocab'].items():
        table[str(token)] = (special[token].encode('utf-8') if token in special else bytes(inverse[c] for c in text)).hex()
    for token, text in special.items():
        table[str(token)] = text.encode('utf-8').hex()
    return table
