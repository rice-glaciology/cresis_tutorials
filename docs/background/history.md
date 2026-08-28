# Where these data come from

Working with the cresis servers you are about to access a very powerful tool that has algorthimice and data storage conventions inherited from the the history of radar data collected across Antarctica and Greenland.

## Why use radar?

Radar is the practical way to see through several hundred meters (up to 3-4 kilometers) of ice. Ice is transparent to radio waves, so a downward-looking radar can reveal information about internal layers and the ice-bed interface. Many traces collected and synthetically averaged in the along track, produce a **radargram**: a vertical slice through the ice sheet, which reveals information about the structure and physical properties of the ice sheet in space that can be used to understand present and past flow conditions.

## CReSIS

The **Center for Remote Sensing of Ice Sheets** was established at the University of Kansas in June 2005 as a National Science Foundation [Science and Technology Center](https://www.nsf.gov/od/oia/ia/stc), with an initial $19 million grant.

Other instiutions invovled in the center included Elizabeth City State University, Haskell Indian Nations University, the University of Maine, Ohio State University and Penn State. A five-year renewal added another $17.9 million, bringing the total NSF award to roughly $36.9 million. The centre held STC status until 2017.

The mission had multiple parts, but their main objective was to build **new radar and seismic instruments** for measuring the physical properties of ice sheets, and build the **models and data systems** to interpret these data. 
This lead to the development of what was first the cresis toolbox, and which is now known as the opr_toolbox.
 
The center still exists at KU, now as the **Center for Remote Sensing and Integrated Systems** (broader remit to include projects connected to radar development for non-ice-sheet applications).

### Instrument naming conventions

The center already has a fleet of radars designed to target different features and different depths in the ice column.

**Lower frequency radar pulses travel further through ice.** Transmission loss or attenuation, rises with
frequency, so if you want to understand the base of a 2500m ice sheet, it's best to work below about 500 MHz.

**Larger bandwidth systems (that necessarily transmit at higher freuqnecies produce finer resolution.** 
Range resolution depends on bandwidth, and it's easier to increase bandwidth by transmitting at higher frequencies becuase of the geometry, size and shape of the antennas needed to produce these pulses. Centimeter-scale changes in seasonal snow reflectivity require gigahertz of bandwidth, which is not available down in the HF band.

Because the targets of different campaigns are often location specific orienetned mostly by science questions (not always radar engineering) you build several instruments.
These include the "ku/kaband" radar altimeter, the "snow" radar, the "accumulationa" radar, and the radio depth sounder, "rds". 

**The four frequency families are exactly the directories you will see on disk:**

| Family | Band | Frequency | Sees | Directory |
|---|---|---|---|---|
| **Radar depth sounders** | HF–VHF | ~1–600 MHz | The full ice column, including the bed | `rds` |
| **Accumulation radars** | UHF | ~500–2000 MHz | Shallow to deep internal layers | `accum` |
| **Snow radars** | L- to Ku-band | ~1–18 GHz | Shallow snow layers, snow on sea ice | `snow` |
| **Altimeters** | Ku- to Ka-band | ~12–38 GHz | The surface; minimal penetration | `kuband`, `kaband` |

This list is sorted according to decreasing depth penetration.  `rds` reaches the bed, `accum`
images the layered upper ice and the bed down to depths near 1500-2400m dependeing on the transmit power, `snow` resolves seasonal snow layering, and the altimeters barely transmits through the surface, but can often image the base of the sea-ice column.

When you see `accum` in a path you are looking at the UHF system — for several ground based seasons, these data transmit and receive pulses polarized in horizontal and vertical antenna orientations makeing it possible to use these methods to understand [ice fabric](../doing-science/fabric-polarimetry.md).

"Multichannel" in MCoRDS is the important for doing any 3D tomography where using multiple antenna elements we can resolve the *direction* an echo came from, not just its delay. 
That is what makes [cross-track swath processing](../doing-science/swath-cross-track-picking.md)
possible, and why some products carry an extra dimension.

Each family also has a characteristic transmit pulse characterized by `radar_type` in the toolbox: the snow and altimeter systems are **FMCW
deramp-on-receive**, the depth sounders are **pulsed**, and the accumulation radars have been all three across their generations. 
See [what the data look like](../reference/data-files.md#why-there-are-five-radar-directories) for how the individual hardware generations map onto these directories.

## Operation IceBridge

NASA's **ICESat** laser altimeter finished its service in 2009. Its successor, **ICESat-2**, would not launch until September 2018. To quickly bridge this nine-year gap in
satellite altimetry over the ice sheets, NASA quickly pivoted to airborne missions as part of **Operation IceBridge**.
Missions included flights over the Arctic, Antarctic and Alaska. 
The first Arctic flights were in March 2009 over Greenland; Antarctic flights began that October. 
The final polar flight was in November 2019, a year after ICESat-2 reached orbit.

CReSIS operated **four radar instruments** on IceBridge — MCoRDS, the snow radar, the Ku-band altimeter and the accumulation radar. 
These systems, which changed year-to-year with improvements in radar hardware and signal processing software were fit to several aircraft: NASA P-3 Orion, the DC-8, a King Air B-200, a
Gulfstream V and an HU-25C Falcon. 
Data were managed by Indiana University (which has a strong history of storage and compute infrastructure).

The program provided an unprecedented volume of radar data flown with like instruments, processed consistently between seasons.
The project's duration, flight coverage and original mission goals also inform the kinds of questions we can ask with these data. 
The data volumes (and instrument vintage) also inform the conventions needed to handle the volume systematically.
Generally, these data are labeled by year, location, and platform `YYYY_LOCATION_PLATFORM` as during a season that platform hardware remained consistent.

Some of the science that came out of it is worth knowing.
IceBridge found the longest canyon on Earth beneath the Greenland ice sheet, and its repeat surveys of Pine Island and Thwaites in West Antarctica underpin much of what we now know about marine ice-sheet instability.

## Open Polar Radar

The tools you are using have evolved to also ingest data collected with other radar pltforms mainted as part of *[Open Polar Radar](https://openpolarradar.org/)** (OPR). 
OPR is an open software ecosystem intended to consolidate polar radar software
and standardise the datasets so they are searchable across institutions.

Current collaborators include the Alfred Wegener Institute, the British Antarctic Survey, CECs in Chile, CReSIS, Lamont-Doherty, the National Institute of Polar Research, the Norwegian Polar Institute, Stanford Radio Glaciology, UTIG and the University of Washington.

Practically, this means:

- The toolbox is public, on [GitLab](https://gitlab.com/openpolarradar/opr),
  and you can contribute to it as you develop code.
- Much of the processed data is public, at
  [data.cresis.ku.edu](https://data.cresis.ku.edu/) and through the
  [geoportal](https://openpolarradar.org/).
- Because of the history of the center the naming still ports from old conventions (i.e. you will see `cresis` in paths, `CSARP_`
  prefixes on product directories (stands for "CReSIS SAR Processor"), and `opr_` prefixes on newer algorthims.

## What to read next

- **[Finding data](../doing-science/finding-data.md)** — the vocabulary of
  seasons, segments and frames, and how to search geographically.
- **[Working with data](../reference/data-files.md)** — the directory
  tree and what is actually inside an echogram file.

## Citing and acknowledging

If you publish anything using these tools, we should cite and acknowledge the toolbox:

> Open Polar Radar. (2023). opr (Version 3.0.1) \[Computer software\].
> <https://doi.org/10.5281/zenodo.5683959>

The acknowledgment text, which lists the supporting NASA and NSF grants, is on the [OPR wiki home page](https://gitlab.com/openpolarradar/opr/-/wikis/home#acknowledgment).
Use it verbatim. 
This infrastructure exists because it was funded, and the funding continues partly because people cite the work of the center.

## Sources

- [CReSIS](https://cresis.ku.edu/) and its
  [NSF award record](https://www.nsf.gov/awardsearch/showAward?AWD_ID=0424589)
- [NASA: Operation IceBridge completes eleven years of polar surveys](https://www.nasa.gov/missions/icebridge/nasas-operation-icebridge-completes-eleven-years-of-polar-surveys/)
- [NSIDC IceBridge data](https://nsidc.org/data/icebridge)
- [Operation IceBridge overview](https://en.wikipedia.org/wiki/Operation_IceBridge)
