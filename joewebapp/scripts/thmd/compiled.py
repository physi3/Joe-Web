import struct
import zlib

from .parser import (
    Dialogue,
    DialogueLine,
    Header,
    LineBreak,
    Script,
    StageDirection,
    get_referenced_characters,
)


MAGIC = b"THMC"
VERSION = 2
HEADER = struct.Struct("!4sBI")
LINE_HEADER = struct.Struct("!B")
SUBLINE_HEADER = struct.Struct("!B")
INTEGER = struct.Struct("!i")
STRING_LENGTH = struct.Struct("!I")

HEADER_LINE = 1
STAGE_DIRECTION_LINE = 2
DIALOGUE_LINE = 3
DIALOGUE_SUBLINE = 1
STAGE_DIRECTION_SUBLINE = 2
LINE_BREAK_SUBLINE = 3


def _pack_string(value):
    encoded = value.encode("utf-8")
    return STRING_LENGTH.pack(len(encoded)) + encoded


def _unpack_string(payload, offset):
    if offset + STRING_LENGTH.size > len(payload):
        raise ValueError("THMC string length is truncated")

    value_size = STRING_LENGTH.unpack_from(payload, offset)[0]
    offset += STRING_LENGTH.size
    value_end = offset + value_size
    if value_end > len(payload):
        raise ValueError("THMC string is truncated")

    return bytes(payload[offset:value_end]).decode("utf-8"), value_end


def Compile(script):
    payload = bytearray()
    payload.extend(struct.pack("!I", len(script.scriptLines)))

    for line in script.scriptLines:
        if type(line) is Header:
            payload.extend(LINE_HEADER.pack(HEADER_LINE))
            payload.extend(LINE_HEADER.pack(line.hType))
            payload.extend(INTEGER.pack(line.index))
            payload.extend(_pack_string(line.title))
        elif type(line) is StageDirection:
            payload.extend(LINE_HEADER.pack(STAGE_DIRECTION_LINE))
            payload.extend(_pack_string(line.content))
        elif type(line) is DialogueLine:
            payload.extend(LINE_HEADER.pack(DIALOGUE_LINE))
            payload.extend(_pack_string(line.speaker))
            payload.extend(struct.pack("!I", len(line.subLines)))
            for subline in line.subLines:
                if type(subline) is Dialogue:
                    payload.extend(SUBLINE_HEADER.pack(DIALOGUE_SUBLINE))
                    payload.extend(_pack_string(subline.content))
                elif type(subline) is StageDirection:
                    payload.extend(SUBLINE_HEADER.pack(STAGE_DIRECTION_SUBLINE))
                    payload.extend(_pack_string(subline.content))
                elif type(subline) is LineBreak:
                    payload.extend(SUBLINE_HEADER.pack(LINE_BREAK_SUBLINE))
                else:
                    raise TypeError(f"Unsupported dialogue subline: {type(subline).__name__}")
        else:
            raise TypeError(f"Unsupported script line: {type(line).__name__}")

    compressed = zlib.compress(bytes(payload), level=9)
    return HEADER.pack(MAGIC, VERSION, len(compressed)) + compressed


def Parse(data):
    if len(data) < HEADER.size:
        raise ValueError("THMC file is too short")

    magic, version, payload_size = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise ValueError("Not a THMC file")
    if version != VERSION:
        raise ValueError(f"Unsupported THMC version: {version}")

    payload_start = HEADER.size
    payload_end = payload_start + payload_size
    if payload_end != len(data):
        raise ValueError("THMC payload has an invalid size")

    payload = memoryview(zlib.decompress(data[payload_start:payload_end]))
    if len(payload) < 4:
        raise ValueError("THMC payload is too short")

    line_count = struct.unpack_from("!I", payload)[0]
    offset = 4
    script_lines = []

    for _ in range(line_count):
        if offset + LINE_HEADER.size > len(payload):
            raise ValueError("THMC line header is truncated")

        line_type = LINE_HEADER.unpack_from(payload, offset)[0]
        offset += LINE_HEADER.size
        if line_type == HEADER_LINE:
            if offset + LINE_HEADER.size + INTEGER.size > len(payload):
                raise ValueError("THMC header line is truncated")
            header_type = LINE_HEADER.unpack_from(payload, offset)[0]
            offset += LINE_HEADER.size
            index = INTEGER.unpack_from(payload, offset)[0]
            offset += INTEGER.size
            title, offset = _unpack_string(payload, offset)
            header = object.__new__(Header)
            header.hType = header_type
            header.index = index
            header.title = title
            script_lines.append(header)
        elif line_type == STAGE_DIRECTION_LINE:
            content, offset = _unpack_string(payload, offset)
            stage_direction = object.__new__(StageDirection)
            stage_direction.content = content
            stage_direction.referencedCharacters = get_referenced_characters(content)
            script_lines.append(stage_direction)
        elif line_type == DIALOGUE_LINE:
            speaker, offset = _unpack_string(payload, offset)
            if offset + STRING_LENGTH.size > len(payload):
                raise ValueError("THMC dialogue line is truncated")
            subline_count = STRING_LENGTH.unpack_from(payload, offset)[0]
            offset += STRING_LENGTH.size
            dialogue_line = object.__new__(DialogueLine)
            dialogue_line.speaker = speaker
            dialogue_line.subLines = []
            for _ in range(subline_count):
                if offset + SUBLINE_HEADER.size > len(payload):
                    raise ValueError("THMC dialogue subline is truncated")
                subline_type = SUBLINE_HEADER.unpack_from(payload, offset)[0]
                offset += SUBLINE_HEADER.size
                if subline_type == DIALOGUE_SUBLINE:
                    content, offset = _unpack_string(payload, offset)
                    subline = object.__new__(Dialogue)
                    subline.content = content
                elif subline_type == STAGE_DIRECTION_SUBLINE:
                    content, offset = _unpack_string(payload, offset)
                    subline = object.__new__(StageDirection)
                    subline.content = content
                    subline.referencedCharacters = get_referenced_characters(content)
                elif subline_type == LINE_BREAK_SUBLINE:
                    subline = object.__new__(LineBreak)
                else:
                    raise ValueError(f"Unknown THMC subline type: {subline_type}")
                dialogue_line.subLines.append(subline)
            script_lines.append(dialogue_line)
        else:
            raise ValueError(f"Unknown THMC line type: {line_type}")

    if offset != len(payload):
        raise ValueError("THMC payload contains trailing data")

    return Script(script_lines)