# Speaking Clock

A multi-language speaking clock that announces the time using [Piper](https://github.com/rhasspy/piper) text-to-speech. It speaks the current hour on the hour using natural language idioms (e.g., "quarter past two", "wpół do czwartej") and supports any language through JSON data files.

## Features

- **Natural time idioms** -- not just "it is 14:30" but "half past two" (English) or "wpół do trzeciej" (Polish)
- **Multi-language** -- add a new language by creating a JSON file in `data/lang/`
- **Voice management** -- browse, download, and auto-detect Piper voices from Hugging Face
- **Bluetooth audio fix** -- plays a silent MP3 before speech to prevent clipping on Bluetooth speakers
- **Flexible scheduling** -- restrict announcements to a time range (e.g., 7:00--22:00)
- **Simulated time** -- debug with `--time HH:MM` to set a fake starting time

## Requirements

- Python 3
- [piper-tts](https://github.com/rhasspy/piper) (`pip install piper-tts`)
- `aplay` (ALSA, for WAV playback)
- `mpg123` (for blank MP3 playback)

## Installation

```bash
git clone https://github.com/jcubic/clock.git
cd clock
pip install piper-tts
```

## Usage

### Speak the current time and exit

```bash
./clock.py --now
```

### Run as a clock (announces on the hour)

```bash
./clock.py
```

### List available voices for a language

```bash
./clock.py --list-voices --lang pl
./clock.py --list-voices --lang en
```

### Install and use a specific voice

```bash
./clock.py --voice en_US-lessac-medium
```

Voices are auto-downloaded from Hugging Face if not already installed.

### Limit speaking hours

```bash
./clock.py --start 7 --end 22
```

Supports midnight wrap (e.g., `--start 22 --end 6`).

### Debug with simulated time

```bash
./clock.py --time 16:00 --exit
```

### All options

```
usage: clock.py [-h] [--lang LANG] [--voice NAME] [--list-voices]
                [--start HOUR] [--end HOUR] [--time HH:MM] [--exit] [--now]

Speaking clock — announces the time using text-to-speech

options:
  --lang LANG    Language code, e.g. pl, en (default: from system locale)
  --voice NAME   Voice name, e.g. en_US-lessac-medium (auto-downloads if missing)
  --list-voices  List available Piper voices for the current language and exit
  --start HOUR   Start hour for speaking range (0-23, default: 0)
  --end HOUR     End hour for speaking range (0-23, default: 23)
  --time HH:MM   Set simulated start time for debugging (e.g., 16:00)
  --exit         Run once and exit (for debugging)
  --now          Speak the current time (with minutes) and exit
```

## Adding a new language

Create a JSON file in `data/lang/<code>.json` (e.g., `de.json` for German). The schema:

```json
{
  "hours": ["midnight", "one o'clock", "...", "eleven o'clock"],
  "hours_alt": ["midnight", "one", "...", "eleven"],
  "minutes": {
    "1": "one", "2": "two", "...": "...", "29": "twenty nine"
  },
  "patterns": {
    "full_hour": "{hour}",
    "quarter_past": "quarter past {hour_alt}",
    "half_past": "half past {hour_alt}",
    "quarter_to": "quarter to {next_hour_alt}",
    "minutes_past": "{minutes} past {hour_alt}",
    "minutes_to": "{minutes} to {next_hour_alt}"
  }
}
```

### Fields

| Field | Required | Description |
|---|---|---|
| `hours` | Yes | 24 entries (index 0 = midnight, 12 = noon, etc.) used in `{hour}` and `{next_hour}` |
| `hours_alt` | No | 24 entries for alternate forms (e.g., genitive case). Defaults to `hours` if omitted |
| `minutes` | Yes | Keys `"1"` through `"29"` -- spoken forms for minute counts |
| `patterns` | Yes | 6 patterns using placeholders below |

### Placeholders

| Placeholder | Meaning |
|---|---|
| `{hour}` | Current hour from `hours` |
| `{hour_alt}` | Current hour from `hours_alt` |
| `{next_hour}` | Next hour from `hours` |
| `{next_hour_alt}` | Next hour from `hours_alt` |
| `{minutes}` | Minute count from `minutes` map |
| `{remaining}` | Minutes remaining to next hour (same source as `{minutes}`) |

### Pattern rules

| Pattern | When | Example (English) |
|---|---|---|
| `full_hour` | :00 | "three o'clock" |
| `quarter_past` | :15 | "quarter past three" |
| `half_past` | :30 | "half past three" |
| `quarter_to` | :45 | "quarter to four" |
| `minutes_past` | :01--:29 (not :15) | "ten past three" |
| `minutes_to` | :31--:59 (not :45) | "ten to four" |

## Project structure

```
clock.py              Main script
data/
  lang/
    en.json           English time data
    pl.json           Polish time data
  voices/             Piper voice files (.onnx + .onnx.json)
  blank.mp3           Silent MP3 for Bluetooth audio wake-up
.cache/
  voices.json         Cached voice catalog from Hugging Face (24h TTL)
```

## License

Copyright (C) [Jakub T. Jankiewicz](https://jakub.jankiewicz.org)

Released under MIT license
