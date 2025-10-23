# Single Wave File to CUE/Labels Splitter Py Script

## Purpose

This is a Python script to assist splitting a single wav file into segments. It converts a list of audio segments ("tracks" as is CD tracks) provided as a text file containing track lengths or start times to a CUE sheet or a labels.txt for use in Audacity.

**Notes**
- The script does not read or write wav files—It is for converting timestamp data between simple hh:mm:ss track duration or timestamp based formats to tool-friendly formats that use total time elapsed.
- Two modes: Duration Mode (default) for track duration-based input files, and Cumulative Mode (--cumulative) for timestamp-based input files.
- The author has no affiliation with the Audacity project.

## Usage

**Python Version**

Python 3.6+ (uses datetime.timedelta)

**Command Line Switches**

- `--cumulative`: Use timestamp-based input file
- `--labels` : Generate labels.txt for Audacity workflows

**Example: Generate tracks.cue in Duration Mode (default)**

`python wav_cue.py timings.txt`

**Example: Generate labels.txt in Duration Mode (default)**

`python wav_cue.py --labels timings.txt`

**Example: Generate labels.txt from Cumulative Mode (--cumulative)**

`python wav_cue.py --cumulative --labels timings_cumulative.txt`

## Compatibility

- CUE Tools - Standard CUE sheet format for CD/DVD authoring software
- Audacity workflows - Import generated `labels.txt` via File →Import →Labels

## Input File Examples

**Duration Mode format**
Input file requires total length of wav file on first line, followed by a triple hyphen on new line, then duration and track labels in CSV format. Track durations support three decimal second digits, but if none, the script will assume .000:

```
GiantWaveFile,0:20:17.550
---
0:06:02,Track01
0:04:18,Track02
0:09:58,Track03
```

**Cumulative Mode format**
Total length of wav file on first line, followed by a triple hyphen on new line, then timestamp of the track start position and track labels in CSV format. Timestamps support three decimal second digits, but if none, the script will assume .000:
```
GiantWaveFile,0:20:17.550
---
0:00:00,Track01
0:06:02,Track02
0:10:20,Track03
```

## Output Examples

`python wav_cue.py timings.txt`

```
REM GENRE AudioCD
REM DATE 2025
TITLE Album_Title
PERFORMER Artist_Name
FILE "GiantWaveFile.wav" WAVE

  TRACK 01 AUDIO
    TITLE "Track01"
    INDEX 01 00:00:00.000

  TRACK 02 AUDIO
    TITLE "Track02"
    INDEX 01 00:06:01.850

  TRACK 03 AUDIO
    TITLE "Track03"
    INDEX 01 00:10:19.700
```

`python wav_cue.py --cumulative --labels timings_cumulative.txt`

```
0.000	362.000	Track01
362.000	620.000	Track02
620.000	1217.550	Track03
```

## Console Output Examples

**Duration Mode, CUE**
```
Duration mode
GiantWaveFile duration: 00:20:17.550
Tracks sum: 00:20:18.000
Total difference: 0.450s
Track count: 3

Rounding error distribution summary:
  Adjustment per track: -0.150s
  Total adjustment: -0.450s
Generated: tracks.cue
```

**Cumulative Mode, labels.txt**
```
Cumulative mode
GiantWaveFile duration: 00:20:17.550
Tracks sum: 00:20:17.550
Total difference: 0.000s
Track count: 3

Generated: labels.txt
```

## Code

View source: [wav_cue.py](wav_cue.py)

## Rounding Error Handling in Duration mode

Track durations typically have rounding errors and will result in a gap with wav file length. To mitigate the gap, the script will distribute it across tracks.

gap = | wav file duration - SUM(track durations) |

**Green**
gap < 0.5s × track count
Script completes conversion and logs gap distribution in console.

**Yellow**
0.5s × track count ≤ gap < 1.0s × track count  
Script warns user before proceeding, and logs gap distribution in console after completion.

**Red**
gap ≥ 1.0s × track count
Script aborts execution.

## License

This Python script is released under the [MIT License](LICENSE).

## About

**X**: [@5ynthaire](https://x.com/5ynthaire)  
**GitHub**: [https://github.com/5ynthaire](https://github.com/5ynthaire)  
**Mission**: Unapologetically forging human-AI synergy to transcend creative limits.  
**Attribution**: Created with Grok 3 by xAI (no affiliation).
