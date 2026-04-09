#!/usr/bin/env python

import argparse
import datetime
import time
import subprocess
import os
import wave
from piper import PiperVoice

# ================== KONFIGURACJA ==================
MODEL_PATH = (
    "voices/pl_PL-gosia-medium.onnx"  # ← zmień na darkman jeśli wolisz męski głos
)
VOICE = PiperVoice.load(MODEL_PATH)

TEMP_WAV = "/tmp/current_time.wav"
# =================================================

# Słownik godzin po polsku — mianownik (nominative): "pierwsza", "druga", ...
HOURS_PL = [
    "północ",  # 0
    "pierwsza",
    "druga",
    "trzecia",
    "czwarta",
    "piąta",
    "szósta",
    "siódma",
    "ósma",
    "dziewiąta",
    "dziesiąta",
    "jedenasta",
    "dwunasta",
    "trzynasta",
    "czternasta",
    "piętnasta",
    "szesnasta",
    "siedemnasta",
    "osiemnasta",
    "dziewiętnasta",
    "dwudziesta",
    "dwudziesta pierwsza",
    "dwudziesta druga",
    "dwudziesta trzecia",  # 23
]

# Godziny w dopełniaczu/miejscowniku — do "po X" i "wpół do X"
HOURS_GENITIVE_PL = [
    "północy",  # 0
    "pierwszej",
    "drugiej",
    "trzeciej",
    "czwartej",
    "piątej",
    "szóstej",
    "siódmej",
    "ósmej",
    "dziewiątej",
    "dziesiątej",
    "jedenastej",
    "dwunastej",
    "trzynastej",
    "czternastej",
    "piętnastej",
    "szesnastej",
    "siedemnastej",
    "osiemnastej",
    "dziewiętnastej",
    "dwudziestej",
    "dwudziestej pierwszej",
    "dwudziestej drugiej",
    "dwudziestej trzeciej",  # 23
]

# Minuty po polsku (liczebniki główne, rodzaj żeński dla 1 i 2)
MINUTES_PL = {
    1: "jedna",
    2: "dwie",
    3: "trzy",
    4: "cztery",
    5: "pięć",
    6: "sześć",
    7: "siedem",
    8: "osiem",
    9: "dziewięć",
    10: "dziesięć",
    11: "jedenaście",
    12: "dwanaście",
    13: "trzynaście",
    14: "czternaście",
    15: "piętnaście",
    16: "szesnaście",
    17: "siedemnaście",
    18: "osiemnaście",
    19: "dziewiętnaście",
    20: "dwadzieścia",
    21: "dwadzieścia jedna",
    22: "dwadzieścia dwie",
    23: "dwadzieścia trzy",
    24: "dwadzieścia cztery",
    25: "dwadzieścia pięć",
    26: "dwadzieścia sześć",
    27: "dwadzieścia siedem",
    28: "dwadzieścia osiem",
    29: "dwadzieścia dziewięć",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Polski zegar mówiący")
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        metavar="HOUR",
        help="Początek zakresu godzin (0-23, domyślnie: 0)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=23,
        metavar="HOUR",
        help="Koniec zakresu godzin (0-23, domyślnie: 23)",
    )
    parser.add_argument(
        "--time",
        type=str,
        default=None,
        metavar="HH:MM",
        help="Ustaw symulowany czas startowy (np. 16:00)",
    )
    parser.add_argument(
        "--exit", action="store_true", help="Uruchom raz i zakończ (do debugowania)"
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Powiedz aktualny czas (z minutami) i zakończ",
    )
    return parser.parse_args()


def speak(text: str):
    print(f"Mówię: {text}")
    with wave.open(TEMP_WAV, "wb") as wav_file:
        VOICE.synthesize_wav(text, wav_file)

    subprocess.run(
        ["aplay", TEMP_WAV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    if os.path.exists(TEMP_WAV):
        os.remove(TEMP_WAV)


def get_spoken_time(hour, minute):
    """Zwraca naturalnie brzmiący czas po polsku"""
    if minute == 0:
        return HOURS_PL[hour]
    elif minute == 15:
        return f"kwadrans po {HOURS_GENITIVE_PL[hour]}"
    elif minute == 30:
        next_hour = (hour + 1) % 24
        return f"wpół do {HOURS_GENITIVE_PL[next_hour]}"
    elif minute == 45:
        next_hour = (hour + 1) % 24
        return f"za kwadrans {HOURS_PL[next_hour]}"
    elif minute < 30:
        return f"{MINUTES_PL[minute]} po {HOURS_GENITIVE_PL[hour]}"
    else:
        remaining = 60 - minute
        next_hour = (hour + 1) % 24
        return f"za {MINUTES_PL[remaining]} {HOURS_PL[next_hour]}"


def is_in_range(hour, start, end):
    """Sprawdza czy godzina mieści się w zakresie (obsługuje przejście przez północ)"""
    if start <= end:
        return start <= hour <= end
    else:
        # Zakres przechodzi przez północ, np. start=22, end=6
        return hour >= start or hour <= end


def main():
    args = parse_args()

    # Walidacja zakresu godzin
    if not (0 <= args.start <= 23):
        print(f"Błąd: --start musi być w zakresie 0-23, podano {args.start}")
        return
    if not (0 <= args.end <= 23):
        print(f"Błąd: --end musi być w zakresie 0-23, podano {args.end}")
        return

    # Oblicz przesunięcie czasu dla opcji --time
    if args.time:
        try:
            h, m = map(int, args.time.split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except ValueError:
            print(
                f"Błąd: --time musi być w formacie HH:MM (np. 16:00), podano '{args.time}'"
            )
            return
        real_now = datetime.datetime.now()
        fake_now = real_now.replace(hour=h, minute=m, second=0, microsecond=0)
        time_offset = fake_now - real_now
    else:
        time_offset = datetime.timedelta(0)

    def get_now():
        return datetime.datetime.now() + time_offset

    # Tryb --now: powiedz aktualny czas i zakończ
    if args.now:
        now = get_now()
        text = get_spoken_time(now.hour, now.minute)
        speak(text)
        return

    print("🕒 Polski zegar mówiący uruchomiony!")
    if args.start != 0 or args.end != 23:
        print(f"   Zakres godzin: {args.start}:00 – {args.end}:00")
    if args.time:
        print(f"   Symulowany czas startowy: {args.time}")
    print("   Mówi samą godzinę co pełną godzinę.\n")
    if not args.exit:
        print("   (Ctrl + C aby wyłączyć)")

    while True:
        now = get_now()

        # Mówimy dokładnie o pełnej godzinie
        if now.minute == 0 and now.second < 5:
            if is_in_range(now.hour, args.start, args.end):
                speak(get_spoken_time(now.hour, 0))
            else:
                print(
                    f"Godzina {now.hour}:00 poza zakresem ({args.start}–{args.end}), pomijam."
                )

            if args.exit:
                break
            time.sleep(65)  # żeby nie powtórzył w tej samej minucie
            continue

        if args.exit:
            print(f"Czas: {now.strftime('%H:%M:%S')} — nie jest pełna godzina.")
            break

        # Obliczamy ile sekund do następnej pełnej godziny
        seconds_to_next_hour = ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_to_next_hour + 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
