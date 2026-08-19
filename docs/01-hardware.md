[← Översikt](../README.md)

# 1. Vad är det för modul?

Bekräftat mot KMP:s egen manual. Detaljerad pinout och moderkortets fullständiga
gränssnittstabell finns i [`docs/08-moderkort.md`](08-moderkort.md).

## Kort svar

Modulen på bilden är **KMP:s WiFi-modul**, dokumenterad i manualens kapitel 7.
Den är en **WiFi ↔ RS-485-brygga**: tar emot data från molnet och skickar till
huvudenheten, och tvärtom. Uppåt pratar den med **AquaTemp**-molnet
(`cloud.linked-go.com`), nedåt sitter den på moderkortets RS-485-buss.

De fyra lysdioderna är nätverkskonfiguration, routeranslutning,
molnserveranslutning och **485-kommunikation** — det är de ikonerna du ser
tryckta på höljet. Den runda knappen är konfigurationsknappen.

Matning: **DC 8–12 V**, 50 mA i viloläge, max 1 A i topp. Mått 78 × 63 × 24 mm,
magnet på baksidan.

## Kontakten

Modulens kontakt heter `CN6` och har fyra poler:

| Pinne | Signal |
|-------|--------|
| 4 | `GND` |
| 3 | `485B` |
| 2 | `485A` |
| 1 | `12V` |

På moderkortet (KMP Smart 36/60) sitter motsvarande buss på en **tvåpolig plint
märkt `RS485`** — `R485(A)` och `R485(B)`, i manualen beskriven som
trådstyrningens kommunikation. Det är alltså samma buss som manöverpanelen
delar. Plinten har ingen matning; modulens 12 V kommer från annat håll.

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
- Rör inte `CN13(HEAT)`, `CN18(EMV)` eller `CN96` — det är 230 V-utgångar.
