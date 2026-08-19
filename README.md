# PoolPump-Controller

Verktyg och dokumentation för att ta reda på hur en poolvärmepumps
WiFi-modul pratar med pumpen — och för att sedan ta över kommunikationen
lokalt, utan moln.

## Slutsatsen först

Modulen på bilden är med stor sannolikhet en **Tuya-baserad WiFi ↔ RS-485-brygga**.
Den är **Modbus RTU-master** på en RS-485-buss där **värmepumpens styrkort är
slav på adress 1**, typiskt i **9600 8N1**. Uppåt speglar den värdena till
Tuya-molnet (Smart Life eller tillverkarens egen app).

Det betyder att du inte behöver knäcka något hemligt protokoll. Du kan koppla
bort modulen, sätta dit en RS-485-adapter och prata direkt med pumpen med
standard-Modbus. `docs/` visar hur, `tools/` gör jobbet.

## Kom igång

```bash
pip install -r requirements.txt

# 1. Lyssna passivt på bussen med originalmodulen inkopplad
python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --scan

# 2. Koppla bort modulen, bli master själv
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --scan-slaves
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --dump

# 3. Kartlägg registren genom att trycka på knappar i panelen
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --watch
```

Du behöver en USB-till-RS485-adapter, helst galvaniskt isolerad.

## Innehåll

| Fil | Vad |
|-----|-----|
| `docs/01-hardware.md` | Vad modulen är, kontaktens pinout, säkerhet |
| `docs/02-protokoll.md` | De två arkitekturerna och hur du skiljer dem åt |
| `docs/03-sniffa.md` | Steg-för-steg-guide, från passiv lyssning till skrivning |
| `docs/04-registerkarta.md` | Referenskarta för Fairland-familjen med skalningar |
| `tools/rs485_sniff.py` | Passiv sniffer, avkodar Modbus RTU och Tuya MCU, gissar baud |
| `tools/modbus_probe.py` | Aktiv master: slavskanning, registerdump, ändringsbevakning |
| `tools/protocol.py` | Ramavkodning, CRC, checksummor (inga beroenden) |
| `esphome/` | Färdig ESPHome-config för permanent, lokal Home Assistant-koppling |

## Säkerhet

Bryt strömmen på säkringen innan du öppnar värmepumpen. Kompressorkretsen är
starkström och kondensatorer håller laddning efter frånslag. Att bara koppla
loss WiFi-modulen påverkar inte pumpens drift — panel och termostat fungerar
som vanligt.

Skrivning till holding-register 7 och uppåt ändrar fabriksparametrar för
avfrostning och expansionsventil. Fel värden där kan skada kompressorn.

## Status

Verktygen är testade mot en emulerad Modbus-slav. Registerkartan kommer från
publika projekt för Fairland-baserade pumpar (se källorna i
`docs/04-registerkarta.md`) och ska verifieras mot din egen pump innan du
litar på den.
