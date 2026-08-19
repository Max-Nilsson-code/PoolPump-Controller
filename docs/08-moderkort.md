[← Översikt](../README.md)

# 8. Moderkortet och WiFi-modulen

Allt på den här sidan är avläst ur **KMP:s egen manual**, avsnitt 4.11 och
kapitel 7. Det ersätter de kvalificerade gissningar som stod i
`docs/01-hardware.md` innan manualen fanns.

## WiFi-modulen: `CN6`

Modulen på bilden är beskriven i manualens kapitel 7. Den tar emot data från
molnet och skickar till huvudenheten, och tvärtom — alltså exakt den
WiFi ↔ RS-485-brygga som resten av projektet utgår från.

**Kontakten `CN6`, sedd med pinnarna numrerade `4 3 2 1`:**

| Pinne | Signal |
|-------|--------|
| 4 | `GND` |
| 3 | `485B` |
| 2 | `485A` (tryckt `458A` i manualen — tryckfel) |
| 1 | `12V` |

**Tekniska data:**

| | |
|---|---|
| Matning | DC 8–12 V, 12 V rekommenderat |
| Strömförbrukning | 50 mA i viloläge, max 1 A i topp |
| Drifttemperatur | −30 °C till +70 °C |
| Mått | 78 × 63 × 24 mm |
| Montering | Magnet på baksidan, undvik direkt solljus |

**De fyra lysdioderna** (uppifrån, `LED1`–`LED4`):

| # | Betydelse | Fast sken | Långsam blinkning | Släckt |
|---|-----------|-----------|-------------------|--------|
| 1 | Nätverkskonfiguration | Konfigurerar nätverk | SmartLink-konfiguration | Klar |
| 2 | Routeranslutning | Normal | Onormal | — |
| 3 | Anslutning till molnserver | Normal | Onormal | — |
| 4 | **485-kommunikation** | Normal | Onormal | — |

Lysdiod 4 är den nyttigaste under felsökning: den visar om modulen faktiskt får
svar från moderkortet. Knappen (`SW2`) är konfigurationsknappen — kort tryck går
in i appens länkkonfigurationsläge.

## Moderkortet: var RS-485 sitter

På moderkortet för **KMP Smart 36/60** finns en egen **tvåpolig plint märkt
`RS485`**. Den motsvarar rad 23 i manualens gränssnittstabell:

| Nr | Skylt | Betydelse |
|----|-------|-----------|
| 23 | `R485(B)` + `R485(A)` | Trådstyrningens kommunikation |

Det är alltså **samma buss som den trådbundna manöverpanelen sitter på**, och
det är där WiFi-modulens `485A`/`485B` ska anslutas. Plinten har ingen matning —
modulens 12 V kommer från annat håll.

> **Korrigering:** jag skrev tidigare att `CN13` skulle vara en dedikerad
> Modbus-slavport. Det stämmer inte för det här kortet. Enligt manualen är
> `CN13(HEAT)` en **utgång för 4-vägsventilen, 220–230 V AC**. Koppla inte in
> någon RS-485-adapter där. Uppgiften om `CN13` kom från communityrapporter om
> andra PHNIX-kort och gäller inte KMP Smart 36/60.

## Hela gränssnittstabellen

| Nr | Skylt | Betydelse |
|----|-------|-----------|
| 01–03 | `P10-(U)` `P10-(V)` `P10-(W)` | Kompressor, utgång 220–230 V AC |
| 04 | `CN18(EMV)` | Vattenpump, utgång 220–230 V AC |
| 05 | `CN13(HEAT)` | 4-vägsventil, utgång 220–230 V AC |
| 06 | `CN96(H)` | Fläkt hög hastighet, utgång 220–230 V AC |
| 07 | `CN96(L)` | Fläkt låg hastighet, utgång 220–230 V AC |
| 08 | `P1(AC-L)` | Fas, ingång 220–230 V AC |
| 09 | `P2(AC-N)` | Nolla, ingång 220–230 V AC |
| 10 | `CN99(PL)` | Trycksensor |
| 11 | `CN29(OVT)` | Vattenflödesbrytare, ingång |
| 12 | `CN30(HP)` | Högtrycksvakt, ingång |
| 13 | `CN31(LP)` | Lågtrycksvakt, ingång |
| 14 | `CN7(OAT)` | Systemets sugtemperatur, ingång |
| 15 | `CN21(RES1)` | Ingående vattentemperatur, ingång |
| 16 | `CN22(RES2)` | Utgående vattentemperatur, ingång |
| 17 | `CN8(OPT)` | Fläktspolens temperatur, ingång |
| 18 | `CN12(PH)` | Omgivningstemperatur, ingång |
| 19 | `CN9(OHT)` | Systemets utloppstemperatur, ingång |
| 20–21 | `P00(GND)` `P01(GND)` | Jordkabel |
| 22 | `P13(L)` `P14(L)` | Elektrisk reaktor |
| **23** | **`R485(B)` `R485(A)`** | **Trådstyrningens kommunikation** |
| 24 | `CN15` | Elektronisk expansionsventil |

`CN15` och `C24` är sexpoliga kontakter märkta `12V 12V A B C D`. Trots
bokstäverna är det **inte** RS-485 utan expansionsventilens stegmotorlindningar.
Blanda inte ihop dem med `RS485`-plinten.

Givarnas placering är värd att notera när du sedan kartlägger register: `CN21`
inloppsvatten, `CN22` utloppsvatten, `CN12` omgivning, `CN8` fläktspole,
`CN7` suggas, `CN9` utlopp. Det är samma sex mätvärden som dyker upp som
`T01`–`T06` i parametertabellen.

## Vad manualen inte säger

Den dokumenterar varken baudrate, slavadress, protokoll eller register. Det
gissas inte här heller — kör `tools/rs485_sniff.py --scan` på `RS485`-plinten
och låt trafiken svara. Se [`docs/03-sniffa.md`](03-sniffa.md).

## Källa

KMP Smart 36/60/75/95 användarmanual: avsnitt 4.11 *Moderkort*, sidorna 22–24,
och kapitel 7 *WiFi-modul*, sidorna 32–34.
