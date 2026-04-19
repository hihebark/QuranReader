#!/usr/bin/env python3
"""
One-time script to build data/quran-text.db from alquran.cloud API.
Run once: python3 scripts/build_text_db.py
Resumes safely if interrupted.
"""
import json
import os
import sqlite3
import time
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH  = os.path.join(DATA_DIR, "quran-text.db")
BASE_URL = "http://api.alquran.cloud/v1"


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ayahs (
            surah_number  INTEGER,
            ayah_number   INTEGER,
            arabic        TEXT,
            english       TEXT,
            PRIMARY KEY (surah_number, ayah_number)
        )
    """)
    conn.commit()

    done = {r[0] for r in conn.execute("SELECT DISTINCT surah_number FROM ayahs").fetchall()}

    for n in range(1, 115):
        if n in done:
            print(f"  {n}/114 already cached")
            continue

        print(f"  {n}/114 downloading...", end=" ", flush=True)
        data = fetch(f"{BASE_URL}/surah/{n}/editions/quran-uthmani,en.sahih")
        ar = data['data'][0]['ayahs']
        en = data['data'][1]['ayahs']

        conn.executemany(
            "INSERT OR REPLACE INTO ayahs VALUES (?,?,?,?)",
            [(n, a['numberInSurah'], a['text'], e['text']) for a, e in zip(ar, en)]
        )
        conn.commit()
        print("done")
        time.sleep(0.25)

    total = conn.execute("SELECT COUNT(*) FROM ayahs").fetchone()[0]
    conn.close()
    print(f"\nBuilt {DB_PATH}  ({total} ayahs)")


if __name__ == "__main__":
    main()
