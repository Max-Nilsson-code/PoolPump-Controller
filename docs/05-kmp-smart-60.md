[← Översikt](../README.md)

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

## Var RS-485 sitter

Moderkortet för KMP Smart 36/60 har **en** RS-485-buss: den tvåpoliga plinten
märkt `RS485`, alltså `R485(A)` och `R485(B)`, som manualen kallar
trådstyrningens kommunikation. Där hänger både den trådbundna panelen och
WiFi-modulen.

> **Korrigering.** Innan manualen fanns skrev jag att nyare PHNIX-kort har en
> dedikerad Modbus-slavport `CN13`. Det gäller inte det här kortet: `CN13(HEAT)`
> är en 230 V-utgång för 4-vägsventilen. Fullständig gränssnittstabell i
> [`docs/08-moderkort.md`](08-moderkort.md).

Parametern **`H37` (Unit Address)** i servicemenyn är pumpens slavadress. Läs av
den i panelen så slipper du gissa — annars hittar `--scan-slaves` den.

## Parametertabell

Koderna nedan är PHNIX egna och visas både i manöverpanelens servicemeny och i
AquaTemp-appen. **Registernumren är inte publika** — men koderna är
betydelsekartan. Arbetsgången blir: dumpa registren, ändra en sak i panelen, se
vilket register som rör sig, och sätt rätt kod på det.

Hela tabellen med alla 150 koder — mätvärden, börvärden, ingångar, utgångar
och serviceparametrar — finns i **[`docs/06-kommandotabell.md`](06-kommandotabell.md)**,
och maskinläsbart i `data/phnix_parameters.json`.

De grupper som finns: `T` mätvärden, `R` börvärden, `S` ingångar, `O` utgångar,
`P` cirkulationspump, `D` avfrostning, `E` expansionsventil, `F` fläkt och
frekvens, `H` systemparametrar.

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
- KMP Smart 36/60/75/95 användarmanual, avsnitt 4.11 och kapitel 7
