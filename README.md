# PoolPump-Controller

Verktyg och dokumentation för att ta reda på hur en poolvärmepumps
WiFi-modul pratar med pumpen — och för att sedan ta över kommunikationen
lokalt, utan moln.

## Slutsatsen först

Pumpen är en **KMP Smart 60** — en inverterstyrd poolvärmepump byggd av
**PHNIX**, med **Aqua Temp**-appen och molnet `cloud.linked-go.com` (alltså
inte Tuya). WiFi-modulen är en **WiFi ↔ RS-485-brygga** som är **Modbus
RTU-master** mot styrkortet.

Du behöver alltså inte knäcka något hemligt protokoll. På nyare PHNIX-kort
finns dessutom en **dedikerad Modbus-slavport märkt `CN13`** — koppla in dig
där och du kan prata lokalt med pumpen *samtidigt* som AquaTemp-appen fortsätter
fungera.

Börja i **[`docs/05-kmp-smart-60.md`](docs/05-kmp-smart-60.md)** — den gäller
just din pump. `tools/` gör själva jobbet.

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
| `docs/04-registerkarta.md` | Referenskarta för Fairland-familjen (jämförelse, gäller *inte* KMP) |
| `docs/05-kmp-smart-60.md` | **KMP Smart 60 / PHNIX: bussar, CN13, parametertabell, molnvägen** |
| `data/phnix_parameters.json` | Alla 150 PHNIX-parameterkoder maskinläsbart |
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

Verktygen är testade mot en emulerad Modbus-slav. Parameterkoderna för PHNIX
är hämtade från AquaTemp-molnets protokoll och är tillförlitliga — men
**registernumren är inte publika** och måste kartläggas mot din pump med
`--dump` och `--watch`. Registerkartan i `docs/04-registerkarta.md` tillhör en
annan tillverkarfamilj och finns med som jämförelse.
