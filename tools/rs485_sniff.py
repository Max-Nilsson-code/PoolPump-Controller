#!/usr/bin/env python3
"""Passiv sniffer för RS-485/UART-trafiken mellan WiFi-modul och värmepump.

Lyssnar bara – skickar aldrig något på bussen. Delar upp strömmen i ramar på
tysta luckor, validerar Modbus RTU-CRC respektive Tuya-checksumma och skriver
ut avkodat resultat.

Exempel:
    # Gissa portparametrar automatiskt (kör med modulen inkopplad och strömsatt)
    python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --scan

    # Lyssna med kända parametrar och spara rådata
    python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --baud 9600 --log capture.bin
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

# Alla sätt en serieport kan vägra en viss baud/paritet-kombination.
PORT_ERRORS: tuple[type[BaseException], ...] = (
    serial.SerialException, OSError, ValueError)
try:
    import termios

    PORT_ERRORS += (termios.error,)
except ImportError:  # Windows har inget termios
    pass

# De inställningar som är vanliga på kinesiska poolvärmepumpar, i turordning.
SCAN_BAUDS = [9600, 4800, 19200, 38400, 115200, 2400, 57600]
SCAN_PARITIES = ["N", "E", "O"]


def char_time(baud: int, parity: str, stopbits: float) -> float:
    """Tid för ett tecken i sekunder (start + data + ev paritet + stopp)."""
    bits = 1 + 8 + (0 if parity == "N" else 1) + stopbits
    return bits / baud


def open_port(args: argparse.Namespace, baud: int, parity: str) -> "serial.Serial":
    gap = max(3.5 * char_time(baud, parity, args.stopbits), 0.002)
    return serial.Serial(
        port=args.port,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity={"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN,
                "O": serial.PARITY_ODD}[parity],
        stopbits=serial.STOPBITS_TWO if args.stopbits == 2 else serial.STOPBITS_ONE,
        timeout=0.2,
        inter_byte_timeout=gap,
    )


def read_frames(port: "serial.Serial", seconds: float):
    """Yield (tidsstämpel, ram). Ramgräns = tyst lucka på bussen."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        chunk = port.read(512)
        if chunk:
            yield time.monotonic(), chunk


def describe(frame: bytes) -> str:
    if protocol.modbus_crc_ok(frame):
        return "MODBUS  " + protocol.decode_modbus(frame)
    tuya = protocol.decode_tuya(frame)
    if tuya:
        return "TUYA    " + tuya
    # Ramgränsen kan ha hamnat fel – leta efter giltiga ramar inuti bufferten.
    parts = []
    for offset, length in protocol.find_modbus_frames(frame):
        parts.append(f"@{offset} " + protocol.decode_modbus(frame[offset:offset + length]))
    for offset, length in protocol.find_tuya_frames(frame):
        parts.append(f"@{offset} " + (protocol.decode_tuya(frame[offset:offset + length]) or ""))
    if parts:
        return "DELVIS  " + " | ".join(parts)
    return "OKÄND   (ingen giltig checksumma)"


def score(port: "serial.Serial", seconds: float) -> tuple[int, int]:
    """Räkna giltiga ramar och totala bytes under en kort mätning."""
    good = 0
    total = 0
    for _, frame in read_frames(port, seconds):
        total += len(frame)
        if protocol.modbus_crc_ok(frame) or protocol.decode_tuya(frame):
            good += 1
        else:
            good += len(protocol.find_modbus_frames(frame))
            good += len(protocol.find_tuya_frames(frame))
    return good, total


def do_scan(args: argparse.Namespace) -> int:
    print(f"Skannar portinställningar, {args.scan_seconds}s per kombination ...\n")
    results = []
    for baud in SCAN_BAUDS:
        for parity in SCAN_PARITIES:
            try:
                with open_port(args, baud, parity) as port:
                    port.reset_input_buffer()
                    good, total = score(port, args.scan_seconds)
            except PORT_ERRORS as exc:
                print(f"  {baud:>6} 8{parity}{int(args.stopbits)}  "
                      f"stöds inte av adaptern ({exc})")
                continue
            results.append((good, total, baud, parity))
            flag = "  <-- träff" if good else ""
            print(f"  {baud:>6} 8{parity}{int(args.stopbits)}  "
                  f"{total:>6} byte  {good:>4} giltiga ramar{flag}")

    print()
    if not results:
        print("Ingen av kombinationerna kunde öppnas. Fel port?")
        return 1
    results.sort(key=lambda r: (r[0], r[1]), reverse=True)
    best = results[0]
    if best[0] == 0 and best[1] == 0:
        print("Ingen trafik alls. Kontrollera A/B (prova att kasta om dem), GND "
              "och att värmepumpen och modulen är strömsatta.")
        return 1
    if best[0] == 0:
        print(f"Trafik hittad men ingen känd ram. Mest data på {best[2]} 8{best[3]} – "
              "kör utan --scan och titta på hexdumpen, protokollet kan vara "
              "proprietärt.")
        return 1
    print(f"Bäst: --baud {best[2]} --parity {best[3]}  ({best[0]} giltiga ramar)")
    return 0


def do_listen(args: argparse.Namespace) -> int:
    log = open(args.log, "ab") if args.log else None
    started = None
    seen: dict[bytes, int] = {}
    try:
        with open_port(args, args.baud, args.parity) as port:
            print(f"Lyssnar på {args.port} @ {args.baud} 8{args.parity}"
                  f"{int(args.stopbits)}. Ctrl-C för att avsluta.\n")
            port.reset_input_buffer()
            for ts, frame in read_frames(port, args.seconds):
                if log:
                    log.write(frame)
                    log.flush()
                started = started or ts
                seen[frame] = seen.get(frame, 0) + 1
                if args.unique and seen[frame] > 1:
                    continue
                print(f"[{ts - started:8.3f}] {len(frame):>3}B  {frame.hex(' ')}")
                print(f"           {describe(frame)}")
    except KeyboardInterrupt:
        print("\nAvbrutet.")
    except PORT_ERRORS as exc:
        print(f"\nSerieporten föll bort eller kunde inte öppnas: {exc}")
    finally:
        if log:
            log.close()
    if seen:
        print(f"\n{sum(seen.values())} ramar, {len(seen)} unika.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True, help="t.ex. /dev/ttyUSB0 eller COM3")
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--parity", choices=["N", "E", "O"], default="N")
    ap.add_argument("--stopbits", type=float, choices=[1, 2], default=1)
    ap.add_argument("--seconds", type=float, default=1e9, help="lyssningstid")
    ap.add_argument("--log", help="spara rådata till fil (append)")
    ap.add_argument("--unique", action="store_true",
                    help="skriv bara ut ramar som inte setts förut")
    ap.add_argument("--scan", action="store_true",
                    help="prova vanliga baud/paritet-kombinationer och gissa rätt")
    ap.add_argument("--scan-seconds", type=float, default=4.0)
    args = ap.parse_args()

    return do_scan(args) if args.scan else do_listen(args)


if __name__ == "__main__":
    raise SystemExit(main())
