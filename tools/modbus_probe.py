#!/usr/bin/env python3
"""Aktiv Modbus RTU-master mot värmepumpens styrkort.

Används när WiFi-modulen är BORTKOPPLAD – då är bussen ledig och du kan bli
master själv. Kör aldrig detta samtidigt som originalmodulen pollar, då krockar
ni på bussen.

Exempel:
    # 1. Vilken slavadress svarar?
    python3 tools/modbus_probe.py --port /dev/ttyUSB0 --scan-slaves

    # 2. Dumpa allt läsbart
    python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --dump

    # 3. Tryck på knappar i panelen och se vilka register som ändras
    python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --watch
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import protocol  # noqa: E402

try:
    import serial  # type: ignore
except ImportError:
    sys.exit("pyserial saknas – kör: pip install -r requirements.txt")

READ_FUNCS = {"coil": 1, "discrete": 2, "holding": 3, "input": 4}


class ModbusError(Exception):
    pass


class Master:
    def __init__(self, port: str, baud: int, parity: str, stopbits: float,
                 timeout: float):
        bits = 1 + 8 + (0 if parity == "N" else 1) + stopbits
        self.ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity={"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN,
                    "O": serial.PARITY_ODD}[parity],
            stopbits=serial.STOPBITS_TWO if stopbits == 2 else serial.STOPBITS_ONE,
            timeout=timeout,
            inter_byte_timeout=max(3.5 * bits / baud, 0.002),
        )

    def close(self) -> None:
        self.ser.close()

    def transact(self, pdu: bytes) -> bytes:
        self.ser.reset_input_buffer()
        self.ser.write(protocol.modbus_append_crc(pdu))
        self.ser.flush()
        frame = self.ser.read(256)
        if not frame:
            raise ModbusError("inget svar")
        if not protocol.modbus_crc_ok(frame):
            raise ModbusError(f"CRC-fel: {frame.hex(' ')}")
        if frame[1] & 0x80:
            code = frame[2]
            raise ModbusError(
                f"exception {code}: "
                f"{protocol.MODBUS_EXCEPTIONS.get(code, 'okänd')}")
        return frame[2:-2]

    def read(self, unit: int, kind: str, addr: int, count: int) -> list[int]:
        func = READ_FUNCS[kind]
        body = self.transact(bytes([unit, func,
                                    addr >> 8, addr & 0xFF,
                                    count >> 8, count & 0xFF]))
        data = body[1:]
        if func in (3, 4):
            return [(data[i] << 8) | data[i + 1] for i in range(0, len(data) - 1, 2)]
        bits: list[int] = []
        for byte in data:
            bits.extend((byte >> i) & 1 for i in range(8))
        return bits[:count]

    def write_coil(self, unit: int, addr: int, on: bool) -> None:
        val = 0xFF00 if on else 0x0000
        self.transact(bytes([unit, 5, addr >> 8, addr & 0xFF,
                             val >> 8, val & 0xFF]))

    def write_register(self, unit: int, addr: int, value: int) -> None:
        self.transact(bytes([unit, 6, addr >> 8, addr & 0xFF,
                             value >> 8, value & 0xFF]))


def as_temp(raw: int) -> str:
    """Fairland/IPS "temperaturtyp 1": faktisk grad = (rått - 60) / 2."""
    value = (raw - 60) / 2
    return f"{value:6.1f}°C" if -30 <= value <= 120 else "        "


def read_block(master: Master, unit: int, kind: str, start: int, end: int,
               chunk: int) -> dict[int, int]:
    """Läs [start, end) och hoppa över adresser som ger exception."""
    out: dict[int, int] = {}
    addr = start
    while addr < end:
        count = min(chunk, end - addr)
        try:
            for offset, value in enumerate(master.read(unit, kind, addr, count)):
                out[addr + offset] = value
        except ModbusError:
            # Blocket innehåller en ogiltig adress – testa en i taget.
            if count > 1:
                for single in range(addr, addr + count):
                    try:
                        out[single] = master.read(unit, kind, single, 1)[0]
                    except ModbusError:
                        pass
        addr += count
    return out


def do_scan_slaves(master: Master, args: argparse.Namespace) -> int:
    print(f"Skannar slavadress {args.unit_from}–{args.unit_to} ...")
    found = []
    for unit in range(args.unit_from, args.unit_to + 1):
        for kind in ("holding", "input", "discrete"):
            try:
                master.read(unit, kind, 0, 1)
            except ModbusError as exc:
                # Ett exception-svar bevisar också att slaven finns.
                if "exception" in str(exc):
                    found.append(unit)
                    print(f"  adress {unit}: svarar (exception på {kind})")
                    break
                continue
            found.append(unit)
            print(f"  adress {unit}: SVARAR ({kind} 0 läsbart)")
            break
    if not found:
        print("\nIngen slav svarade. Kontrollera: A/B kastade om? GND kopplad? "
              "Rätt baud/paritet? Sitter originalmodulen kvar och stör?")
        return 1
    print(f"\nHittade: {found}")
    return 0


def do_dump(master: Master, args: argparse.Namespace) -> int:
    plan = [
        ("discrete", 0, args.bits, "Discrete inputs (status/larm, skrivskyddade)"),
        ("coil", 0, 8, "Coils (på/av, skrivbara)"),
        ("input", 0, args.regs, "Input registers (mätvärden)"),
        ("holding", 0, args.regs, "Holding registers (inställningar)"),
    ]
    for kind, start, end, title in plan:
        print(f"\n=== {title} — {kind} {start}..{end - 1} ===")
        values = read_block(master, args.unit, kind, start, end, args.chunk)
        if not values:
            print("  (inget svar)")
            continue
        for addr in sorted(values):
            raw = values[addr]
            if kind in ("input", "holding"):
                print(f"  {addr:>4}: {raw:>6}  0x{raw:04X}  {as_temp(raw)}")
            else:
                print(f"  {addr:>4}: {raw}")
    print("\nTips: '°C'-kolumnen är en gissning – (rått-60)/2. Jämför med vad "
          "panelen visar för att bekräfta skalningen.")
    return 0


def parse_range(spec: str) -> tuple[str, int, int]:
    kind, _, rng = spec.partition(":")
    start, _, end = rng.partition("-")
    return kind, int(start), int(end)


def do_watch(master: Master, args: argparse.Namespace) -> int:
    ranges = [parse_range(r) for r in args.watch_range]
    previous: dict[tuple[str, int], int] = {}
    print("Pollar. Ändra något i panelen/appen och se vad som rör sig. "
          "Ctrl-C avslutar.\n")
    try:
        while True:
            for kind, start, end in ranges:
                values = read_block(master, args.unit, kind, start, end, args.chunk)
                for addr, raw in values.items():
                    key = (kind, addr)
                    old = previous.get(key)
                    if old is None:
                        previous[key] = raw
                        continue
                    if old != raw:
                        previous[key] = raw
                        stamp = time.strftime("%H:%M:%S")
                        extra = f"  ({as_temp(raw).strip()})" if kind in ("input", "holding") else ""
                        print(f"[{stamp}] {kind}[{addr}]: {old} -> {raw}{extra}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nAvbrutet.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--parity", choices=["N", "E", "O"], default="N")
    ap.add_argument("--stopbits", type=float, choices=[1, 2], default=1)
    ap.add_argument("--timeout", type=float, default=0.5)
    ap.add_argument("--unit", type=int, default=1, help="slavadress")
    ap.add_argument("--chunk", type=int, default=8, help="register per läsning")

    ap.add_argument("--scan-slaves", action="store_true")
    ap.add_argument("--unit-from", type=int, default=1)
    ap.add_argument("--unit-to", type=int, default=32)

    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--regs", type=int, default=32, help="antal register i --dump")
    ap.add_argument("--bits", type=int, default=96, help="antal bitar i --dump")

    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--watch-range", action="append",
                    default=None, metavar="TYP:START-SLUT",
                    help="t.ex. input:0-16 (kan anges flera gånger)")
    ap.add_argument("--interval", type=float, default=2.0)

    ap.add_argument("--read", nargs=3, metavar=("TYP", "ADDR", "ANTAL"))
    ap.add_argument("--write-coil", nargs=2, metavar=("ADDR", "0|1"))
    ap.add_argument("--write-reg", nargs=2, metavar=("ADDR", "VÄRDE"))
    ap.add_argument("--yes", action="store_true",
                    help="krävs för att skriva till värmepumpen")

    args = ap.parse_args()
    if args.watch_range is None:
        args.watch_range = ["discrete:0-18", "input:0-16", "holding:0-26"]

    master = Master(args.port, args.baud, args.parity, args.stopbits, args.timeout)
    try:
        if args.scan_slaves:
            return do_scan_slaves(master, args)
        if args.dump:
            return do_dump(master, args)
        if args.watch:
            return do_watch(master, args)
        if args.read:
            kind, addr, count = args.read[0], int(args.read[1]), int(args.read[2])
            print(master.read(args.unit, kind, addr, count))
            return 0
        if args.write_coil or args.write_reg:
            if not args.yes:
                print("Skrivning påverkar värmepumpen på riktigt. "
                      "Lägg till --yes om du är säker.")
                return 1
            if args.write_coil:
                master.write_coil(args.unit, int(args.write_coil[0]),
                                  args.write_coil[1] not in ("0", "off", "false"))
            else:
                master.write_register(args.unit, int(args.write_reg[0]),
                                      int(args.write_reg[1]))
            print("OK")
            return 0
        ap.print_help()
        return 1
    except ModbusError as exc:
        print(f"Modbus-fel: {exc}")
        return 1
    finally:
        master.close()


if __name__ == "__main__":
    raise SystemExit(main())
