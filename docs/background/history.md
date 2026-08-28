# Where these data come from

Working with the cresis servers you are about to access a very powerful tool that has algorthimice and data storage conventions inherited from the the history of radar data collected across Antarctica and Greenland.

## Why use radar?

Radar is the practical way to see through several hundred meters (up to 3-4 kilometers) of ice. Ice is transparent to radio waves, so a downward-looking radar can reveal information about internal layers and the ice-bed interface. Many traces collected and synthetically averaged in the along track, produce a **radargram**: a vertical slice through the ice sheet, which reveals information about the structure and physical properties of the ice sheet in space and time.

The returns are weak, the environment is enormous, and you need to cover continents. 
That is an engineering problem as much as a science one, which is why the software you are about to use came out of an engineering
centre.

## CReSIS

The **Center for Remote Sensing of Ice Sheets** was established at the
University of Kansas on 1 June 2005 as a National Science Foundation
[Science and Technology Center](https://www.nsf.gov/od/oia/ia/stc), with an
initial $19 million grant — one of only two STCs established that year. Its
founding director was Prasad Gogineni.

KU led it, with core partners at Elizabeth City State University, Haskell
Indian Nations University, the University of Maine, Ohio State University and
Penn State. A five-year renewal added a further $17.9 million, bringing the
total NSF award to roughly $36.9 million, and the centre held STC status until
2017.

The mission was deliberately dual: build **new instruments** for measuring ice
sheets, and build the **models and data systems** to interpret what they
returned. That combination is why one organisation ended up owning radar
hardware, the processing chain, the data archive and the picking tools — the
whole stack you are about to work in.

The centre still exists at KU, now as the **Center for Remote Sensing and
Integrated Systems** (same acronym, broader remit), directed by Carl Leuschen.

### The instruments, and why frequency decides everything

The centre already had a fleet of radars rather than one, and the reason is a
single unavoidable trade-off.

**Lower frequencies travel further through ice.** Transmission loss rises with
frequency, so if you want an echo back from the bed through three kilometres of
ice, you work below about 500 MHz.

**Higher frequencies give finer resolution.** Range resolution depends on
bandwidth, and you can only get wide bandwidth if the carrier is high enough to
accommodate it. Centimetre-scale snow layering needs gigahertz of bandwidth,
which is simply not available down in the VHF band.

You cannot have both, so you build several instruments. The accumulation
radar's centre frequency was picked explicitly as the balance point between
these two pressures.

That trade-off is the organising principle of the whole archive. **The four
frequency families are exactly the directories you will see on disk:**

| Family | Band | Frequency | Sees | Directory |
|---|---|---|---|---|
| **Radar depth sounders** | HF–VHF | ~1–600 MHz | The full ice column, including the bed | `rds` |
| **Accumulation radars** | UHF | ~500–2000 MHz | Shallow to deep internal layers | `accum` |
| **Snow radars** | L- to Ku-band | ~1–18 GHz | Shallow snow layers, snow on sea ice | `snow` |
| **Altimeters** | Ku- to Ka-band | ~12–38 GHz | The surface; minimal penetration | `kuband`, `kaband` |

Read down that table and you are reading depth: `rds` reaches the bed, `accum`
images the layered upper ice, `snow` resolves individual snow layers, and the
altimeters barely get past the surface — which is the point, because surface
elevation is what they are for.

The four IceBridge instruments sit in that scheme as MCoRDS (`rds`), the
accumulation radar (`accum`), the snow radar (`snow`) and the Ku-band altimeter
(`kuband`).

When you see `accum` in a path you are looking at the UHF system — that is the
one the [fabric work](../doing-science/fabric-polarimetry.md) uses in a
ground-based configuration.

"Multichannel" in MCoRDS is the important word for anything 3D: multiple
antenna elements let you resolve the *direction* an echo came from, not just
its delay. That is what makes
[cross-track swath processing](../doing-science/swath-cross-track-picking.md)
possible, and why some products carry an extra dimension.

Each family also has a characteristic transmit architecture, which you will
meet as `radar_type` in the toolbox: the snow and altimeter systems are **FMCW
deramp-on-receive**, the depth sounders are **pulsed**, and the accumulation
radars have been all three across their generations. See
[what the data look like](../reference/data-files.md#why-there-are-five-radar-directories)
for how the individual hardware generations map onto these directories.

## Operation IceBridge

NASA's **ICESat** laser altimeter finished its service in 2009. Its successor,
**ICESat-2**, would not launch until September 2018. A nine-year gap in
satellite altimetry over the ice sheets, at exactly the moment they were
starting to change quickly, was unacceptable.

**Operation IceBridge** filled it with aircraft. From 2009 to 2019 — eleven
years and more than a thousand survey flights — NASA flew instrumented aircraft
over the Arctic, Antarctic and Alaska. The first Arctic flights were in March
2009 over Greenland; Antarctic flights began that October. The final polar
flight was in November 2019, a year after ICESat-2 reached orbit.

CReSIS operated **four radar instruments** on IceBridge — MCoRDS, the snow
radar, the Ku-band altimeter and the accumulation radar — flying on a rotating
cast of aircraft including the NASA P-3 Orion, the DC-8, a King Air B-200, a
Gulfstream V and an HU-25C Falcon. Indiana University provided data management.

This matters to you for a very practical reason: **IceBridge is why the archive
is as large and as consistent as it is.** A decade of sustained, funded, annual
flying with the same instruments and the same processing chain produced the
seasons you will be searching through, and the file conventions you are about
to learn were shaped by the need to handle that volume systematically. The
`YYYY_LOCATION_PLATFORM` season naming exists because there were that many
campaigns to keep straight.

It is also why the toolbox has so much calibration machinery. Eleven years of
different aircraft, different antenna installations and evolving hardware means
every season has its own system time delay, its own channel equalization and
its own quirks — all recorded per season in the parameter spreadsheets.

Some of the science that came out of it is worth knowing: IceBridge found the
longest canyon on Earth beneath the Greenland ice sheet, and its repeat surveys
of Pine Island and Thwaites in West Antarctica underpin much of what we now
think about marine ice-sheet instability.

## Open Polar Radar

The tools you are using are no longer a single centre's internal codebase.
**[Open Polar Radar](https://openpolarradar.org/)** (OPR) is the successor
effort: an open software ecosystem intended to consolidate polar radar software
and standardise the datasets so they are searchable across institutions.

Current collaborators include the Alfred Wegener Institute, the British
Antarctic Survey, the Center for Oldest Ice Exploration, CECs in Chile, CReSIS,
Lamont-Doherty, the National Institute of Polar Research, the Norwegian Polar
Institute, Stanford Radio Glaciology, UTIG and the University of Washington.

Practically, this means:

- The toolbox is public, on [GitLab](https://gitlab.com/openpolarradar/opr),
  and you can contribute to it.
- Much of the processed data is public, at
  [data.cresis.ku.edu](https://data.cresis.ku.edu/) and through the
  [geoportal](https://openpolarradar.org/).
- The naming still shows its history. You will see `cresis` in paths, `CSARP_`
  prefixes on product directories (from "CReSIS SAR Processor"), and
  `opr_` prefixes on newer functions. Same system, different eras.

## What to read next

- **[Finding data](../doing-science/finding-data.md)** — the vocabulary of
  seasons, segments and frames, and how to search geographically.
- **[What the data look like](../reference/data-files.md)** — the directory
  tree and what is actually inside an echogram file.

## Citing and acknowledging

If you publish anything using these tools, you owe both a citation and an
acknowledgment:

> Open Polar Radar. (2023). opr (Version 3.0.1) \[Computer software\].
> <https://doi.org/10.5281/zenodo.5683959>

The acknowledgment text, which lists the supporting NASA and NSF grants, is on
the [OPR wiki home page](https://gitlab.com/openpolarradar/opr/-/wikis/home#acknowledgment).
Use it verbatim. This infrastructure exists because it was funded, and the
funding continues partly because people cite it.

## Sources

- [CReSIS](https://cresis.ku.edu/) and its
  [NSF award record](https://www.nsf.gov/awardsearch/showAward?AWD_ID=0424589)
- [NASA: Operation IceBridge completes eleven years of polar surveys](https://www.nasa.gov/missions/icebridge/nasas-operation-icebridge-completes-eleven-years-of-polar-surveys/)
- [NSIDC IceBridge data](https://nsidc.org/data/icebridge)
- [Operation IceBridge overview](https://en.wikipedia.org/wiki/Operation_IceBridge)
