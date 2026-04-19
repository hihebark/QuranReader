import sqlite3
from .constants import LAYOUT_DB, TEXT_DB


def load_surah_pages() -> dict[int, int]:
    """Return {surah_number: first_page} from the mushaf layout database."""
    try:
        conn = sqlite3.connect(LAYOUT_DB)
        rows = conn.execute(
            "SELECT CAST(surah_number AS INT), page_number FROM pages "
            "WHERE surah_number != '' ORDER BY CAST(surah_number AS INT)"
        ).fetchall()
        conn.close()
        return {s: p for s, p in rows}
    except Exception as e:
        print(f"Layout DB error: {e}")
        return {}


def load_basmala() -> str:
    """Return the Basmala string exactly as stored in the text database."""
    try:
        conn = sqlite3.connect(TEXT_DB)
        row = conn.execute(
            "SELECT arabic FROM ayahs WHERE surah_number=1 AND ayah_number=1"
        ).fetchone()
        conn.close()
        return row[0].lstrip('\ufeff') if row else ""
    except Exception:
        return ""


def load_ayahs(surah_number: int) -> list[tuple[int, str, str]]:
    """Return [(ayah_number, arabic, english)] for the given surah."""
    try:
        conn = sqlite3.connect(TEXT_DB)
        rows = conn.execute(
            "SELECT ayah_number, arabic, english FROM ayahs "
            "WHERE surah_number=? ORDER BY ayah_number",
            (surah_number,)
        ).fetchall()
        conn.close()
        return [(n, ar.lstrip('\ufeff'), en) for n, ar, en in rows]
    except Exception as e:
        print(f"Text DB error: {e}")
        return []


SURAH_FIRST_PAGE: dict[int, int] = load_surah_pages()
BASMALA: str = load_basmala()
