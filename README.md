# Single Wave File to CUE/Labels Splitter Py Script

## Purpose

This is a Python script to assist splitting a single wav file into segments. It converts a list of audio segments ("tracks" as is CD tracks) provided as a text file containing track lengths, to a CUE sheet or a labels.txt for use in Audacity.

**Notes**
- The script does not read or write wav files—It is for converting timestamp data between common track duration based formats to tool-friendly formats that use total time elapsed.
- The author has no affiliation with the Audacity project.

## Usage

**Python Version**

Python 3.6+ (uses datetime.timedelta)

**Generate tracks.cue (default)**
>python wav_cue.py timings.txt

**Generate labels.txt**
>python wav_cue.py --labels timings.txt

## Compatibility

- CUE Tools - Standard CUE sheet format for CD/DVD authoring software
- Audacity workflows - Import generated `labels.txt` via File →Import →Labels

## Input File Example

Input files require total length of wav file on first line, followed by a triple hyphen on new line, then track labels and duration in CSV format. Track durations support three decimal digits, but if none, the script will assume .000:

```
GiantWaveFile,0:20:17.550
---
Track01,0:06:02
Track02,0:04:18
Track03,0:09:58
```
## Output Example

>python wav_cue.py timings.txt

```
REM GENRE AudioCD
REM DATE 2025
TITLE Album_Title
PERFORMER Artist_Name
FILE "GiantWaveFile.wav" WAVE

  TRACK 01 AUDIO
    TITLE "Track01"
    INDEX 01 00:06:01.850

  TRACK 02 AUDIO
    TITLE "Track02"
    INDEX 01 00:10:19.700

  TRACK 03 AUDIO
    TITLE "Track03"
    INDEX 01 00:20:17.550
```

>python wav_cue.py --labels timings.txt

```
0.000	361.850	Track01
361.850	619.700	Track02
619.700	1217.550	Track03
```

## Console Output Example

```
GiantWaveFile duration: 00:20:17.550
Tracks sum: 00:20:18.000
Total difference: 0.450s
Track count: 3

Rounding error distribution summary:
  Adjustment per track: -0.150s
  Total adjustment: -0.450s
Generated: tracks.cue
```

## Code

View source: [wav_cue.py](wav_cue.py)

## Rounding Error Handling

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
