import os

APP_ID = "io.github.hihebark.QuranReader"


def _find_data_dir() -> str:
    # Development: data/ sits two levels above src/quran_reader/
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(os.path.dirname(os.path.dirname(here)), "data")
    if os.path.isdir(source):
        return source
    # Installed (Flatpak / system): look in XDG data dirs
    xdg = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    for base in xdg.split(":"):
        candidate = os.path.join(base, APP_ID)
        if os.path.isdir(candidate):
            return candidate
    return source  # fallback


DATA_DIR  = _find_data_dir()
PAGES_DIR = os.path.join(DATA_DIR, "quran-pages")
LAYOUT_DB = os.path.join(DATA_DIR, "mushaf-qatar-layout.db")
TEXT_DB   = os.path.join(DATA_DIR, "quran-text.db")

HAS_TEXT_DB = os.path.exists(TEXT_DB)

APP_CSS = b"""
.mushaf-page {
    background-color: #FFFFF8;
}
.ayah-badge {
    border: 1.5px solid @accent_color;
    border-radius: 999px;
    color: @accent_color;
    font-size: 12px;
    font-weight: bold;
    padding: 4px 9px;
    min-width: 34px;
    min-height: 34px;
}
.ayah-english {
    font-size: 13px;
}
"""

# (number, arabic_name, english_name, meaning, ayah_count)
SURAHS = [
    (1,   "الفاتحة",       "Al-Fatihah",       "The Opening",               7),
    (2,   "البقرة",         "Al-Baqarah",       "The Cow",                   286),
    (3,   "آل عمران",       "Ali 'Imran",       "Family of Imran",           200),
    (4,   "النساء",         "An-Nisa",          "The Women",                 176),
    (5,   "المائدة",        "Al-Ma'idah",       "The Table Spread",          120),
    (6,   "الأنعام",        "Al-An'am",         "The Cattle",                165),
    (7,   "الأعراف",        "Al-A'raf",         "The Heights",               206),
    (8,   "الأنفال",        "Al-Anfal",         "The Spoils of War",         75),
    (9,   "التوبة",         "At-Tawbah",        "The Repentance",            129),
    (10,  "يونس",           "Yunus",            "Jonah",                     109),
    (11,  "هود",            "Hud",              "Hud",                       123),
    (12,  "يوسف",           "Yusuf",            "Joseph",                    111),
    (13,  "الرعد",          "Ar-Ra'd",          "The Thunder",               43),
    (14,  "ابراهيم",        "Ibrahim",          "Abraham",                   52),
    (15,  "الحجر",          "Al-Hijr",          "The Rocky Tract",           99),
    (16,  "النحل",          "An-Nahl",          "The Bee",                   128),
    (17,  "الإسراء",        "Al-Isra",          "The Night Journey",         111),
    (18,  "الكهف",          "Al-Kahf",          "The Cave",                  110),
    (19,  "مريم",           "Maryam",           "Mary",                      98),
    (20,  "طه",             "Ta-Ha",            "Ta-Ha",                     135),
    (21,  "الأنبياء",       "Al-Anbiya",        "The Prophets",              112),
    (22,  "الحج",           "Al-Hajj",          "The Pilgrimage",            78),
    (23,  "المؤمنون",       "Al-Mu'minun",      "The Believers",             118),
    (24,  "النور",          "An-Nur",           "The Light",                 64),
    (25,  "الفرقان",        "Al-Furqan",        "The Criterion",             77),
    (26,  "الشعراء",        "Ash-Shu'ara",      "The Poets",                 227),
    (27,  "النمل",          "An-Naml",          "The Ant",                   93),
    (28,  "القصص",          "Al-Qasas",         "The Stories",               88),
    (29,  "العنكبوت",       "Al-'Ankabut",      "The Spider",                69),
    (30,  "الروم",          "Ar-Rum",           "The Romans",                60),
    (31,  "لقمان",          "Luqman",           "Luqman",                    34),
    (32,  "السجدة",         "As-Sajdah",        "The Prostration",           30),
    (33,  "الأحزاب",        "Al-Ahzab",         "The Combined Forces",       73),
    (34,  "سبإ",            "Saba",             "Sheba",                     54),
    (35,  "فاطر",           "Fatir",            "Originator",                45),
    (36,  "يس",             "Ya-Sin",           "Ya Sin",                    83),
    (37,  "الصافات",        "As-Saffat",        "Those Who Set Ranks",       182),
    (38,  "ص",              "Sad",              "The Letter Sad",            88),
    (39,  "الزمر",          "Az-Zumar",         "The Troops",                75),
    (40,  "غافر",           "Ghafir",           "The Forgiver",              85),
    (41,  "فصلت",           "Fussilat",         "Explained in Detail",       54),
    (42,  "الشورى",         "Ash-Shuraa",       "The Consultation",          53),
    (43,  "الزخرف",         "Az-Zukhruf",       "The Ornaments of Gold",     89),
    (44,  "الدخان",         "Ad-Dukhan",        "The Smoke",                 59),
    (45,  "الجاثية",        "Al-Jathiyah",      "The Crouching",             37),
    (46,  "الأحقاف",        "Al-Ahqaf",         "The Wind-Curved Sandhills", 35),
    (47,  "محمد",           "Muhammad",         "Muhammad",                  38),
    (48,  "الفتح",          "Al-Fath",          "The Victory",               29),
    (49,  "الحجرات",        "Al-Hujurat",       "The Rooms",                 18),
    (50,  "ق",              "Qaf",              "The Letter Qaf",            45),
    (51,  "الذاريات",       "Adh-Dhariyat",     "The Winnowing Winds",       60),
    (52,  "الطور",          "At-Tur",           "The Mount",                 49),
    (53,  "النجم",          "An-Najm",          "The Star",                  62),
    (54,  "القمر",          "Al-Qamar",         "The Moon",                  55),
    (55,  "الرحمن",         "Ar-Rahman",        "The Beneficent",            78),
    (56,  "الواقعة",        "Al-Waqi'ah",       "The Inevitable",            96),
    (57,  "الحديد",         "Al-Hadid",         "The Iron",                  29),
    (58,  "المجادلة",       "Al-Mujadila",      "The Pleading Woman",        22),
    (59,  "الحشر",          "Al-Hashr",         "The Exile",                 24),
    (60,  "الممتحنة",       "Al-Mumtahanah",    "She That Is To Be Examined",13),
    (61,  "الصف",           "As-Saf",           "The Ranks",                 14),
    (62,  "الجمعة",         "Al-Jumu'ah",       "The Congregation",          11),
    (63,  "المنافقون",      "Al-Munafiqun",     "The Hypocrites",            11),
    (64,  "التغابن",        "At-Taghabun",      "The Mutual Disillusion",    18),
    (65,  "الطلاق",         "At-Talaq",         "The Divorce",               12),
    (66,  "التحريم",        "At-Tahrim",        "The Prohibitions",          12),
    (67,  "الملك",          "Al-Mulk",          "The Sovereignty",           30),
    (68,  "القلم",          "Al-Qalam",         "The Pen",                   52),
    (69,  "الحاقة",         "Al-Haqqah",        "The Reality",               52),
    (70,  "المعارج",        "Al-Ma'arij",       "The Ascending Stairways",   44),
    (71,  "نوح",            "Nuh",              "Noah",                      28),
    (72,  "الجن",           "Al-Jinn",          "The Jinn",                  28),
    (73,  "المزمل",         "Al-Muzzammil",     "The Enshrouded One",        20),
    (74,  "المدثر",         "Al-Muddaththir",   "The Cloaked One",           56),
    (75,  "القيامة",        "Al-Qiyamah",       "The Resurrection",          40),
    (76,  "الانسان",        "Al-Insan",         "The Man",                   31),
    (77,  "المرسلات",       "Al-Mursalat",      "The Emissaries",            50),
    (78,  "النبإ",          "An-Naba",          "The Tidings",               40),
    (79,  "النازعات",       "An-Nazi'at",       "Those Who Drag Forth",      46),
    (80,  "عبس",            "'Abasa",           "He Frowned",                42),
    (81,  "التكوير",        "At-Takwir",        "The Overthrowing",          29),
    (82,  "الإنفطار",       "Al-Infitar",       "The Cleaving",              19),
    (83,  "المطففين",       "Al-Mutaffifin",    "The Defrauding",            36),
    (84,  "الإنشقاق",       "Al-Inshiqaq",      "The Sundering",             25),
    (85,  "البروج",         "Al-Buruj",         "The Mansions of Stars",     22),
    (86,  "الطارق",         "At-Tariq",         "The Morning Star",          17),
    (87,  "الأعلى",         "Al-A'la",          "The Most High",             19),
    (88,  "الغاشية",        "Al-Ghashiyah",     "The Overwhelming",          26),
    (89,  "الفجر",          "Al-Fajr",          "The Dawn",                  30),
    (90,  "البلد",          "Al-Balad",         "The City",                  20),
    (91,  "الشمس",          "Ash-Shams",        "The Sun",                   15),
    (92,  "الليل",          "Al-Layl",          "The Night",                 21),
    (93,  "الضحى",          "Ad-Duhaa",         "The Morning Hours",         11),
    (94,  "الشرح",          "Ash-Sharh",        "The Relief",                8),
    (95,  "التين",          "At-Tin",           "The Fig",                   8),
    (96,  "العلق",          "Al-'Alaq",         "The Clot",                  19),
    (97,  "القدر",          "Al-Qadr",          "The Power",                 5),
    (98,  "البينة",         "Al-Bayyinah",      "The Clear Proof",           8),
    (99,  "الزلزلة",        "Az-Zalzalah",      "The Earthquake",            8),
    (100, "العاديات",       "Al-'Adiyat",       "The Courser",               11),
    (101, "القارعة",        "Al-Qari'ah",       "The Calamity",              11),
    (102, "التكاثر",        "At-Takathur",      "The Rivalry in World Increase", 8),
    (103, "العصر",          "Al-'Asr",          "The Declining Day",         3),
    (104, "الهمزة",         "Al-Humazah",       "The Traducer",              9),
    (105, "الفيل",          "Al-Fil",           "The Elephant",              5),
    (106, "قريش",           "Quraysh",          "Quraysh",                   4),
    (107, "الماعون",        "Al-Ma'un",         "The Small Kindnesses",      7),
    (108, "الكوثر",         "Al-Kawthar",       "The Abundance",             3),
    (109, "الكافرون",       "Al-Kafirun",       "The Disbelievers",          6),
    (110, "النصر",          "An-Nasr",          "The Divine Support",        3),
    (111, "المسد",          "Al-Masad",         "The Palm Fibre",            5),
    (112, "الإخلاص",        "Al-Ikhlas",        "The Sincerity",             4),
    (113, "الفلق",          "Al-Falaq",         "The Daybreak",              5),
    (114, "الناس",          "An-Nas",           "Mankind",                   6),
]

SURAH_BY_NUM = {s[0]: s for s in SURAHS}
