# 4. Referens-registerkarta (Fairland-familjen)

Kartan nedan är sammanställd från publika projekt för Fairland/IPS-baserade
poolvärmepumpar och stämmer på ett stort antal ombrandade modeller. **Betrakta
den som en startgissning, inte som sanning för just din pump** — verifiera med
`--watch` enligt `docs/03-sniffa.md` innan du bygger något ovanpå.

Portparametrar: `9600 8N1`, slavadress `1`.

## Temperaturskalning ("typ 1")

```
grader = (registervärde − 60) / 2
```

`116` → `(116 − 60) / 2` = **28,0 °C**. Ett steg i registret är alltså 0,5 °C,
och börvärden ändras i steg om 2 (= 1,0 °C).

Undantag: register `input 6` (hetgas) och `input 12` (kylplatta) skalas bara
`/2`, utan offset.

## Coils (fn 1/5) — skrivbara

| Adress | Betydelse |
|--------|-----------|
| 0 | På/av |
| 1 | Manuell avfrostning |

## Discrete inputs (fn 2) — läsbara statusbitar

| Adress | Betydelse |
|--------|-----------|
| 0 | På/av-status |
| 1 | Avfrostar |
| 2 | DIN1 (ej ansluten) |
| 3 | DIN2 — extern start (potentialfri kontakt) |
| 4 | DIN3 — flödesvakt |
| 5 | DIN4 — lågtryckspressostat (inverterad: 0 = larm) |
| 6 | DIN5 — högtryckspressostat (inverterad: 0 = larm) |
| 7–15 | Utgång 1–9 (reläer: kompressor, fläkt, 4-vägsventil, pump …) |
| 16 | Fel / skyddsutlösning |
| 17 | Kompressor begär drift |
| 48–59 | Felkod E0–Eb |
| 61 | Felkod Ed |
| 64–74 | Parameterlarm P0–Pa |
| 80–91 | Frekvensomriktarlarm F0–Fb |

Vanliga felkoder: `E1` högtryck, `E2` lågtryck, `E3` inget vattenflöde,
`E4` fasföljd (3-fas), `E5` matningsspänning utanför område, `E6` lågt flöde,
`E7` utloppstemperatur utanför område.

## Input registers (fn 4) — mätvärden, skrivskyddade

| Adress | Betydelse | Skalning |
|--------|-----------|----------|
| 0 | Kompressorvarvtal | % |
| 1 | Kompressorns börfrekvens | Hz |
| 2 | PFC-spänning | V |
| 3 | **Vattentemperatur in** | typ 1 |
| 4 | **Vattentemperatur ut** | typ 1 |
| 5 | **Utomhustemperatur** | typ 1 |
| 6 | Hetgastemperatur | `/2` |
| 7 | Yttre batteri (förångare) | typ 1 |
| 8 | Sugtemperatur | typ 1 |
| 9 | Inre batteri (växlare) | typ 1 |
| 10 | Kompressorfrekvens | Hz |
| 11 | Kompressorström | `/10` A |
| 12 | Kylplattans temperatur | `/2` |
| 13 | Expansionsventilens öppning | `/10` % |
| 14 | Fläktvarvtal | rpm |

Effekt i watt fås som `register 11 / 10 × register 2` — grovt, men följer
verkligheten väl nog för energiuppföljning.

## Holding registers (fn 3/6) — inställningar, skrivbara

| Adress | Betydelse | Värden |
|--------|-----------|--------|
| 0 | Funktion | 0 = auto, 1 = värme, 2 = kyla |
| 1 | Driftläge | 0 = smart, 1 = tyst, 3 = turbo |
| 2 | Börvärde autoläge | typ 1, 84–140 |
| 3 | **Börvärde värmeläge** | typ 1, 84–140 (= 12–40 °C) |
| 4 | Börvärde kylläge | typ 1, 84–140 |
| 5 | Cirkulationspumpens läge (P0) | 0 = kontinuerlig, 1 = temperaturstyrd, 2 = tid+temperatur |
| 6 | Cirkulationspumpens gångtid (P1) | 10–120 min |
| 7 | Min kompressorgångtid | 30–90 min |
| 8 | Starttemperatur avfrostning (P3) | typ 1 |
| 9 | Max avfrostningstid (P4) | 1–12 min |
| 10 | Avslutstemperatur avfrostning (P5) | typ 1 |
| 17–18 | Överhettningsnivå expansionsventil | typ 1 |
| 25 | Beteende efter strömavbrott | 0 = av, 1 = återgå till tidigare läge |

**Rör inte register 7–18 utan att veta vad du gör.** Fel avfrostnings- eller
överhettningsparametrar kan slå ut kompressorn.

## Källor

- [Elwell/pool-heatpump](https://github.com/Elwell/pool-heatpump) — ESPHome för
  Madimack (ombrandad Fairland), mest kompletta kartan
- [spdr870/fairland_iphcr45_modbus](https://github.com/spdr870/fairland_iphcr45_modbus) —
  Fairland IPHCR45 via RS485-till-Ethernet
- [Home Assistant-tråden](https://community.home-assistant.io/t/controlling-a-fairland-pool-heatpump-eliminating-tuya/579467) —
  där registren ursprungligen kartlades
- [andreondra/homeassistant-poolstar-poolex](https://github.com/andreondra/homeassistant-poolstar-poolex) —
  variant B (Tuya MCU-protokoll i stället för Modbus)
