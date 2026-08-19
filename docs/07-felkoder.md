[← Översikt](../README.md)

# 7. Felkoder

Transkriberat ur **KMP:s egen manual**, avsnitt 4.10 *Parameterlista och
felkoder*. Det här är alltså inte längre en sammanställning från liknande
pumpar — det är din pumps faktiska tabell.
Maskinläsbart: `data/error_codes.json`.

## Viktigt: koderna krockar med parameterkoderna

Panelen använder samma bokstäver för två helt olika saker:

| Bokstav | Som **felkod** på displayen | Som **parameter** i servicemenyn |
|---------|------------------------------|-----------------------------------|
| `E` | Driftfel: tryck, flöde, frost | Expansionsventilens inställningar |
| `P` | Givarfel | Cirkulationspump och filtrering |
| `F` | Drivkorts- och fläktfel | Fläkt- och frekvensinställningar |

`P01` som felkod betyder givarfel på inloppsvattnet — `P01` som parameter
betyder pumpläge. Parametersidan finns i
[`docs/06-kommandotabell.md`](06-kommandotabell.md).

## `P` — givarfel

| Kod | Betydelse | Orsak | Åtgärd |
|-----|-----------|-------|--------|
| `P01` | Givarfel inloppsvatten | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P02` | Givarfel utloppsvatten | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P04` | Givarfel omgivning | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P05` | Givarfel rör | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P07` | Givarfel suggas | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P08` | Givarfel hetgas | Temperaturgivaren är trasig eller kortsluten | Kontrollera eller byt givaren |
| `P09` | Givarfel frostskyddsmedel | Frostskyddsmedlets temperaturgivare är trasig eller kortsluten | Kontrollera och ersätt givaren |
| `PP` | Trycksensorfel | Trycksensorn är bruten | Kontrollera eller byt trycksensorn |

Notera att det inte finns något `P03` eller `P06` i den här serien. Varje
givarfel motsvarar en `T`-parameter som slutat leverera vettiga värden:
`P01`→`T02`, `P02`→`T03`, `P04`→`T05`, `P05`→`T04`, `P07`→`T01`, `P08`→`T06`.
Det kan du bekräfta direkt över Modbus.

> Manualens PDF skriver koderna som `P081` och `E08` som `E081` — en
> fotnotssiffra som klistrats ihop med koden i textextraktionen. `E08` är
> **fältverifierad**: koden på displayen är faktiskt `E08`, kommunikationsfel.
> `P08` är rättad av samma skäl men inte lika bekräftad ännu.

## `E` — drift- och skyddsfel

| Kod | Betydelse | Orsak | Åtgärd |
|-----|-----------|-------|--------|
| `E01` | Högtrycksskydd | Högtrycksbrytaren är aktiv | Kontrollera tryckbrytaren och kylkretsen |
| `E02` | Lågtrycksskydd | Lågtryck 1-skydd | Kontrollera tryckbrytaren och kylkretsen |
| `E03` | Flödesvaktsskydd | Inget eller för lite vatten i vattensystemet | Kontrollera rör, vattenflöde och cirkulationspump |
| `E05` | Vattenskydd, antifrysskydd | Vatten- eller omgivningstemperaturen är för låg | — |
| `E06` | För stor differens inlopp/utlopp | Vattenflödet är inte tillräckligt och differenstrycket lågt | Kontrollera vattenflödet och om systemet är blockerat |
| `E07` | Frostskydd | Vattenflödet är inte tillräckligt | Kontrollera vattenflödet och om systemet är blockerat |
| `E19` | Primärt frostskydd | Omgivningstemperaturen är låg | — |
| `E29` | Sekundärt frostskydd | Omgivningstemperaturen är låg | — |
| `E08` | Kommunikationsfel hastighetskontrollenhet | Kommunikationen mellan hastighetskontrollenheten och moderkortet misslyckas | Kontrollera kommunikationsanslutningen |

`E03` och `E06` är de vanligaste och handlar båda om vattenflöde: stäng
bypassventilen mer så att mer vatten går genom värmepumpen.

## `TP` — omgivningstemperatur

| Kod | Betydelse | Orsak | Åtgärd |
|-----|-----------|-------|--------|
| `TP` | Lågt omgivningsskydd | Omgivningstemperaturen är för låg | — |

## `F03x` / `F05x` — fläktmotorer

| Kod | Betydelse | Orsak | Åtgärd |
|-----|-----------|-------|--------|
| `F031` | Fläktmotor 1 fel | Låst rotor, eller dålig kontakt mellan DC-fläktmodul och fläktmotor | Byt fläktmotor, eller kontrollera trådanslutningen |
| `F032` | Fläktmotor 2 fel | Låst rotor, eller dålig kontakt mellan DC-fläktmodul och fläktmotor | Byt fläktmotor, eller kontrollera trådanslutningen |
| `F051` | EC-fläktens återkoppling | Fel på fläktmotorn, fläktmotorn stannar | Kontrollera om fläktmotorn är trasig eller låst |

## `F` — frekvensomriktare och drivkort

| Kod | Betydelse | Orsak | Åtgärd |
|-----|-----------|-------|--------|
| `F01` | Drv1 MOP-larm | MOP-drivlarm | Återhämtar sig efter 150 s |
| `F02` | Frekvensomriktaren av | Kommunikationsfel mellan frekvensomriktare och moderkort | Kontrollera kommunikationsanslutningarna |
| `F03` | IPM-skydd | IPM-modulärt skydd | Återhämtar sig efter 150 s |
| `F04` | Kompressorns kretskort | Brist på fas, steg eller hårdvaruskada | Kontrollera mätspänningen i frekvensomvandlarens kretskort |
| `F05` | DC-fläktfel | Motorns strömåterkoppling är öppen krets eller kortsluten | Kontrollera att strömkablarna är anslutna i fläktmotorn |
| `F06` | IPM överström | IPM-inströmmen är stor | Kontrollera och justera strömmätningen |
| `F07` | Inverterare DC överspänning | DC-busspänningen över skyddsvärdet | Kontrollera den ingående spänningen |
| `F08` | Inverterare DC underspänning | DC-busspänningen under skyddsvärdet | Kontrollera den ingående spänningen |
| `F09` | Inverterare låg inspänning | Låg inspänning som ger hög inström | Kontrollera den ingående spänningen |
| `F10` | Inverterare ingångsöverspänning | Inspänningen är för hög | Kontrollera den ingående spänningen |
| `F11` | Inverterare provtagningsspänning | Provtagningsfel på inspänningen | Kontrollera och justera spänningen |
| `F12` | Kommunikationsfel DSP–PFC | Anslutningsfel mellan DSP och PFC | Kontrollera kommunikationsanslutningarna |
| `F15` | IPM överhettad | IPM-modulen är överhettad | Kontrollera och justera strömmatningen |
| `F16` | Svag magnetism, varning | Kompressorns magnetiska kraft är otillräcklig | — |
| `F17` | Inverterare matningsfas | Inspänningen har förlorat en fas | Kontrollera och mät spänningen |
| `F18` | IPM provtagningsström | IPM:s strömprovtagning är felaktig | Kontrollera och mät strömmen |
| `F19` | Inverterare temperaturgivare | Givaren är kortsluten eller öppen krets | Inspektera eller byt givaren |
| `F20` | Omvandlaren överhettad | Omvandlaren är överhettad | Kontrollera och justera strömmatningen |
| `F22` | Omvandlaren överhettad, varning | Omvandlarens temperatur är för hög | Kontrollera och justera strömmatningen |
| `F23` | Kompressorns överström, varning | Kompressorströmmen är för stor | Kompressorns överströmsskydd |
| `F24` | Inmatningsström, varning | Ingångsströmmen är för stor | Kontrollera och justera strömmatningen |
| `F25` | EEPROM-fel, varning | MCU-fel | Kontrollera om chippet är skadat, byt ut |
| `F26` | Inmatning överström | Utrustningsbelastningen är för stor | — |
| `F27` | PFC-fel | PFC-kretsskydd | Kontrollera om PFC-brytarens rör är kortslutet |
| `F28` | V15V över- eller underspänning | V15V är överbelastad eller underspänd | Kontrollera att V15V ligger inom 13,5–16,5 V |

Det här är effektelektronikens egna larm. `F01` och `F03` återställer sig
själva efter 150 sekunder. Resten är i praktiken servicefall.

## Skydd utan felkod

Manualen listar fyra skyddsfunktioner som löser ut utan att visa någon kod:

| Skydd | Orsak | Åtgärd |
|-------|-------|--------|
| Låg temperatur skydd | Omgivningstemperaturen är låg | — |
| Kompressorns strömskydd | Kompressorn är överbelastad | Kontrollera att kompressorsystemet fungerar normalt |
| Frånluft över temp-skydd | Kompressorn är överbelastad | Kontrollera att kompressorsystemet fungerar normalt |
| Kommunikationsfel | Kommunikationsfel mellan det trådbundna systemet och moderkortet | Kontrollera kabelanslutningen mellan kontrollenheten och moderkortet |

Den sista är värd att lägga på minnet: tappar den trådbundna panelen kontakten
med moderkortet får du **ingen kod** — bara en död display. Kontrollera
kablaget till `RS485`-plinten på moderkortet
([`docs/08-moderkort.md`](08-moderkort.md)).

## Hur felen syns över Modbus

På styrkort i den här familjen speglas varje felkod normalt som **en egen
statusbit** bland discrete inputs, inte som ett felnummer i ett register.
Bitadresserna är inte publika — kartlägg dem så här:

```bash
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 \
    --watch --watch-range discrete:0-128 --interval 1
```

Framkalla sedan ett ofarligt fel. Enklast är att stänga av poolpumpen så att
flödesvakten löser ut och `E03` visas i panelen. Biten som slår om samtidigt är
felkodens adress.

Det finns oftast också en samlad "fel aktivt"-bit som går hög vid vilket fel som
helst. Den räcker för en larmnotis i Home Assistant.

## Via molnet i stället

AquaTemp-molnet returnerar felet som färdig textbeskrivning via
`getFaultDataByDeviceCode`, så
[HA-integrationen](https://github.com/radical-squared/aquatemp) ger `is_fault`
plus en läsbar felsträng utan att du kartlägger en enda bit.

## Källa

KMP Smart 36/60/75/95 användarmanual, avsnitt 4.10, sidorna 19–20.
