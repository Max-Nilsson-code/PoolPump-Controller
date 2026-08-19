# 3. Steg för steg: ta reda på vad din pump pratar

Räkna med en kväll. Du behöver en **USB-till-RS485-adapter** (~100 kr; helst
en isolerad med ADM2483/MAX13487, annars duger CH340+MAX485) och lite
kopplingstråd.

```bash
pip install -r requirements.txt
```

## Steg 0 — läs av modulen

Bryt strömmen, ta loss modulen (de flesta sitter på en skena eller med
dubbelhäftande tejp) och fotografera baksidan. En märkning som `HS01-485-WR3`,
`WBR3`, `TYWE3S` eller en FCC-ID pekar direkt ut vilken chippfamilj det är, och
avgör variant A eller B i `docs/02-protokoll.md`.

## Steg 1 — lyssna passivt (ändrar ingenting)

> På din KMP Smart 60 (PHNIX): leta först efter en kontakt märkt **`CN13`** på
> styrkortet. Det är en dedikerad Modbus-slavport — sitter du där kan du hoppa
> direkt till steg 2 och behålla WiFi-modulen inkopplad. Se
> `docs/05-kmp-smart-60.md`.

Låt WiFi-modulen sitta kvar och koppla in adaptern **parallellt** på samma
buss:

```
Adapter A   ->  A (gul)
Adapter B   ->  B (vit/blå)
Adapter GND ->  GND (svart)
```

Rör inte 12 V-ledaren. Adaptern matas från USB.

```bash
python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --scan
```

`--scan` provar 9600/4800/19200/38400/115200/2400/57600 med N/E/O-paritet och
rapporterar vilken kombination som ger ramar med giltig checksumma. Kör sedan
med de parametrarna och spara rådata:

```bash
python3 tools/rs485_sniff.py --port /dev/ttyUSB0 --baud 9600 --log capture.bin
```

Du bör se ett upprepande mönster av request/response. Notera slavadressen och
vilka funktionskoder och adressintervall modulen pollar — det är exakt de
register tillverkaren själv anser vara intressanta.

Är det tyst: kasta om A och B och prova igen. Fortfarande tyst: kontrollera
att GND är kopplad och att pumpen är strömsatt.

## Steg 2 — bli master själv

Bryt strömmen. Sitter du på `CN13` behöver du inte röra WiFi-modulen alls.
Annars: **koppla loss WiFi-modulen** och sätt adaptern i dess ställe (A, B och
GND — 12 V behövs inte). Slå på strömmen igen.

Slavadressen står i panelens servicemeny som parameter `H37`, men
`--scan-slaves` hittar den också.

```bash
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --scan-slaves
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --dump
```

`--dump` läser discrete inputs, coils, input- och holding-register, hoppar
över adresser som ger `illegal data address`, och visar varje registervärde
både rått och tolkat som temperatur enligt `(rått − 60) / 2`.

## Steg 3 — kartlägg registren mot verkligheten

Det här är själva reverse-engineeringen, och den är enkel: polla kontinuerligt
och gör saker i panelen.

```bash
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --watch
```

Varje ändring skrivs ut med tidsstämpel. Höj börvärdet ett steg — ett holding-
register hoppar två enheter (därav `/2`-skalningen). Byt läge, stäng av, tvinga
avfrostning. Efter tio minuter har du din egen registerkarta, verifierad mot
din specifika modell. Jämför med referenskartan i `docs/04-registerkarta.md`.

## Steg 4 — skriv (försiktigt)

```bash
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --write-coil 0 1 --yes
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 --write-reg 3 116 --yes
```

`--yes` krävs för alla skrivningar. Börja med `coil 0` (på/av) — den är
ofarlig och lätt att verifiera. Skriv **inte** blint till holding-register över
25; där ligger fabriksparametrar för avfrostning och expansionsventil som kan
skada kompressorn om de sätts fel.

## Steg 5 — permanent lösning

När kartan stämmer: ersätt USB-adaptern med en ESP32 med RS485-transceiver
(t.ex. LilyGO T-CAN485, som passar i originalmodulens läge och matas från
samma 12 V) och kör ESPHome-configen i `esphome/`. Då pratar värmepumpen
direkt med Home Assistant, lokalt, utan moln.
