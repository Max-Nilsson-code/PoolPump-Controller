[← Översikt](../README.md)

# 2. Hur kommunikationen ser ut

Det finns två arkitekturer i den här produktkategorin. Vilken du har avgör
helt vilket angreppssätt som fungerar.

## A. WiFi-modulen är Modbus-master på RS-485 (så fungerar din KMP Smart 60)

```
 AquaTemp-molnet  <--WiFi-->  [WiFi-modul]  <--RS-485-->  [Värmepumpens styrkort]
                               Modbus-MASTER               Modbus-SLAV, adress 1
```

PHNIX-kort har ofta **tre** separata bussar: panelbussen, WiFi-modulens port och
en dedikerad Modbus-slavport märkt `CN13`. Använd `CN13` om den finns — se
`docs/05-kmp-smart-60.md`.

Styrkortet är en helt vanlig **Modbus RTU-slav**. WiFi-modulen pollar den
någon gång per sekund och speglar värdena till molnet. Panelen på pumpen
hänger på samma buss eller på en egen.

Typiska portparametrar: **9600 baud, 8 databitar, ingen paritet, 1 stoppbit
(9600 8N1), slavadress 1.** Förekommer även 4800 och 19200.

Konsekvensen är den bästa tänkbara: **du behöver inte reverse-engineera något
protokoll.** Dra ur WiFi-modulen, koppla in en USB-RS485-adapter i samma
kontakt och bli master själv. Molnet behövs aldrig mer.

Det du får åt: vattentemperatur in/ut, utomhustemperatur, kompressorvarvtal
och -ström, expansionsventil, fläktvarvtal, alla larmkoder, samt skrivbara
börvärden och på/av.

## B. WiFi-modulen sitter i panelen och pratar Tuya MCU-protokoll

```
 Tuya-molnet  <--WiFi-->  [WBR3]  <--UART 3,3 V-->  [Panelens MCU]  <--RS-485-->  [Styrkort]
                                   Tuya MCU-protokoll                proprietärt
```

Här är WiFi-chippet inte alls på RS-485-bussen. Det pratar Tuyas eget
serieprotokoll (ramar som börjar `55 AA`, 9600 8N1) med panelens processor,
och det är panelen som sköter RS-485 mot pumpen med ett protokoll som ofta
inte är Modbus.

Känns igen på: modulen har bara 4 trådar men märkning `TX/RX/3V3/GND`, eller
sitter som en lödd modul inuti panelen. Din modul har `RS-485` tryckt utanpå
och en separat matningskabel, vilket talar emot detta.

Om det ändå visar sig vara variant B: byt ut WBR3:an mot en ESP8266/ESP32 med
ESPHome och `tuya:`-komponenten. Då talar ESP:en samma MCU-protokoll som
Tuya-chippet gjorde, och du slipper röra RS-485 helt.
[Referensprojekt för Poolex](https://github.com/andreondra/homeassistant-poolstar-poolex).

## Så skiljer du dem åt

`tools/rs485_sniff.py` avkodar båda. Kör den på bussen och läs vad den skriver:

- `MODBUS slav 1 REQ Read Input Registers ...` → variant A.
- `TUYA DP status ...` → variant B.
- Trafik men inget som checksummar → någon tillverkares egna protokoll. Spara
  dumpen med `--log` och jämför ramar mot knapptryck i panelen.
- Helt tyst → fel A/B-polaritet, ingen GND, eller ingen matning.
