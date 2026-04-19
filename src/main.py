#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quran_reader.window import QuranBrowser


def main():
    app = QuranBrowser()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
