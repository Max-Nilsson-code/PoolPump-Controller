# 1. Vad är det för modul?

## Kort svar

Bilden visar en **WiFi-modul (gateway) för poolvärmepump**, av den typ som
sitter monterad på pumpens utsida eller på baksidan av manöverpanelen. Den
tydliga `RS-485`-märkningen på höljet plus den 4-poliga kabeln är signaturen
för den överlägset vanligaste konstruktionen: modulen är en
**WiFi ↔ RS-485-brygga** som pratar **Modbus RTU** med värmepumpens styrkort
och Tuya-molnet ("Smart Life"/tillverkarens egna app) uppåt.

Modulerna säljs som generiska Tuya-moduler (t.ex. `HS01-485-WR3` med
RTL8710BN, eller en `WBR3`) och kläs i olika varumärken. Samma hårdvara sitter
i Fairland, IPS, Madimack, Duratech, Aquark, Poolex, Gullberg & Jansson m.fl. —
och de delar i praktiken samma registerkarta.

> Detta är en kvalificerad slutsats utifrån bilden, inte en verifierad
> identifiering. `docs/03-sniffa.md` visar hur du bevisar det på 15 minuter.

## Kontakten

Den 4-poliga kontakten (PH2.54 eller en M10-skruvkontakt beroende på modell)
går till en port märkt **`WIFI`**, `RS485` eller `485` på styrkortet:

| Pinne | Signal | Färg (vanligt, verifiera alltid) |
|-------|--------|----------------------------------|
| 1 | +12 V | röd |
| 2 | GND   | svart |
| 3 | A (D+ / non-inverting) | gul |
| 4 | B (D− / inverting)     | vit/blå |

Färgkoderna varierar mellan tillverkare. **Mät alltid** innan du kopplar in
något: 12 V mellan pinne 1 och 2 med pumpen strömsatt, och ~0,2 V viloskillnad
mellan A och B. Vissa moduler matas med 5 V i stället — kolla innan du matar
något från den.

Det spelar ingen roll om du kastar om A och B — inget går sönder, du får bara
ingen data. Prova tvärtom om det är tyst.

## Innan du öppnar något

- Bryt matningen till värmepumpen på säkringen, inte bara på panelen.
  Kompressorkretsen är 230/400 V och kondensatorerna håller laddning.
- RS-485-sidan är klenspänning, men den delar chassi med starkströmssidan.
  Använd en **galvaniskt isolerad** USB-RS485-adapter om du kan, annars minst
  en laptop på batteri under mätningen.
- Koppla in och ur bussen med strömmen bruten.
- Att koppla bort WiFi-modulen påverkar inte pumpens drift — panelen och
  termostaten fungerar precis som förut. Det är det ofarligaste första steget.
