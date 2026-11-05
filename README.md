# acqstat

**acqstat** is a lightweight desktop tool for rapid inspection of contactless physiological recordings acquired from Continuous Wave (CW) radar systems.

The application provides:

- Quick file loading via drag-and-drop
- Automatic metadata extraction
- Basic signal statistics
- Interactive channel plotting
- Respiratory rate estimation from breathing displacement signals
- I/Q signal visualization
- Automatic HTML report generation
- Overview plots of extracted breathing and pulse signals

Typical use cases include:

- CW radar validation
- Contactless respiration monitoring
- Contactless pulse monitoring
- Signal quality inspection
- Dataset sanity checking before further processing
- Generation of quick-look reports for studies and experiments

---

# Main Workflow

When a CSV file is dropped into the application, the following processing chain is executed:

```text
dropEvent()
│
├─ Read metadata
├─ Load dataframe
├─ Store sampling rate, duration...
├─ Compute respiratory rate (if breath signal exists)
├─ Create channel cards
└─ Enable report button
```

The application automatically parses recording metadata such as:

- Acquisition version
- Sampling frequency
- Timestamp
- Channel names
- Recording duration

If a breathing displacement signal is available (`d_breath` or `Distance_breath`), respiratory rate is estimated using a sliding-window approach.

---

# Interactive Exploration

Each detected signal receives its own statistics card.

For every channel the following information is displayed:

- Minimum value
- Maximum value
- Mean value
- Standard deviation

Users can generate:

- Full recording plots
- First-minute plots

Workflow:

```text
CHANNEL CARD BUTTON
    └─ plot_chart()
           Single signal plot
```

This mode is intended for rapid visual inspection of individual channels.

---

# Report Generation

The report button generates a HTML summary report containing signal visualisations and acquisition metadata.

```text
REPORT BUTTON
    ├─ generate_iq_thumbnail()
    │      └─ generate_svg(layout="twinx")
    │
    └─ generate_svg(...)
            │
            ├─ breath+pulse available
            │      └─ stacked-breath
            │             + RR overlays
            │
            └─ otherwise
                   uses I/Q columns
                   still through stacked-breath

Unused branch:
    generate_svg(layout="stacked")
```

---

# Plot Types

## 1. I/Q Thumbnail (Twin Axis)

Used as the report summary thumbnail.

```text
I signal  → Left Y axis
Q signal  → Right Y axis
Time      → Shared X axis
```

Purpose:

- Quick verification of radar acquisition
- Inspection of I/Q dynamic range
- Detection of clipping or saturation

---

## 2. Breathing Overview

When breathing and pulse displacement signals are available:

```text
Distance_breath
Distance_pulse
Respiratory Rate
```

the report generates minute-by-minute breathing overview plots.

Features:

- One subplot per minute
- Common signal scaling
- Respiratory-rate overlay
- Easy identification of motion artefacts
- Visual verification of breathing stability

---

## 3. Respiratory Rate Estimation

Respiratory rate is computed from:

```text
d_breath
or
Distance_breath
```

using a sliding 30-second window.

Output:

- Respiratory rate trend
- Associated timestamps

These values are overlaid on breathing overview plots.
Based on either SciPy or BioSPPy. 

---

# Typical Signal Types

Raw radar channels:

```text
I
Q
I_raw
Q_raw
```

Hardware-processed channels:

```text
Distance
Distance_breath
Distance_pulse
Distance_filter
```

Software-derived channels:

```text
d
d_breath
d_pulse
d_hsound
HR
ECG
Annotation
```

---

# Typical Use Cases

## Radar Acquisition Verification

Verify that:

- I and Q signals are present
- Dynamic range is appropriate
- Recording duration is correct



# Summary

**acqstat** is designed as a quick-look analysis and reporting tool for CW contactless physiology recordings. It enables fast inspection of radar-derived I/Q signals, breathing and pulse displacement channels, respiratory-rate estimation, and automatic report generation for physiological monitoring experiments.