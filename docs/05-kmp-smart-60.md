# 5. KMP Smart 60 — vad som faktiskt gäller

Uppdaterat efter att modellen bekräftats. **Det här dokumentet gäller din pump;
`docs/04-registerkarta.md` gäller en annan tillverkarfamilj och ska bara läsas
som jämförelse.**

## Vem har byggt den

KMP Smart 60 är en inverterstyrd poolvärmepump med R32 och inbyggd WiFi-modul
som styrs via appen **Aqua Temp**. Det placerar den i **PHNIX**-familjen
(Guangdong PHNIX Eco-energy Solution), som är OEM åt en lång rad europeiska
varumärken: Thermotec, EvoHeat, Gullberg & Jansson, heatpumps4pools m.fl. Samma
styrkort, samma parametertabell, samma moln.

Molnet är `cloud.linked-go.com:449` — **inte Tuya**. Det är en viktig skillnad
mot vad jag antog av bilden allena: modulen är en AquaTemp-modul, inte en
Tuya-modul. Konsekvensen för dig är liten, för arkitekturen är densamma
(WiFi-modulen är Modbus-master mot styrkortet), men allt som handlar om
Tuya-appar, `tuya-convert` eller Tuya lokala nycklar är irrelevant här.

## Två vägar

### Väg 1: molnet, noll hårdvara

Det finns en färdig Home Assistant-integration mot AquaTemp-molnet:
[radical-squared/aquatemp](https://github.com/radical-squared/aquatemp) (HACS).
Den ger klimatentitet, alla sensorer i tabellerna nedan, och kräver bara ditt
AquaTemp-konto.

Nackdelar: beroende av molnet och din internetuppkoppling, och AquaTemp tillåter
bara en inloggning i taget — skapa ett andra konto och dela pumpen till det om
du vill använda appen parallellt.

Det här är rimligen värt att sätta upp först, som referens. När du sedan
kartlägger Modbus lokalt kan du jämföra dina registervärden mot appens
namngivna parametrar och veta exakt vad du tittar på.

### Väg 2: lokal Modbus över RS-485

Det du egentligen vill ha. Se `docs/03-sniffa.md` för arbetsgången.

## Viktigt: PHNIX-korten har flera RS-485-bussar

Det här är den stora fällan, och skiljer sig från vad `docs/02-protokoll.md`
beskriver generellt:

| Buss | Vad den är | Använd? |
|------|------------|---------|
| Panelbussen | Internkommunikation mellan styrkort och manöverpanel | Nej — proprietär, och du stör panelen |
| WiFi-modulens port | Där modulen på bilden sitter | Går, men konkurrerar med modulen |
| **`CN13`** | Dedikerad Modbus-slavport på nyare PHNIX-kort | **Ja** |

Leta efter en kontakt märkt **`CN13`** på styrkortet. Den är avsedd för precis
det du vill göra och stör varken panel eller WiFi-modul — du kan alltså behålla
AquaTemp-appen samtidigt. Finns ingen CN13 får du använda WiFi-modulens port och
koppla loss modulen.

Parametern **`H37` (Unit Address)** i servicemenyn är pumpens Modbus-slavadress.
Läs av den i panelen så slipper du gissa — annars hittar `--scan-slaves` den.

## Parametertabell

Koderna nedan är PHNIX egna och visas både i manöverpanelens servicemeny och i
AquaTemp-appen. **Registernumren är inte publika** — men koderna är
betydelsekartan. Arbetsgången blir: dumpa registren, ändra en sak i panelen, se
vilket register som rör sig, och sätt rätt kod på det.

Maskinläsbar version med alla 150 parametrar: `data/phnix_parameters.json`.

### Mätvärden — `T`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `T01` | Suction Temp. | °C |
| `T02` | Inlet water Temp. | °C |
| `T03` | Outlet water Temp. | °C |
| `T04` | Coil 1 Temp. | °C |
| `T05` | Ambient Temp. | °C |
| `T06` | Exhaust Temp. | °C |
| `T07` | Compressor current Detect | A |
| `T08` | AC Fan Output | % |
| `T09` | Flow Rate Input | Hz |
| `T10` | Pressure Sensor | bar |
| `T11` | Super heat | °C |
| `T12` | Target speed of fan motor | r |
| `T13` | Over heat after commpen. | °C |
| `T14` | Inverter plate AC voltage | V |
| `T15` | Antifreeze Temp. | °C |
| `T16` | EC Fan motor Speed | r |
| `T17` | Speed of fan motor1 | r |
| `T18` | Speed of fan motor2 | r |
| `T19` | Buses voltage | V |
| `T20` | Limited Frequency Protect State |  |
| `T21` | Frequency Reduction Protect State |  |
| `T22` | Coil 2 Temp. | °C |
| `T23` | driver board running state 1 |  |
| `T24` | driver board running state 2 |  |
| `T25` | driver board running state 3 |  |
| `T26` | driver board running state 4 |  |
| `T27` | driver board running state 5 |  |
| `T28` | Target frequency |  |

### Börvärden och gränser — `R`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `R01` | Cooling set | °C |
| `R02` | Heating set | °C |
| `R03` | Auto. Set | °C |
| `R04` | Temp Difference | °C |
| `R05` | Power Off Temp Difference | °C |
| `R08` | Min. cool | °C |
| `R09` | Max. cool | °C |
| `R10` | Min. heat | °C |
| `R11` | Max. heat | °C |
| `R12` | Power on Difference | °C |

### Ingångar — `S`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `S01` | HP switch |  |
| `S02` | LP switch |  |
| `S03` | Flow switch |  |
| `S04` | Remote switch |  |
| `S05` | Mode switch |  |
| `S06` | Master/Slave switch |  |

Utöver dessa finns `D` (avfrostning), `E` (expansionsventil), `F` (fläkt och
frekvens), `H` (systemparametrar), `O` (utgångar) och `P` (skydd). De ligger i
JSON-filen. Rör dem inte förrän allt annat är kartlagt — `D`-, `E`- och
`F`-parametrarna styr kompressorskydd.

### De fyra styrbara

| Kod | Betydelse |
|-----|-----------|
| `Power` | På/av |
| `Mode` | 0 = kyla, 1 = värme, 2 = auto |
| `Set_Temp` | Aktivt börvärde |
| `Manual-mute` | 0 = auto fläkt, 1 = tyst läge |

Börvärdet ligger i `R01` (kyla), `R02` (värme) eller `R03` (auto) beroende på
läge, med gränserna `R08`–`R11`.

## Skalning

PHNIX skalar oftast temperaturer som **`värde / 10`** med tecken, till skillnad
från Fairland-familjens `(värde − 60) / 2`. Gissa inte — `--dump` visar båda
kolumnerna, och den som matchar panelens avlästa inloppstemperatur är den rätta.

## Källor

- [radical-squared/aquatemp](https://github.com/radical-squared/aquatemp) —
  HA-integration mot AquaTemp-molnet; parametertabellen ovan är hämtad därifrån
- [KMP Smart 60 produktsida](https://www.kmp.se/kmp-smart-60/)
- Communityrapporter om `CN13` som dedikerad Modbus-slavport på PHNIX-kort
