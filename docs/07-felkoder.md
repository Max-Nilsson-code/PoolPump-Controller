[← Översikt](../README.md)

# 7. Felkoder

Koderna nedan gäller poolvärmepumpar med samma OEM-styrkort som KMP Smart 60,
sammanställda ur flera svenska installations- och bruksanvisningar för
inverterstyrda poolvärmepumpar i PHNIX-familjen.

> **⚠️ markerar lägre säkerhet.** `E`- och `P`-serien är samstämmig mellan
> källorna och kan litas på. `F`-serien kommer från frekvensomriktarens drivkort
> och varierar mest mellan modeller — KMP:s egen manual listar `F01`–`F27`.
> Slå upp den koden du faktiskt får innan du skruvar.
> Maskinläsbart: `data/error_codes.json`.

## Viktigt: koderna krockar med parameterkoderna

Det här förvirrar lätt. Panelen använder samma bokstäver för två helt olika
saker:

| Bokstav | Som **felkod** på displayen | Som **parameter** i servicemenyn |
|---------|------------------------------|-----------------------------------|
| `E` | Driftfel (tryck, flöde, kommunikation) | Expansionsventilens inställningar |
| `P` | Givarfel | Cirkulationspump och filtrering |
| `F` | Drivkortsfel | Fläkt- och frekvensinställningar |

`P01` som felkod betyder alltså givarfel på inloppsvattnet — `P01` som parameter
betyder pumpläge. Se `docs/06-kommandotabell.md` för parametersidan.

## `E` — driftfel

| Kod | Betydelse | Vad du gör |
|-----|-----------|------------|
| `E01` | Högt systemtryck | Högtrycksvakt löst ut. Kontrollera vattenflöde, luftflöde över förångaren och köldmediemängd. |
| `E02` | Lågt systemtryck | Lågtrycksvakt löst ut. Köldmediebrist, igensatt förångare eller för låg utetemperatur. |
| `E03` | Flödesskydd | Inget eller för lite vatten i systemet. Kontrollera cirkulationspump, filter och bypassventil. |
| `E04` ⚠️ | Okänd i mina källor | Förekommer i serien men betydelsen bekräftades inte. Slå upp i KMP:s manual. På trefasenheter är E04 ofta fasföljdsfel. |
| `E05` | Frostskydd vattensystem | Vatten- eller omgivningstemperaturen är för låg. |
| `E06` | För stor temperaturdifferens in/ut | Vattenflödet är för lågt. Öppna bypassventilen mindre så mer vatten går genom pumpen. |
| `E07` | Frysskydd i kylläge | Utloppsvattnets temperatur är för låg. |
| `E08` | Kommunikationsfel | Ingen kommunikation mellan styrkort och display. Kontrollera panelbussens kablage. |

`E03` och `E06` är de i särklass vanligaste, och båda handlar om vattenflöde.
Stäng bypassventilen mer så att mer vatten går genom värmepumpen.

## `P` — givarfel

| Kod | Betydelse | Vad du gör |
|-----|-----------|------------|
| `P01` | Givarfel inloppsvatten | Givaren är bruten eller kortsluten. Motsvarar T02. |
| `P02` | Givarfel utloppsvatten | Givaren är bruten eller kortsluten. Motsvarar T03. |
| `P03` | Givarfel värmeväxlare | Inre batteriets givare bruten eller kortsluten. |
| `P04` | Givarfel omgivning | Utomhusgivaren bruten eller kortsluten. Motsvarar T05. |
| `P05` | Givarfel förångare | Yttre batteriets givare ej ansluten, kabelbrott eller kortslutning. Motsvarar T04. |
| `P07` | Givarfel suggas | Sugtemperaturgivaren ej ansluten, kabelbrott eller kortslutning. Motsvarar T01. |

Kolumnen "motsvarar" i detaljerna pekar ut vilken `T`-parameter givaren
rapporterar till. Ser du `P02` är det alltså `T03` som slutat leverera vettiga
värden — vilket du kan bekräfta direkt över Modbus.

## `F` — drivkort och frekvensomriktare

| Kod | Betydelse | Vad du gör |
|-----|-----------|------------|
| `F01` ⚠️ | MOP-drivlarm | Återställs automatiskt efter cirka 150 sekunder. |
| `F02` ⚠️ | Frekvensomriktaren offline | Kommunikationsfel mellan frekvensomriktare och moderkort. Kontrollera kablaget mellan korten. |
| `F03` ⚠️ | IPM-modulskydd | Skydd i effektmodulen, ofta fasbortfall mot kompressorn. |
| `F04` ⚠️ | Fel på motorströmsåterkoppling | Avbrott eller kortslutning i strömmätningen. |
| `F05` ⚠️ | Hög IPM-ingångsström eller överspänning | DC-mellanledets spänning över skyddsnivån. |

KMP:s manual listar `F01`–`F27`. De högre koderna är i stort sett alltid
kompressor- och effektelektronikskydd, och de är inget du åtgärdar själv.

## Hur felen syns över Modbus

På styrkort i den här familjen speglas varje felkod som **en egen statusbit**
bland discrete inputs — inte som ett felnummer i ett register. Fairland-kortet
lägger till exempel `E0`–`Eb` på bitadress 48–59 och `P0`–`Pa` på 64–74
(`docs/04-registerkarta.md`). PHNIX gör något liknande, men bitadresserna är
inte publika.

Kartlägg dem så här:

```bash
# Bevaka hela statusområdet
python3 tools/modbus_probe.py --port /dev/ttyUSB0 --unit 1 \
    --watch --watch-range discrete:0-128 --interval 1
```

Framkalla sedan ett ofarligt fel — enklast är att stänga av poolpumpen så att
flödesvakten löser ut och `E03` visas i panelen. Biten som slår om samtidigt är
felkodens adress. Upprepa för de fel du kan framkalla riskfritt.

Det finns oftast också en samlad "fel/skydd aktivt"-bit som går hög vid vilket
fel som helst. Den är den enda du egentligen behöver för en larmnotis i Home
Assistant.

## Via molnet i stället

AquaTemp-molnet returnerar felet som en färdig textbeskrivning via
`getFaultDataByDeviceCode`, så
[HA-integrationen](https://github.com/radical-squared/aquatemp) ger dig
`is_fault` plus en läsbar felsträng utan att du behöver kartlägga en enda bit.
Bra som komplement medan du arbetar dig igenom Modbus-sidan.

## Källor

Svenska bruksanvisningar för inverterstyrda poolvärmepumpar med samma
OEM-styrkort:
[KMP inverter-manual](https://www.kmp.se/wp-content/uploads/2018/01/Inverter-user-manual_-sv.pdf) ·
[Poolstore](https://poolstore.se/wp-content/uploads/2022/09/Pool-Store-inverter-Poolvarmepump-Manual.pdf) ·
[InverPilot](https://www.pool-fritid.se/wp-content/uploads/2026/03/InverPilot-Manual.pdf) ·
[Flotde](https://www.vvsbutiken.nu/dokument/Flotde%20Varmepump%20Inverter%20ABS%2050%20mm%20Manual.pdf) ·
[Gullberg & Jansson Q-serien](https://www.gullbergjansson.se/fileadmin/user_upload/Dokument/manualer/Q-serien/Q-serien_SV_ver4.pdf)

KMP:s egen manual är den som gäller för din pump — den listar hela `F`-serien.
