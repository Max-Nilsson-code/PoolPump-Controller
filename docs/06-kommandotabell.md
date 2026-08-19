# 6. Kommando- och parametertabell (PHNIX / AquaTemp)

Fullständig lista över de kommandon och parametrar KMP Smart 60:s styrkort
exponerar. Koderna är PHNIX egna och används både i AquaTemp-molnets protokoll
och i manöverpanelens servicemeny.

> **Vad som är känt och inte.** Koderna och deras betydelse är verifierade —
> de kommer från AquaTemp-integrationens protokolldefinition. **Modbus-
> registernumren är däremot inte publika.** Kartlägg dem med
> `tools/modbus_probe.py --watch` och sätt rätt kod på rätt adress.
> `data/phnix_parameters.json` innehåller hela listan maskinläsbart.

## Styrkommandon — det du skriver till

De fyra som räcker för normal styrning:

| Kommando | Betydelse | Värden |
|----------|-----------|--------|
| `Power` | På/av | 0 = av, 1 = på |
| `Mode` | Driftläge | 0 = kyla, 1 = värme, 2 = auto |
| `Set_Temp` | Aktivt börvärde | speglar `R01`/`R02`/`R03` beroende på läge |
| `Manual-mute` | Fläktläge | 0 = auto, 1 = tyst |

### Börvärden och gränser — `R`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `R01` | Börvärde kyla *(Cooling set)* | °C |
| `R02` | Börvärde värme *(Heating set)* | °C |
| `R03` | Börvärde auto *(Auto. Set)* | °C |
| `R04` | Hysteres *(Temp Difference)* | °C |
| `R05` | Hysteres avstängning *(Power Off Temp Difference)* | °C |
| `R08` | Min börvärde kyla *(Min. cool)* | °C |
| `R09` | Max börvärde kyla *(Max. cool)* | °C |
| `R10` | Min börvärde värme *(Min. heat)* | °C |
| `R11` | Max börvärde värme *(Max. heat)* | °C |
| `R12` | Hysteres inkoppling *(Power on Difference)* | °C |

Vilket börvärde som gäller styrs av `Mode`: kyla → `R01` (gränser `R08`–`R09`),
värme → `R02` (gränser `R10`–`R11`), auto → `R03`.

### Cirkulationspump och filtrering — `P`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `P01` | Pumpläge *(Mode)* | — |
| `P02` | Intervall *(Interval)* | min |
| `P03` | Gångtid *(Duration)* | min |
| `P04` | Förtid *(Advance)* | min |
| `P05` | Filtrering på/av *(Water pump filtration)* | — |
| `P06` | Filtrering start 1 *(Water Pump Filtration start Time1)* | h |
| `P07` | Filtrering stopp 1 *(Water Pump Filtration End Time1)* | h |
| `P08` | Filtrering start 2 *(Water Pump Filtration start Time2)* | h |
| `P09` | Filtrering stopp 2 *(Water Pump Filtration End Time 2)* | h |

## Mätvärden — det du läser

### Givare och drift — `T`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `T01` | Sugtemperatur *(Suction Temp.)* | °C |
| `T02` | Vattentemperatur in *(Inlet water Temp.)* | °C |
| `T03` | Vattentemperatur ut *(Outlet water Temp.)* | °C |
| `T04` | Batteritemperatur 1 (förångare) *(Coil 1 Temp.)* | °C |
| `T05` | Utomhustemperatur *(Ambient Temp.)* | °C |
| `T06` | Hetgastemperatur *(Exhaust Temp.)* | °C |
| `T07` | Kompressorström *(Compressor current Detect)* | A |
| `T08` | AC-fläktens utstyrning *(AC Fan Output)* | % |
| `T09` | Flödesgivare *(Flow Rate Input)* | Hz |
| `T10` | Tryckgivare *(Pressure Sensor)* | bar |
| `T11` | Överhettning *(Super heat)* | °C |
| `T12` | Fläktens börvarvtal *(Target speed of fan motor)* | r |
| `T13` | Överhettning efter kompensering *(Over heat after commpen.)* | °C |
| `T14` | AC-spänning växelriktarkort *(Inverter plate AC voltage)* | V |
| `T15` | Frysskyddstemperatur *(Antifreeze Temp.)* | °C |
| `T16` | EC-fläktens varvtal *(EC Fan motor Speed)* | r |
| `T17` | Fläktmotor 1 varvtal *(Speed of fan motor1)* | r |
| `T18` | Fläktmotor 2 varvtal *(Speed of fan motor2)* | r |
| `T19` | Mellanledsspänning (DC-bus) *(Buses voltage)* | V |
| `T20` | Frekvensbegränsning aktiv *(Limited Frequency Protect State)* | — |
| `T21` | Frekvensnedtrappning aktiv *(Frequency Reduction Protect State)* | — |
| `T22` | Batteritemperatur 2 *(Coil 2 Temp.)* | °C |
| `T23` | Drivkortets status 1 *(driver board running state 1)* | — |
| `T24` | Drivkortets status 2 *(driver board running state 2)* | — |
| `T25` | Drivkortets status 3 *(driver board running state 3)* | — |
| `T26` | Drivkortets status 4 *(driver board running state 4)* | — |
| `T27` | Drivkortets status 5 *(driver board running state 5)* | — |
| `T28` | Börfrekvens *(Target frequency)* | — |

`T02` och `T03` är de två du vill ha i Home Assistant. `T07 × T14` ger
momentan effekt i watt.

### Utgångar och kompressor — `O`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `O01` | Kompressor *(Compressor)* | — |
| `O02` | Fläkt hög *(High fan)* | — |
| `O03` | Fläkt låg *(Low fan)* | — |
| `O04` | Cirkulationspump *(Circulate pump)* | — |
| `O05` | 4-vägsventil *(4-way valve)* | — |
| `O06` | Expansionsventil *(Exp. Valve)* | — |
| `O07` | Kompressorns utfrekvens *(Comp. Output frequency)* | Hz |
| `O08` | Kompressorström *(Compressor current)* | A |
| `O09` | IPM-temperatur *(IPM Temp.)* | °C |

### Ingångar och brytare — `S`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `S01` | Högtryckspressostat *(HP switch)* | — |
| `S02` | Lågtryckspressostat *(LP switch)* | — |
| `S03` | Flödesvakt *(Flow switch)* | — |
| `S04` | Fjärrstyrningsingång *(Remote switch)* | — |
| `S05` | Lägesomkopplare *(Mode switch)* | — |
| `S06` | Master/slav-omkopplare *(Master/Slave switch)* | — |

`S03` (flödesvakt) är den viktigaste för automation: den talar om ifall
poolpumpen går, vilket avgör om värmepumpen får starta.

## Servicenivå — rör bara om du vet vad du gör

Följande grupper styr kompressorskydd, avfrostning och expansionsventil.
Felaktiga värden kan skada pumpen. Läs gärna, skriv inte.

### Systemparametrar — `H`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `H01` | Power Down Memory | — |
| `H02` | Mode Type | — |
| `H03` | Temperature Unit | °C |
| `H06` | Heating Min. frequency | — |
| `H07` | Cooling Min. frequency | — |
| `H08` | Heating Max frequency | — |
| `H09` | Cooling Max frequency | — |
| `H10` | Delay off time | — |
| `H11` | Auto mode restarting time | — |
| `H12` | Compressor type | — |
| `H13` | Comp. Defrost Frequency | — |
| `H14` | Frequency Cycle of 0.2℃ | — |
| `H15` | Comp. Overcurren Protect | — |
| `H16` | Refrigerant Type | — |
| `H17` | Cool start Compen. Low temp. | — |
| `H18` | Cool stop Compen. Low temp. | — |
| `H19` | Cool Max. Frequency low temp. | — |
| `H20` | Cool start Compen. high temp. | — |
| `H21` | Cool stop Compen. High temp. | — |
| `H22` | Cool stop Frequency high temp. | — |
| `H23` | Heat start Compen.low temp. | — |
| `H24` | Heat stop Compen.low temp. | — |
| `H25` | Heat Max.frequency low temp | — |
| `H26` | Heat start Compen.high temp. | — |
| `H27` | Heat stop Compen.high temp. | — |
| `H28` | Heat Max.frequency high temp. | — |
| `H29` | Max. Pressure Sensor Value | — |
| `H30` | Min. Pressure Sensor Value | — |
| `H31` | Ambient temp. before commpen. | — |
| `H32` | Ambient temp. after commpen. | — |
| `H33` | Max. Frequency silent comp. | — |
| `H34` | Comp. stop. | — |
| `H35` | Temp Difference of Start Freq. | — |
| `H36` | Start Frequency | — |
| `H37` | Unit Address | — |
| `H38` | Pressure Measurement | — |
| `H39` | Resonance 1 | — |
| `H40` | Resonance 2 | — |
| `H41` | Resonance 3 | — |
| `H42` | Fast Test Mode | — |
| `H43` | Dual Coil | — |

`H37` är pumpens Modbus-slavadress. `H03` avgör om temperaturer rapporteras i
°C eller °F, vilket påverkar skalningen.

### Avfrostning — `D`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `D01` | Stat Defrosting Temp | °C |
| `D01-bar` | Start setp. | bar |
| `D02` | End Defrosting Temp | °C |
| `D03` | Defrosting Cycle | min |
| `D04` | Max. Duration | min |
| `D06` | Defrost type | — |
| `D07` | Out Temp when Defrost | °C |
| `D08` | Defrost Coil Temp. Deviation | °C |
| `D08-bar` | Compensation offset | bar |
| `D09` | Defrost out Temp. Deviation | °C |
| `D10` | Defrost ending coil temp. | °C |
| `D10-bar` | Defrost ending pressure. | bar |

### Expansionsventil — `E`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `E01` | EEV Mode | — |
| `E02` | Super Heat | °C |
| `E03` | Init. Place | — |
| `E04` | Min. Place | — |
| `E05` | Defrost Place | — |
| `E06` | Cooling Place | — |
| `E07` | EEV exhaust set temp. | °C |
| `E09` | EEV step proportion value | — |
| `E10` | EEV step integral value | — |
| `E11` | EEV step differential value | — |
| `E12` | Super heatcompen. differ. | °C |

### Fläkt och frekvens — `F`

| Kod | Betydelse | Enhet |
|-----|-----------|-------|
| `F01` | Speed | — |
| `F02` | Max. cool | °C |
| `F02-bar` | Cooling high speed pressure | bar |
| `F03` | Min. cool | °C |
| `F03-bar` | Cooling low speed pressure | bar |
| `F04` | Stop cool | °C |
| `F04-bar` | Cooling motor off pressure | bar |
| `F05` | Max. heat | °C |
| `F05-bar` | Heating high speed pressure | bar |
| `F06` | Min. heat | °C |
| `F06-bar` | Heating low speed pressure | bar |
| `F07` | Stop heat | °C |
| `F07-bar` | Heating motor off pressure | bar |
| `F10` | Ctrl. probe | — |
| `F11` | Heating Max. Duty Ratio | % |
| `F12` | Cooling Fan Duty Ratio | % |
| `F13` | Heating Min. fan duty ratio | % |
| `F14` | Timer Mute Start | h |
| `F15` | Timer Mute End | h |
| `F16` | Duty Ratio of Mute Mode | % |
| `F17` | Timer Mute ON/OFF | — |
| `F18` | Manual Fan motor Speed | — |
| `F19` | AC Fan Rated Duty Ratio | % |
| `F20` | PWM Detect/Antifreeze Temp. | — |

Koder med suffixet `-bar` gäller enheter med tryckgivare i stället för
temperaturgivare för avfrostningsstyrning (`H38` avgör vilket).

## Modbus-funktionskoder

Det som faktiskt går över tråden när WiFi-modulen pollar:

| Kod | Funktion | Används till |
|-----|----------|--------------|
| `0x01` | Read Coils | på/av och andra skrivbara flaggor |
| `0x02` | Read Discrete Inputs | statusbitar: `S`-ingångar, `O`-utgångar, larm |
| `0x03` | Read Holding Registers | inställningar: `R`, `P`, `H`, `D`, `E`, `F` |
| `0x04` | Read Input Registers | mätvärden: `T`, `O07`–`O09` |
| `0x05` | Write Single Coil | slå på/av |
| `0x06` | Write Single Register | sätta börvärde eller parameter |
| `0x10` | Write Multiple Registers | flera parametrar på en gång |

`tools/rs485_sniff.py` skriver ut dessa i klartext när den lyssnar på bussen.

## Källa

Parametertabellen är hämtad från
[radical-squared/aquatemp](https://github.com/radical-squared/aquatemp),
Home Assistant-integrationen mot AquaTemp/PHNIX-molnet. Svenska
översättningar och grupperingen är gjorda här.
