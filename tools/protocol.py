"""Ramavkodning för de två protokoll en pool-WiFi-modul brukar prata.

Ingen extern dependency – bara stdlib. Används av rs485_sniff.py och
modbus_probe.py.
"""

from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------
# Modbus RTU
# --------------------------------------------------------------------------

MODBUS_FUNCTIONS = {
    1: "Read Coils",
    2: "Read Discrete Inputs",
    3: "Read Holding Registers",
    4: "Read Input Registers",
    5: "Write Single Coil",
    6: "Write Single Register",
    15: "Write Multiple Coils",
    16: "Write Multiple Registers",
    17: "Report Server ID",
    23: "Read/Write Multiple Registers",
}

MODBUS_EXCEPTIONS = {
    1: "Illegal function",
    2: "Illegal data address",
    3: "Illegal data value",
    4: "Server device failure",
    5: "Acknowledge",
    6: "Server device busy",
    8: "Memory parity error",
    10: "Gateway path unavailable",
    11: "Gateway target failed to respond",
}


def modbus_crc(data: bytes) -> int:
    """CRC-16/MODBUS. Returnerar heltal, little-endian på tråden."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def modbus_append_crc(pdu: bytes) -> bytes:
    crc = modbus_crc(pdu)
    return pdu + bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def modbus_crc_ok(frame: bytes) -> bool:
    if len(frame) < 4:
        return False
    return modbus_crc(frame[:-2]) == frame[-2] | (frame[-1] << 8)


def _words(payload: bytes) -> list[int]:
    return [
        (payload[i] << 8) | payload[i + 1]
        for i in range(0, len(payload) - 1, 2)
    ]


def decode_modbus(frame: bytes) -> str:
    """Beskriv en Modbus RTU-ram i klartext. Antar att CRC redan validerats."""
    if len(frame) < 4:
        return "för kort för Modbus"

    unit, func = frame[0], frame[1]
    body = frame[2:-2]

    if func & 0x80:
        base = func & 0x7F
        code = body[0] if body else 0
        return (
            f"slav {unit} EXCEPTION på fn {base} "
            f"({MODBUS_FUNCTIONS.get(base, '?')}): "
            f"{code} {MODBUS_EXCEPTIONS.get(code, 'okänd')}"
        )

    name = MODBUS_FUNCTIONS.get(func, f"fn {func}")

    # Request: adress + antal (4 databytes). Response: byte count + data.
    if func in (1, 2, 3, 4):
        if len(body) == 4:
            addr = (body[0] << 8) | body[1]
            count = (body[2] << 8) | body[3]
            return f"slav {unit} REQ  {name} addr={addr} antal={count}"
        if body and body[0] == len(body) - 1:
            data = body[1:]
            if func in (3, 4):
                vals = _words(data)
                return f"slav {unit} RESP {name} värden={vals}"
            bits: list[int] = []
            for byte in data:
                bits.extend((byte >> i) & 1 for i in range(8))
            return f"slav {unit} RESP {name} bitar={bits}"

    if func in (5, 6) and len(body) == 4:
        addr = (body[0] << 8) | body[1]
        val = (body[2] << 8) | body[3]
        extra = " (PÅ)" if func == 5 and val == 0xFF00 else ""
        return f"slav {unit} {name} addr={addr} värde={val}{extra}"

    if func in (15, 16):
        if len(body) >= 5 and body[4] == len(body) - 5:
            addr = (body[0] << 8) | body[1]
            count = (body[2] << 8) | body[3]
            data = body[5:]
            payload = _words(data) if func == 16 else list(data)
            return f"slav {unit} REQ  {name} addr={addr} antal={count} data={payload}"
        if len(body) == 4:
            addr = (body[0] << 8) | body[1]
            count = (body[2] << 8) | body[3]
            return f"slav {unit} RESP {name} addr={addr} antal={count}"

    return f"slav {unit} {name} body={body.hex(' ')}"


def find_modbus_frames(buf: bytes, max_len: int = 256) -> list[tuple[int, int]]:
    """Hitta (offset, längd) för alla delsträngar med giltig Modbus-CRC.

    Används på en rå byteström där ramgränserna är okända – t.ex. när
    sniffern inte lyckats separera ramar på tidsluckor.
    """
    hits: list[tuple[int, int]] = []
    pos = 0
    while pos < len(buf) - 3:
        for length in range(4, min(max_len, len(buf) - pos) + 1):
            if modbus_crc_ok(buf[pos : pos + length]):
                hits.append((pos, length))
                pos += length
                break
        else:
            pos += 1
    return hits


# --------------------------------------------------------------------------
# Tuya MCU serial protocol (55 AA ...)
# --------------------------------------------------------------------------

TUYA_COMMANDS = {
    0x00: "Heartbeat",
    0x01: "Product info",
    0x02: "Working mode",
    0x03: "WiFi status",
    0x04: "Reset WiFi",
    0x05: "Reset WiFi + select mode",
    0x06: "DP command (moln -> MCU)",
    0x07: "DP status (MCU -> modul)",
    0x08: "Query DP status",
    0x1C: "Set time",
}

TUYA_DP_TYPES = {0: "raw", 1: "bool", 2: "value", 3: "string", 4: "enum", 5: "bitmap"}


@dataclass
class TuyaFrame:
    version: int
    command: int
    payload: bytes

    def describe(self) -> str:
        name = TUYA_COMMANDS.get(self.command, f"cmd 0x{self.command:02X}")
        if self.command in (0x06, 0x07) and self.payload:
            return f"Tuya {name}: " + "; ".join(_tuya_dps(self.payload))
        return f"Tuya {name} payload={self.payload.hex(' ') or '-'}"


def _tuya_dps(payload: bytes) -> list[str]:
    out: list[str] = []
    i = 0
    while i + 4 <= len(payload):
        dp_id = payload[i]
        dp_type = payload[i + 1]
        length = (payload[i + 2] << 8) | payload[i + 3]
        data = payload[i + 4 : i + 4 + length]
        i += 4 + length
        type_name = TUYA_DP_TYPES.get(dp_type, str(dp_type))
        if dp_type in (1, 4) and len(data) == 1:
            value: object = data[0]
        elif dp_type == 2 and len(data) == 4:
            value = int.from_bytes(data, "big", signed=True)
        elif dp_type == 3:
            value = data.decode("utf-8", "replace")
        else:
            value = data.hex(" ")
        out.append(f"DP{dp_id}({type_name})={value}")
    return out


def decode_tuya(frame: bytes) -> str | None:
    """Avkoda en Tuya MCU-ram. Returnerar None om det inte är en giltig ram."""
    if len(frame) < 7 or frame[0] != 0x55 or frame[1] != 0xAA:
        return None
    length = (frame[4] << 8) | frame[5]
    if len(frame) != 6 + length + 1:
        return None
    if (sum(frame[:-1]) & 0xFF) != frame[-1]:
        return None
    return TuyaFrame(frame[2], frame[3], frame[6:-1]).describe()


def find_tuya_frames(buf: bytes) -> list[tuple[int, int]]:
    hits: list[tuple[int, int]] = []
    pos = 0
    while pos < len(buf) - 6:
        if buf[pos] == 0x55 and buf[pos + 1] == 0xAA:
            length = (buf[pos + 4] << 8) | buf[pos + 5]
            total = 7 + length
            if pos + total <= len(buf) and decode_tuya(buf[pos : pos + total]):
                hits.append((pos, total))
                pos += total
                continue
        pos += 1
    return hits
