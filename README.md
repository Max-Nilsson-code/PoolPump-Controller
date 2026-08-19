# PoolPump-Controller

Verktyg och dokumentation för att ta reda på hur en poolvärmepumps WiFi-modul
pratar med pumpen — och för att sedan ta över kommunikationen lokalt, utan moln.

## Slutsatsen först

Pumpen är en **KMP Smart 60** — en inverterstyrd poolvärmepump byggd av
**PHNIX**, med **Aqua Temp**-appen och molnet `cloud.linked-go.com` (alltså inte
Tuya). WiFi-modulen är en **WiFi ↔ RS-485-brygga** som är **Modbus RTU-master**
mot styrkortet.

Du behöver alltså inte knäcka något hemligt protokoll. På nyare PHNIX-kort finns
dessutom en **dedikerad Modbus-slavport märkt `CN13`** — koppla in dig där och du
kan prata lokalt med pumpen *samtidigt* som AquaTemp-appen fortsätter fungera.

---

## Snabblänkar

### Börja här

| | |
|---|---|
| 🎯 **[Din pump: KMP Smart 60](docs/05-kmp-smart-60.md)** | Vem som byggt den, vilka bussar som finns, `CN13`, molnvägen |
| 🔌 **[Steg-för-steg-guide](docs/03-sniffa.md)** | Från passiv sniffning till att skriva börvärden |
| 📋 **[Kommandon och parametrar](docs/06-kommandotabell.md)** | Alla 150 koder med svensk förklaring |
| 🚨 **[Felkoder](docs/07-felkoder.md)** | `E`, `P` och `F` med åtgärd |

### Alla dokument

**[1. Hårdvaran](docs/01-hardware.md)** — vad modulen är och hur du kopplar in dig
[Kort svar](docs/01-hardware.md#kort-svar) ·
[Kontakten och pinout](docs/01-hardware.md#kontakten) ·
[Innan du öppnar något](docs/01-hardware.md#innan-du-öppnar-något)

**[2. Protokollet](docs/02-protokoll.md)** — de två arkitekturerna
[A: Modbus-master på RS-485](docs/02-protokoll.md#a-wifi-modulen-är-modbus-master-på-rs-485-så-fungerar-din-kmp-smart-60) ·
[B: Tuya MCU-protokoll](docs/02-protokoll.md#b-wifi-modulen-sitter-i-panelen-och-pratar-tuya-mcu-protokoll) ·
[Så skiljer du dem åt](docs/02-protokoll.md#så-skiljer-du-dem-åt)

**[3. Sniffa och kartlägg](docs/03-sniffa.md)** — arbetsgången
[0. Läs av modulen](docs/03-sniffa.md#steg-0--läs-av-modulen) ·
[1. Lyssna passivt](docs/03-sniffa.md#steg-1--lyssna-passivt-ändrar-ingenting) ·
[2. Bli master själv](docs/03-sniffa.md#steg-2--bli-master-själv) ·
[3. Kartlägg registren](docs/03-sniffa.md#steg-3--kartlägg-registren-mot-verkligheten) ·
[4. Skriv försiktigt](docs/03-sniffa.md#steg-4--skriv-försiktigt) ·
[5. Permanent lösning](docs/03-sniffa.md#steg-5--permanent-lösning)

**[4. Registerkarta, Fairland](docs/04-registerkarta.md)** — jämförelse, gäller *inte* KMP
[Temperaturskalning](docs/04-registerkarta.md#temperaturskalning-typ-1) ·
[Coils](docs/04-registerkarta.md#coils-fn-15--skrivbara) ·
[Discrete inputs](docs/04-registerkarta.md#discrete-inputs-fn-2--läsbara-statusbitar) ·
[Input registers](docs/04-registerkarta.md#input-registers-fn-4--mätvärden-skrivskyddade) ·
[Holding registers](docs/04-registerkarta.md#holding-registers-fn-36--inställningar-skrivbara)

**[5. KMP Smart 60 / PHNIX](docs/05-kmp-smart-60.md)** — det som gäller din pump
[Vem har byggt den](docs/05-kmp-smart-60.md#vem-har-byggt-den) ·
[Två vägar: moln eller lokalt](docs/05-kmp-smart-60.md#två-vägar) ·
[Flera RS-485-bussar och `CN13`](docs/05-kmp-smart-60.md#viktigt-phnix-korten-har-flera-rs-485-bussar) ·
[Parametertabell](docs/05-kmp-smart-60.md#parametertabell) ·
[Skalning](docs/05-kmp-smart-60.md#skalning)

**[6. Kommando- och parametertabell](docs/06-kommandotabell.md)** — alla koder
[Styrkommandon](docs/06-kommandotabell.md#styrkommandon--det-du-skriver-till) ·
[`R` börvärden](docs/06-kommandotabell.md#börvärden-och-gränser--r) ·
[`P` cirkulationspump](docs/06-kommandotabell.md#cirkulationspump-och-filtrering--p) ·
[`T` mätvärden](docs/06-kommandotabell.md#givare-och-drift--t) ·
[`O` utgångar](docs/06-kommandotabell.md#utgångar-och-kompressor--o) ·
[`S` ingångar](docs/06-kommandotabell.md#ingångar-och-brytare--s) ·
[`H` systemparametrar](docs/06-kommandotabell.md#systemparametrar--h) ·
[`D` avfrostning](docs/06-kommandotabell.md#avfrostning--d) ·
[`E` expansionsventil](docs/06-kommandotabell.md#expansionsventil--e) ·
[`F` fläkt och frekvens](docs/06-kommandotabell.md#fläkt-och-frekvens--f) ·
[Modbus-funktionskoder](docs/06-kommandotabell.md#modbus-funktionskoder)

**[7. Felkoder](docs/07-felkoder.md)** — vad displayen försöker säga
[Koderna krockar med parameterkoderna](docs/07-felkoder.md#viktigt-koderna-krockar-med-parameterkoderna) ·
[`E` driftfel](docs/07-felkoder.md#e--driftfel) ·
[`P` givarfel](docs/07-felkoder.md#p--givarfel) ·
[`F` drivkortsfel](docs/07-felkoder.md#f--drivkort-och-frekvensomriktare) ·
[Hur felen syns över Modbus](docs/07-felkoder.md#hur-felen-syns-över-modbus) ·
[Via molnet i stället](docs/07-felkoder.md#via-molnet-i-stället)

### Kod och data

| Fil | Vad |
|-----|-----|
| [`tools/rs485_sniff.py`](tools/rs485_sniff.py) | Passiv sniffer. Gissar baud/paritet, avkodar Modbus RTU och Tuya MCU |
| [`tools/modbus_probe.py`](tools/modbus_probe.py) | Aktiv master: slavskanning, registerdump, ändringsbevakning |
| [`tools/protocol.py`](tools/protocol.py) | Ramavkodning, CRC och checksummor. Inga beroenden |
| [`data/phnix_parameters.json`](data/phnix_parameters.json) | Alla 150 parameterkoder maskinläsbart |
| [`data/error_codes.json`](data/error_codes.json) | Felkoderna maskinläsbart, med säkerhetsnivå per kod |
| [`esphome/poolpump-modbus.yaml`](esphome/poolpump-modbus.yaml) | ESPHome-config för permanent lokal Home Assistant-koppling |

---

## Kom igång

```bash
pip install -r requirements.txt

# 1. Lyssna passivt på bussen med originalmodulen inkopplad
python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --scan

# 2. Bli master själv (på CN13, eller med WiFi-modulen bortkopplad)
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --scan-slaves
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --dump

# 3. Kartlägg registren genom att trycka på knappar i panelen
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --watch
```

Du behöver en USB-till-RS485-adapter, helst galvaniskt isolerad.

## Säkerhet

Bryt strömmen på säkringen innan du öppnar värmepumpen. Kompressorkretsen är
starkström och kondensatorer håller laddning efter frånslag. Att bara koppla
loss WiFi-modulen påverkar inte pumpens drift — panel och termostat fungerar som
vanligt.

Skriv inte till serviceparametrarna (`D`, `E`, `F`, och `H` över ~`H05`) utan att
veta vad de gör. Fel värden för avfrostning, expansionsventil eller
frekvensgränser kan skada kompressorn.

## Status

Verktygen är testade mot en emulerad Modbus-slav — läsning, skrivning,
slavskanning, dump och watch fungerar.

Parameterkoderna kommer från AquaTemp-molnets protokolldefinition och är
tillförlitliga. Felkoderna är sammanställda ur flera svenska manualer för samma
OEM-styrkort; `E`- och `P`-serien är samstämmig, `F`-serien varierar mellan
modeller och är markerad därefter.

**Modbus-registernumren är inte publika** och måste kartläggas mot din egen pump
med `--dump` och `--watch`. Det är den enda biten som återstår.
