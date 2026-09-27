"""
Preprocessing and Normalization Module for Business Entity Resolution.
Handles legal suffixes, address abbreviations, noisy numbers, and open-set country normalization.
"""

import re
import unicodedata

# Legal company suffixes mapping to standard token
LEGAL_SUFFIXES = {
    r"\b(corporation|corp|incorporated|inc)\b": "inc",
    r"\b(private limited|pvt ltd|pvt\.?\s*ltd\.?|private ltd)\b": "pvtltd",
    r"\b(limited|ltd)\b": "ltd",
    r"\b(limited liability company|llc|l\.l\.c\.)\b": "llc",
    r"\b(limited liability partnership|llp|l\.l\.p\.)\b": "llp",
    r"\b(company|co)\b": "co",
    r"\b(societe anonyme|s\.a\.|sa)\b": "sa",
    r"\b(sarl|s\.a\.r\.l\.)\b": "sarl",
    r"\b(sas|s\.a\.s\.)\b": "sas",
    r"\b(gmbh|g\.m\.b\.h\.)\b": "gmbh",
    r"\b(proprietorship|prop)\b": "prop",
    r"\b(enterprises|enterprise|ent)\b": "ent",
    r"\b(services|service|serv)\b": "serv",
    r"\b(solutions|solution|sol)\b": "sol",
    r"\b(technologies|technology|tech)\b": "tech",
}

# Address abbreviations mapping
ADDRESS_ABBREVIATIONS = {
    r"\b(st|str|street)\b": "street",
    r"\b(rd|road)\b": "road",
    r"\b(ave|avenue|av)\b": "avenue",
    r"\b(blvd|boulevard)\b": "boulevard",
    r"\b(dr|drive)\b": "drive",
    r"\b(ln|lane)\b": "lane",
    r"\b(ct|court)\b": "court",
    r"\b(fl|flr|floor)\b": "floor",
    r"\b(ste|suite)\b": "suite",
    r"\b(apt|apartment)\b": "apartment",
    r"\b(hwy|highway)\b": "highway",
    r"\b(pkwy|parkway)\b": "parkway",
    r"\b(pl|place)\b": "place",
    r"\b(bldg|building)\b": "building",
    r"\b(sq|square)\b": "square",
    r"\b(ctr|center|centre)\b": "center",
    r"\b(sec|sector)\b": "sector",
    r"\b(opp|opposite)\b": "opp",
    r"\b(nr|near)\b": "near",
}

# Known country standardizations (open-set fallback preserves cleaned string)
COUNTRY_MAP = {
    "us": "us",
    "usa": "us",
    "united states": "us",
    "united states of america": "us",
    "u.s.": "us",
    "u.s.a.": "us",
    "in": "in",
    "ind": "in",
    "india": "in",
    "fr": "fr",
    "fra": "fr",
    "france": "fr",
}

def clean_text(text: str) -> str:
    """Basic text sanitation, unicode normalization, punctuation normalization."""
    if not isinstance(text, str):
        return ""
    # Normalize unicode (decompose accents, NFKD)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    # Replace & with and
    text = re.sub(r"&", " and ", text)
    # Remove special punctuation, keep alphanumeric, spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_business_name(name: str) -> str:
    """Normalize business name by standardizing legal suffixes and removing boilerplate."""
    cleaned = clean_text(name)
    if not cleaned:
        return ""
    
    # Normalize legal forms
    for pattern, repl in LEGAL_SUFFIXES.items():
        cleaned = re.sub(pattern, repl, cleaned)
        
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def normalize_address(address: str) -> str:
    """Normalize address components and abbreviations."""
    cleaned = clean_text(address)
    if not cleaned:
        return ""
        
    for pattern, repl in ADDRESS_ABBREVIATIONS.items():
        cleaned = re.sub(pattern, repl, cleaned)
        
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def normalize_country(country: str) -> str:
    """Normalize country as an open-set string label."""
    cleaned = clean_text(country)
    if not cleaned:
        return ""
    return COUNTRY_MAP.get(cleaned, cleaned)

def extract_numbers(text: str) -> set:
    """Extract numeric sequences (pin codes, building numbers, suite numbers)."""
    if not text:
        return set()
    nums = re.findall(r"\b\d+\b", text)
    return set(nums)

def preprocess_dataframe(df):
    """Applies standardized preprocessing across entity DataFrame."""
    df = df.copy()
    df["business_name_clean"] = df["business_name"].fillna("").apply(normalize_business_name)
    df["business_address_clean"] = df["business_address"].fillna("").apply(normalize_address)
    df["country_clean"] = df["country"].fillna("").apply(normalize_country)
    
    # Pre-extract token sets for fast candidate generation & feature computation
    df["name_tokens"] = df["business_name_clean"].apply(lambda s: set(s.split()) if s else set())
    df["address_tokens"] = df["business_address_clean"].apply(lambda s: set(s.split()) if s else set())
    df["address_numbers"] = df["business_address"].fillna("").apply(extract_numbers)
    
    return df
