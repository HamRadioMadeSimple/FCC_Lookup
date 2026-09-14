#!/usr/bin/env python3
"""
FCC Lookup Ver 1.65 - Ham Radio Callsign Lookup Tool
Shares ham.db with JS8Map. Default folder on Windows: C:/FCC_DB
Windows build with distance and bearing from a home callsign.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, csv, os, sys, threading, math, json, tempfile, urllib.request, zipfile

APP_NAME = "FCC Lookup"
APP_VERSION = "Ver 1.65"
APP_DISPLAY_NAME = f"{APP_NAME} {APP_VERSION}"
AUTHOR_CALL = "KW3KW"
AUTHOR_CREDIT = f"by {AUTHOR_CALL}"
DEFAULT_DB_DIR = r"C:\FCC_DB"

# ── PyInstaller-safe paths ────────────────────────────────────────────────────
# Bundled assets live in sys._MEIPASS when frozen. User-writable config/logs
# live in %APPDATA%\FCC_Lookup so installed copies under Program Files do not
# lose the selected database path.

def _asset(filename):
    """Path to a bundled asset — works both frozen and in development."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)

def _legacy_writable(filename):
    """Old v1.5 writable path, kept only so existing config can be migrated."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

def _state_dir():
    if os.name == 'nt':
        root = os.environ.get('APPDATA') or os.environ.get('LOCALAPPDATA')
        if root:
            return os.path.join(root, 'FCC_Lookup')
    # Linux/Mint: follow the XDG config location when available.
    root = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(root, 'FCC_Lookup')

def _state_file(filename):
    return os.path.join(_state_dir(), filename)

def _writable(filename):
    """Path for writable files such as config and error logs."""
    return _state_file(filename)

CONFIG_FILE = _state_file("fcc_lookup.cfg")
SETTINGS_FILE = _state_file("fcc_lookup_settings.json")
LEGACY_CONFIG_FILE = _legacy_writable("fcc_lookup.cfg")
FCC_ICON    = _asset("fcc_icon.png")
FCC_ICO     = _asset("FC_launcher_icon.ico")

def load_config():
    # First use the new per-user config. Then fall back to the old same-folder
    # config so installed v1.5 users keep their previous DB folder if possible.
    for cfg in (CONFIG_FILE, LEGACY_CONFIG_FILE):
        if os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    p = f.read().strip().strip('"')
                if p and os.path.isdir(p):
                    return p
            except Exception:
                pass
    return DEFAULT_DB_DIR

def save_config(path):
    try:
        os.makedirs(_state_dir(), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding='utf-8') as f:
            f.write(path)
    except Exception:
        pass

def load_settings():
    defaults = {"home_call": "", "home_call_user_set": False}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                defaults.update(data)
    except Exception:
        pass
    home = str(defaults.get("home_call", "")).strip().upper()
    user_set = bool(defaults.get("home_call_user_set", False))
    # Public build safety: KW3KW is only an author credit, never a Home *default*.
    # Clear it only if it was never chosen by the user (e.g. a stale test file);
    # if the operator deliberately set it, honor it like any other callsign.
    if home == AUTHOR_CALL and not user_set:
        home = ""
        user_set = False
    defaults["home_call"] = home
    defaults["home_call_user_set"] = user_set
    return defaults

def save_settings(settings):
    """Write settings to disk. Returns True on success, False if it could not
    be written (read-only folder, missing APPDATA, etc.) so the caller can say so."""
    try:
        os.makedirs(_state_dir(), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False

BASE_DIR = load_config()
DB_PATH  = os.path.join(BASE_DIR, "ham.db")
CDN_FILE = os.path.join(BASE_DIR, "amateur_delim.txt")
FCC_AM   = os.path.join(BASE_DIR, "AM.dat")
FCC_EN   = os.path.join(BASE_DIR, "EN.dat")

def set_base_dir(path):
    global BASE_DIR, DB_PATH, CDN_FILE, FCC_AM, FCC_EN
    BASE_DIR = path
    DB_PATH  = os.path.join(BASE_DIR, "ham.db")
    CDN_FILE = os.path.join(BASE_DIR, "amateur_delim.txt")
    FCC_AM   = os.path.join(BASE_DIR, "AM.dat")
    FCC_EN   = os.path.join(BASE_DIR, "EN.dat")
    save_config(path)

US_CLASSES = {
    'T':'Technician','G':'General','A':'Amateur Extra',
    'N':'Novice','P':'Advanced (Legacy)',
}

PROVINCE = {
    'BC':(53.7267,-127.6476,'British Columbia'),'AB':(53.9333,-116.5765,'Alberta'),
    'SK':(52.9399,-106.4509,'Saskatchewan'),'MB':(53.7609,-98.8139,'Manitoba'),
    'ON':(51.2538,-85.3232,'Ontario'),'QC':(52.9399,-73.5491,'Quebec'),
    'NB':(46.5653,-66.4619,'New Brunswick'),'NS':(44.6820,-63.7443,'Nova Scotia'),
    'PE':(46.5107,-63.4168,'Prince Edward Island'),'NL':(53.1355,-57.6604,'Newfoundland and Labrador'),
    'YT':(64.2823,-135.0000,'Yukon'),'NT':(64.8255,-124.8457,'Northwest Territories'),
    'NU':(70.2998,-83.1076,'Nunavut'),
}

US_STATE_CENTERS = {
    'AL':(32.8067,-86.7911),'AK':(61.3707,-152.4044),'AZ':(33.7298,-111.4312),'AR':(34.9697,-92.3731),
    'CA':(36.1162,-119.6816),'CO':(39.0598,-105.3111),'CT':(41.5978,-72.7554),'DE':(39.3185,-75.5071),
    'DC':(38.9072,-77.0369),'FL':(27.7663,-81.6868),'GA':(33.0406,-83.6431),'HI':(21.0943,-157.4983),
    'ID':(44.2405,-114.4788),'IL':(40.3495,-88.9861),'IN':(39.8494,-86.2583),'IA':(42.0115,-93.2105),
    'KS':(38.5266,-96.7265),'KY':(37.6681,-84.6701),'LA':(31.1695,-91.8678),'ME':(44.6939,-69.3819),
    'MD':(39.0639,-76.8021),'MA':(42.2302,-71.5301),'MI':(43.3266,-84.5361),'MN':(45.6945,-93.9002),
    'MS':(32.7416,-89.6787),'MO':(38.4561,-92.2884),'MT':(46.9219,-110.4544),'NE':(41.1254,-98.2681),
    'NV':(38.3135,-117.0554),'NH':(43.4525,-71.5639),'NJ':(40.2989,-74.5210),'NM':(34.8405,-106.2485),
    'NY':(42.1657,-74.9481),'NC':(35.6301,-79.8064),'ND':(47.5289,-99.7840),'OH':(40.3888,-82.7649),
    'OK':(35.5653,-96.9289),'OR':(44.5720,-122.0709),'PA':(40.5908,-77.2098),'RI':(41.6809,-71.5118),
    'SC':(33.8569,-80.9450),'SD':(44.2998,-99.4388),'TN':(35.7478,-86.6923),'TX':(31.0545,-97.5635),
    'UT':(40.1500,-111.8624),'VT':(44.0459,-72.7107),'VA':(37.7693,-78.1700),'WA':(47.4009,-121.4905),
    'WV':(38.4912,-80.9545),'WI':(44.2685,-89.6165),'WY':(42.7560,-107.3025),
    'PR':(18.2208,-66.5901),'VI':(18.3358,-64.8963),'GU':(13.4443,144.7937),'AS':(-14.2710,-170.1322),
}

PROVINCE_NAME_TO_CENTER = {name.upper(): (lat, lon) for _abbr, (lat, lon, name) in PROVINCE.items()}
PROVINCE_NAME_TO_CENTER.update({_abbr: (lat, lon) for _abbr, (lat, lon, _name) in PROVINCE.items()})

def center_for_record(country, state):
    st = (state or '').strip().upper()
    if (country or '').upper() == 'CA':
        return PROVINCE_NAME_TO_CENTER.get(st)
    return US_STATE_CENTERS.get(st)

def format_display_name(name):
    """Display FCC names as First Last instead of LAST, FIRST."""
    n = str(name or '').strip()
    if not n:
        return ''
    if ',' in n:
        parts = [p.strip() for p in n.split(',') if p.strip()]
        if len(parts) >= 2:
            last = parts[0]
            first = parts[1]
            suffix = ' '.join(parts[2:]).strip()
            n = f"{first} {last}".strip()
            if suffix:
                n = f"{n}, {suffix}"
    # FCC names often arrive in all caps. Title-case only all-uppercase names.
    if n.isupper():
        n = n.title()
    return n

ZIP_CENTERS_CACHE = None
ZIP_CENTER_FILES = (
    "zip_latlon.csv", "zip_lat_lon.csv", "us_zip_latlon.csv", "uszips.csv",
    "zip_codes.csv", "zip_code_database.csv",
)

# U.S. Census Gazetteer ZCTA file. It provides representative latitude/longitude
# for ZIP Code Tabulation Areas. This is the app's best free zip-to-zip source.
CENSUS_ZCTA_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_zcta_national.zip"
ZIP_CENTER_OUTPUT = "zip_latlon.csv"

def _zip5(value):
    digits = ''.join(ch for ch in str(value or '') if ch.isdigit())
    return digits[:5] if len(digits) >= 5 else ''

def _as_float(value):
    try:
        return float(str(value).strip())
    except Exception:
        return None

def _valid_latlon(lat, lon):
    try:
        lat = float(lat); lon = float(lon)
    except Exception:
        return False
    if abs(lat) < 0.0001 and abs(lon) < 0.0001:
        return False
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0

def _field(row, names):
    lower = {str(k).lower().strip(): v for k, v in row.items()}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return ''

def load_zip_centers():
    """Optional ZIP centroid loader.

    For accurate US zip-to-zip distance, put a CSV in the DB folder or app folder
    named zip_latlon.csv, zip_lat_lon.csv, us_zip_latlon.csv, uszips.csv,
    zip_codes.csv, or zip_code_database.csv.
    Accepted columns include zip/zipcode/zcta and lat/latitude plus lon/lng/longitude.
    """
    global ZIP_CENTERS_CACHE
    if ZIP_CENTERS_CACHE is not None:
        return ZIP_CENTERS_CACHE
    centers = {}
    search_dirs = [BASE_DIR, os.path.dirname(os.path.abspath(__file__)), getattr(sys, '_MEIPASS', '')]
    seen = set()
    for folder in search_dirs:
        if not folder or folder in seen:
            continue
        seen.add(folder)
        for fname in ZIP_CENTER_FILES:
            path = os.path.join(folder, fname)
            if not os.path.exists(path):
                continue
            try:
                with open(path, newline='', encoding='utf-8-sig', errors='replace') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        z = _zip5(_field(row, ('zip', 'zipcode', 'zip_code', 'zcta', 'postal_code')))
                        lat = _as_float(_field(row, ('lat', 'latitude', 'y')))
                        lon = _as_float(_field(row, ('lon', 'lng', 'longitude', 'x')))
                        if z and _valid_latlon(lat, lon):
                            centers[z] = (lat, lon)
            except Exception:
                pass
            if centers:
                ZIP_CENTERS_CACHE = centers
                return centers
    ZIP_CENTERS_CACHE = centers
    return centers

def download_zip_centers(progress_cb, done_cb):
    """Download Census ZCTA centroids and save a compact zip_latlon.csv in BASE_DIR."""
    import urllib.request, zipfile
    global ZIP_CENTERS_CACHE
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        out_csv = os.path.join(BASE_DIR, ZIP_CENTER_OUTPUT)
        tmp_zip = os.path.join(BASE_DIR, "_zcta_centers_download.zip")

        if progress_cb:
            progress_cb(f"Downloading Census ZIP/ZCTA centers to {BASE_DIR} ...")
        urllib.request.urlretrieve(CENSUS_ZCTA_URL, tmp_zip)

        rows_written = 0
        try:
            with zipfile.ZipFile(tmp_zip, 'r') as zf:
                txt_names = [n for n in zf.namelist() if n.lower().endswith(('.txt', '.csv'))]
                if not txt_names:
                    raise RuntimeError("No text file found inside Census ZIP archive")
                name = txt_names[0]
                raw = zf.read(name).decode('utf-8-sig', errors='replace')
        finally:
            try:
                os.remove(tmp_zip)
            except Exception:
                pass

        lines = raw.splitlines()
        if not lines:
            raise RuntimeError("Downloaded Census ZIP file was empty")
        header = lines[0]
        # Census Gazetteer files are normally tab-delimited, but keep this tolerant.
        if '\t' in header:
            delim = '\t'
        elif '|' in header:
            delim = '|'
        elif ',' in header:
            delim = ','
        else:
            delim = None

        with open(out_csv, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['zip', 'lat', 'lon'])
            if delim:
                reader = csv.DictReader(lines, delimiter=delim)
                for row in reader:
                    z = _zip5(_field(row, ('GEOID', 'GEOID_ZCTA5_20', 'ZCTA5', 'ZCTA5CE20', 'zip', 'zipcode', 'zcta')))
                    lat = _as_float(_field(row, ('INTPTLAT', 'INTPTLAT20', 'lat', 'latitude')))
                    lon = _as_float(_field(row, ('INTPTLONG', 'INTPTLON', 'INTPTLON20', 'lon', 'lng', 'longitude')))
                    if z and _valid_latlon(lat, lon):
                        writer.writerow([z, f"{lat:.8f}", f"{lon:.8f}"])
                        rows_written += 1
            else:
                raise RuntimeError("Could not read delimiter in Census ZIP center file")

        if rows_written == 0:
            raise RuntimeError("Downloaded Census file did not contain readable ZIP centers")
        ZIP_CENTERS_CACHE = None
        load_zip_centers()
        done_cb(True, f"Loaded {rows_written:,} ZIP/ZCTA centers into {out_csv}")
    except Exception as e:
        done_cb(False, f"ZIP center download failed: {e}")

def position_for_record(city, state, zip_code, country, lat=None, lon=None):
    """Return (lat, lon, source) for distance/bearing. Source tells how exact it is."""
    country = (country or 'US').upper()
    if _valid_latlon(lat, lon):
        return float(lat), float(lon), 'database lat/lon'

    if country == 'US':
        z = _zip5(zip_code)
        if z:
            centers = load_zip_centers()
            if z in centers:
                lat2, lon2 = centers[z]
                return lat2, lon2, f'ZIP {z} center'
        center = center_for_record('US', state)
        if center:
            return center[0], center[1], 'state center estimate'

    if country == 'CA':
        # Canadian import usually stores lat/lon. If not, use FSA/province fallback.
        postal = str(zip_code or '').strip().upper()
        if postal:
            lat2, lon2 = postal_to_latlon(postal, '')
            if _valid_latlon(lat2, lon2):
                return lat2, lon2, 'postal/FSA center'
        center = center_for_record('CA', state)
        if center:
            return center[0], center[1], 'province center estimate'

    return None, None, 'no position available'

def distance_bearing_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance and initial bearing from point 1 to point 2."""
    r_miles = 3958.7613
    phi1 = math.radians(lat1); phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    miles = r_miles * c

    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    return miles, bearing

def compass_from_bearing(deg):
    dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    return dirs[int((deg + 11.25) // 22.5) % 16]

CITIES = {
    ('VANCOUVER','BC'):(49.2827,-123.1207),('VICTORIA','BC'):(48.4284,-123.3656),
    ('CALGARY','AB'):(51.0447,-114.0719),('EDMONTON','AB'):(53.5461,-113.4938),
    ('SASKATOON','SK'):(52.1332,-106.6700),('REGINA','SK'):(50.4452,-104.6189),
    ('WINNIPEG','MB'):(49.8951,-97.1384),('BRANDON','MB'):(49.8485,-99.9501),
    ('TORONTO','ON'):(43.6532,-79.3832),('OTTAWA','ON'):(45.4215,-75.6972),
    ('MISSISSAUGA','ON'):(43.5890,-79.6441),('HAMILTON','ON'):(43.2557,-79.8711),
    ('LONDON','ON'):(42.9849,-81.2453),('KITCHENER','ON'):(43.4516,-80.4925),
    ('WINDSOR','ON'):(42.3149,-83.0364),('BARRIE','ON'):(44.3894,-79.6903),
    ('KINGSTON','ON'):(44.2312,-76.4860),('THUNDER BAY','ON'):(48.3809,-89.2477),
    ('SUDBURY','ON'):(46.4917,-80.9930),('PETERBOROUGH','ON'):(44.3091,-78.3197),
    ('MONTREAL','QC'):(45.5017,-73.5673),('QUEBEC CITY','QC'):(46.8139,-71.2080),
    ('LAVAL','QC'):(45.5707,-73.7031),('GATINEAU','QC'):(45.4767,-75.7013),
    ('SHERBROOKE','QC'):(45.4041,-71.8929),('SAGUENAY','QC'):(48.4279,-71.0668),
    ('MONCTON','NB'):(46.0878,-64.7782),('SAINT JOHN','NB'):(45.2733,-66.0633),
    ('FREDERICTON','NB'):(45.9636,-66.6431),
    ('HALIFAX','NS'):(44.6488,-63.5752),('DARTMOUTH','NS'):(44.6711,-63.5778),
    ('TRURO','NS'):(45.3648,-63.2561),('SYDNEY','NS'):(46.1351,-60.1831),
    ('CHARLOTTETOWN','PE'):(46.2382,-63.1311),('SUMMERSIDE','PE'):(46.3948,-63.7879),
    ("ST. JOHN'S",'NL'):(47.5556,-52.7453),('CORNER BROOK','NL'):(48.9554,-57.9500),
    ('WHITEHORSE','YT'):(60.7212,-135.0568),('YELLOWKNIFE','NT'):(62.4540,-114.3718),
    ('IQALUIT','NU'):(63.7467,-68.5170),
}

FSA_PREFIX = {
    'V0':(50.0,-125.0),'V1':(50.7,-120.3),'V2':(49.1,-122.4),'V3':(49.2,-122.8),
    'V4':(49.3,-122.9),'V5':(49.2,-123.1),'V6':(49.3,-123.1),'V7':(49.4,-123.0),
    'V8':(48.6,-123.4),'V9':(48.9,-123.7),
    'T0':(52.5,-113.5),'T1':(50.9,-114.0),'T2':(51.1,-114.1),'T3':(51.2,-114.2),
    'T4':(53.5,-113.5),'T5':(53.6,-113.5),'T6':(53.5,-113.4),'T7':(53.2,-113.5),
    'T8':(53.8,-113.6),'T9':(49.7,-112.8),
    'S0':(52.0,-105.5),'S2':(50.6,-104.6),'S3':(50.4,-104.6),'S4':(50.5,-104.5),
    'S6':(52.2,-106.7),'S7':(52.1,-106.6),
    'R0':(50.0,-97.0),'R1':(49.9,-97.3),'R2':(49.8,-97.1),'R3':(49.9,-97.2),
    'R4':(49.8,-97.3),'R5':(49.9,-98.2),'R6':(49.9,-98.5),'R7':(50.0,-99.5),
    'R8':(49.8,-99.9),'R9':(51.0,-100.0),
    'K0':(44.8,-77.0),'K1':(45.4,-75.7),'K2':(45.3,-75.8),'K4':(44.5,-76.3),
    'K6':(44.2,-77.3),'K7':(44.2,-76.5),'K8':(46.5,-80.8),'K9':(46.4,-80.5),
    'L0':(44.0,-79.3),'L1':(43.9,-79.0),'L2':(43.3,-79.8),'L3':(43.5,-79.9),
    'L4':(43.8,-79.5),'L5':(43.6,-79.6),'L6':(43.7,-79.7),'L7':(43.9,-79.4),
    'L8':(43.3,-79.9),'L9':(44.1,-79.6),
    'M1':(43.8,-79.2),'M2':(43.7,-79.4),'M3':(43.7,-79.5),'M4':(43.7,-79.4),
    'M5':(43.6,-79.4),'M6':(43.6,-79.5),'M8':(43.6,-79.5),'M9':(43.7,-79.5),
    'N0':(43.0,-80.8),'N1':(43.4,-80.5),'N2':(43.5,-80.5),'N3':(43.2,-79.9),
    'N4':(42.8,-80.5),'N5':(42.8,-81.2),'N6':(43.0,-81.3),'N7':(43.0,-82.0),
    'N8':(42.3,-83.0),'N9':(42.1,-82.9),
    'P0':(46.5,-82.0),'P1':(46.5,-80.9),'P2':(46.3,-81.0),'P3':(46.4,-80.9),
    'P4':(46.5,-84.3),'P5':(48.0,-85.0),'P6':(46.6,-79.5),'P7':(48.4,-89.2),
    'P8':(46.5,-82.0),'P9':(48.5,-81.3),
    'G0':(47.2,-70.5),'G1':(46.8,-71.2),'G2':(46.8,-71.3),'G3':(46.9,-71.4),
    'G4':(46.9,-71.5),'G5':(46.5,-71.8),'G6':(46.3,-72.4),'G7':(48.4,-71.1),
    'G8':(46.6,-72.8),'G9':(46.4,-72.6),
    'H1':(45.6,-73.6),'H2':(45.5,-73.6),'H3':(45.5,-73.6),'H4':(45.5,-73.7),
    'H7':(45.7,-73.8),'H8':(45.5,-73.9),'H9':(45.4,-73.8),
    'J0':(45.5,-72.5),'J1':(45.4,-71.9),'J2':(45.6,-73.7),'J3':(45.5,-73.4),
    'J4':(45.5,-73.5),'J5':(45.6,-73.5),'J6':(45.6,-74.0),'J7':(45.7,-74.0),
    'J8':(45.5,-75.7),'J9':(45.7,-77.0),
    'E1':(46.1,-64.8),'E2':(45.3,-66.1),'E3':(45.9,-66.6),'E4':(46.0,-65.5),
    'E5':(45.8,-66.5),'E6':(47.0,-65.5),'E7':(47.5,-65.7),'E8':(47.6,-65.7),
    'E9':(47.0,-65.0),
    'B0':(44.5,-64.5),'B1':(46.1,-60.2),'B2':(44.7,-63.6),'B3':(44.5,-64.0),
    'B4':(44.7,-63.7),'B5':(43.8,-66.1),'B6':(45.6,-62.6),'B9':(45.4,-62.5),
    'C0':(46.3,-63.5),'C1':(46.2,-63.1),
    'A0':(47.0,-53.0),'A1':(47.6,-52.7),'A2':(47.0,-55.0),'A5':(48.9,-57.9),
    'A8':(48.9,-54.6),
    'X0':(64.0,-130.0),'X1':(62.5,-114.4),'Y0':(60.7,-135.1),'Y1':(60.7,-135.1),
}

def postal_to_latlon(postal_code, prov):
    p = postal_code.upper().replace(' ','').strip()
    if len(p) >= 2 and p[:2] in FSA_PREFIX:
        return FSA_PREFIX[p[:2]]
    if prov in PROVINCE:
        lat, lon, _ = PROVINCE[prov]
        return lat, lon
    return 0.0, 0.0

def qual_to_class(row):
    if row.get('qual_a') == 'A': return 'Advanced'
    if row.get('qual_b') == 'B': return 'Basic with Honours'
    if row.get('qual_c') == 'C': return 'Basic'
    return 'Amateur'

LAST_DB_ERROR = None

def get_conn():
    return sqlite3.connect(DB_PATH)

def migrate_db(conn, create_indexes=False):
    """Create/upgrade ham.db without doing long table-wide cleanup on the UI thread."""
    conn.execute("""CREATE TABLE IF NOT EXISTS callsigns (
        callsign TEXT PRIMARY KEY, name TEXT, address TEXT,
        city TEXT, state TEXT, zip TEXT, lat REAL, lon REAL,
        class TEXT, country TEXT DEFAULT 'US')""")
    existing = {r[1]: r for r in conn.execute("PRAGMA table_info(callsigns)")}
    needed = {
        'name':    "TEXT",
        'address': "TEXT DEFAULT ''",
        'city':    "TEXT",
        'state':   "TEXT",
        'zip':     "TEXT",
        'lat':     "REAL DEFAULT 0.0",
        'lon':     "REAL DEFAULT 0.0",
        'class':   "TEXT",
        'country': "TEXT DEFAULT 'US'",
    }
    changed = False
    for col, decl in needed.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE callsigns ADD COLUMN {col} {decl}")
            changed = True
    # Index creation can be slow on a large ham.db. Do it during imports/updates,
    # not during the first status refresh after the main screen appears.
    if create_indexes:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_callsign ON callsigns(callsign)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_country_state ON callsigns(country,state)")
    conn.commit()

def ensure_db_ready(create_indexes=False):
    global LAST_DB_ERROR
    LAST_DB_ERROR = None
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = get_conn()
        migrate_db(conn, create_indexes=create_indexes)
        conn.close()
        return True
    except Exception as e:
        LAST_DB_ERROR = str(e)
        try:
            conn.close()
        except Exception:
            pass
        return False

def db_counts():
    global LAST_DB_ERROR
    if not os.path.exists(DB_PATH):
        LAST_DB_ERROR = None
        return 0, 0
    if not ensure_db_ready():
        return 0, 0
    try:
        conn = get_conn()
        us = conn.execute("SELECT COUNT(*) FROM callsigns WHERE CASE WHEN country IS NULL OR TRIM(country)='' THEN 'US' ELSE UPPER(country) END='US'").fetchone()[0]
        ca = conn.execute("SELECT COUNT(*) FROM callsigns WHERE UPPER(COALESCE(country,''))='CA'").fetchone()[0]
        conn.close()
        LAST_DB_ERROR = None
        return us, ca
    except Exception as e:
        LAST_DB_ERROR = str(e)
        try:
            conn.close()
        except Exception:
            pass
        return 0, 0

def lookup_callsign(call):
    if not ensure_db_ready(): return None
    try:
        conn = get_conn()
        c = call.upper().strip()
        row = conn.execute(
            "SELECT name,address,city,state,zip,class,country FROM callsigns WHERE callsign=?",
            (c,)).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT name,address,city,state,zip,class,country FROM callsigns WHERE UPPER(TRIM(callsign))=? LIMIT 1",
                (c,)).fetchone()
        conn.close()
        return row
    except Exception as e:
        global LAST_DB_ERROR
        LAST_DB_ERROR = str(e)
        try:
            conn.close()
        except Exception:
            pass
        return None

def lookup_callsign_full(call):
    if not ensure_db_ready(): return None
    try:
        conn = get_conn()
        c = call.upper().strip()
        row = conn.execute(
            "SELECT callsign,name,address,city,state,zip,lat,lon,class,country FROM callsigns WHERE callsign=?",
            (c,)).fetchone()
        if row is None:
            row = conn.execute(
                "SELECT callsign,name,address,city,state,zip,lat,lon,class,country FROM callsigns WHERE UPPER(TRIM(callsign))=? LIMIT 1",
                (c,)).fetchone()
        conn.close()
        if not row:
            return None
        keys = ('callsign','name','address','city','state','zip','lat','lon','class','country')
        return dict(zip(keys, row))
    except Exception as e:
        global LAST_DB_ERROR
        LAST_DB_ERROR = str(e)
        try:
            conn.close()
        except Exception:
            pass
        return None

def load_fcc(progress_cb, done_cb):
    try:
        conn = get_conn()
        migrate_db(conn, create_indexes=True)
        progress_cb("Reading EN.dat ...")
        ent = {}
        with open(FCC_EN, encoding='latin-1') as f:
            for r in csv.reader(f, delimiter='|'):
                if len(r) >= 18:
                    ent[r[1]] = (r[7], r[15], r[16], r[17], r[18] if len(r)>18 else '')
        progress_cb("Reading AM.dat ...")
        batch = []
        with open(FCC_AM, encoding='latin-1') as f:
            for r in csv.reader(f, delimiter='|'):
                if len(r) >= 6 and r[1] in ent:
                    n,a,c,s,z = ent[r[1]]
                    call = (r[4] or '').strip().upper()
                    if call:
                        batch.append((call,n,a,c,s,z,0.0,0.0,r[5],'US'))
                if len(batch) >= 2000:
                    conn.executemany("INSERT OR REPLACE INTO callsigns (callsign,name,address,city,state,zip,lat,lon,class,country) VALUES (?,?,?,?,?,?,?,?,?,?)", batch)
                    batch.clear()
        if batch:
            conn.executemany("INSERT OR REPLACE INTO callsigns (callsign,name,address,city,state,zip,lat,lon,class,country) VALUES (?,?,?,?,?,?,?,?,?,?)", batch)
        conn.commit(); conn.close()
        done_cb(True, "FCC (US) database loaded successfully.")
    except Exception as e:
        done_cb(False, f"Error loading FCC data:\n{e}")

def load_canadian(progress_cb, done_cb):
    try:
        if not os.path.exists(CDN_FILE):
            done_cb(False, f"Canadian file not found:\n{CDN_FILE}")
            return
        conn = get_conn()
        migrate_db(conn, create_indexes=True)
        progress_cb("Reading Canadian data ...")
        batch, total = [], 0
        with open(CDN_FILE, encoding='utf-8', errors='replace') as f:
            for row in csv.DictReader(f, delimiter=';'):
                call = (row.get('callsign') or '').strip().upper()
                if not call: continue
                first   = (row.get('first_name') or '').strip().title()
                surname = (row.get('surname')    or '').strip().title()
                name    = f"{first} {surname}".strip() or call
                city    = (row.get('city')       or '').strip().title()
                prov    = (row.get('prov_cd')    or '').strip().upper()
                postal  = (row.get('postal_code')or '').strip().upper()
                cls     = qual_to_class(row)
                ck = (city.upper(), prov)
                lat, lon = CITIES[ck] if ck in CITIES else postal_to_latlon(postal, prov)
                pn = PROVINCE.get(prov,(None,None,prov))[2]
                batch.append((call,name,'',city,pn,postal,lat,lon,cls,'CA'))
                if len(batch) >= 500:
                    conn.executemany("INSERT INTO callsigns (callsign,name,address,city,state,zip,lat,lon,class,country) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(callsign) DO UPDATE SET name=excluded.name,city=excluded.city,state=excluded.state,zip=excluded.zip,lat=excluded.lat,lon=excluded.lon,class=excluded.class,country=excluded.country", batch)
                    total += len(batch); batch.clear()
                    progress_cb(f"Imported {total:,} Canadian records ...")
        if batch:
            conn.executemany("INSERT INTO callsigns (callsign,name,address,city,state,zip,lat,lon,class,country) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(callsign) DO UPDATE SET name=excluded.name,city=excluded.city,state=excluded.state,zip=excluded.zip,lat=excluded.lat,lon=excluded.lon,class=excluded.class,country=excluded.country", batch)
            total += len(batch)
        conn.commit(); conn.close()
        done_cb(True, f"Canadian database loaded.\n{total:,} records imported.")
    except Exception as e:
        done_cb(False, f"Error loading Canadian data:\n{e}")

# ── Auto-download URLs ────────────────────────────────────────────────────────
FCC_ZIP_URL = "https://data.fcc.gov/download/pub/uls/complete/l_amat.zip"
CDN_ZIP_URL = "https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip"

def download_and_update_fcc(progress_cb, done_cb):
    """Download FCC complete amateur zip, extract AM.dat & EN.dat, then import."""
    tmp = None
    try:
        os.makedirs(BASE_DIR, exist_ok=True)   # create the selected DB folder if missing
        progress_cb("Connecting to FCC server ...")
        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        tmp.close()

        def reporthook(count, block, total):
            if total > 0:
                mb_done  = count * block / 1_048_576
                mb_total = total / 1_048_576
                progress_cb(f"Downloading FCC data ... {mb_done:.1f} / {mb_total:.1f} MB")
            else:
                progress_cb(f"Downloading FCC data ...")

        urllib.request.urlretrieve(FCC_ZIP_URL, tmp.name, reporthook)
        progress_cb("Extracting AM.dat and EN.dat ...")

        with zipfile.ZipFile(tmp.name, 'r') as z:
            names = z.namelist()
            for target in ('AM.dat', 'EN.dat'):
                match = next((n for n in names if n.upper().endswith(target.upper())), None)
                if match:
                    data = z.read(match)
                    with open(os.path.join(BASE_DIR, target), 'wb') as f:
                        f.write(data)
                else:
                    done_cb(False, f"{target} not found in FCC zip.\nFiles in zip: {names[:10]}")
                    return

        # Now run the normal import
        load_fcc(progress_cb, done_cb)

    except Exception as e:
        done_cb(False, f"FCC auto-update failed:\n{e}")
    finally:
        if tmp and os.path.exists(tmp.name):
            try: os.unlink(tmp.name)
            except Exception: pass


def download_and_update_canadian(progress_cb, done_cb):
    """Download Canadian amateur zip, extract amateur_delim.txt, then import."""
    tmp = None
    try:
        os.makedirs(BASE_DIR, exist_ok=True)   # create the selected DB folder if missing
        progress_cb("Connecting to Industry Canada server ...")
        tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        tmp.close()

        def reporthook(count, block, total):
            if total > 0:
                mb_done  = count * block / 1_048_576
                mb_total = total / 1_048_576
                progress_cb(f"Downloading Canadian data ... {mb_done:.1f} / {mb_total:.1f} MB")
            else:
                progress_cb("Downloading Canadian data ...")

        urllib.request.urlretrieve(CDN_ZIP_URL, tmp.name, reporthook)
        progress_cb("Extracting amateur_delim.txt ...")

        with zipfile.ZipFile(tmp.name, 'r') as z:
            names = z.namelist()
            match = next((n for n in names if 'amateur_delim' in n.lower()), None)
            if match:
                data = z.read(match)
                with open(CDN_FILE, 'wb') as f:
                    f.write(data)
            else:
                done_cb(False, f"amateur_delim.txt not found in zip.\nFiles: {names[:10]}")
                return

        load_canadian(progress_cb, done_cb)

    except Exception as e:
        done_cb(False, f"Canadian auto-update failed:\n{e}")
    finally:
        if tmp and os.path.exists(tmp.name):
            try: os.unlink(tmp.name)
            except Exception: pass


# ── Colours ───────────────────────────────────────────────────────────────────
BG='#1a1a2e'; PANEL='#16213e'; CARD='#0f3460'
ACCENT='#4cc9f0'; CA_CLR='#ff9f43'; RED='#e94560'
TEXT='#eaeaea'; WHITE='#ffffff'
GOLD='#FFD700'; SUBTEXT='#a8a8b3'
BTN_BG='#333366'; BTN_FG='#ffffff'; ENTRY_BG='#0f3460'

# ── App ───────────────────────────────────────────────────────────────────────
class FccLookup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_DISPLAY_NAME)
        self.geometry("760x600")
        self.minsize(700,560)
        self.configure(bg=BG)
        self.resizable(True, True)
        self._busy = False
        self._settings = load_settings()
        self._status_busy = False
        self._status_seq = 0
        self._ham_img = None   # keep reference so GC doesn't destroy it
        self._fcc_img = None
        self._set_icon()
        self._build_menu()
        self._build_ui()
        self.after(200, self._refresh_status_async)

    def _set_icon(self):
        """Set FCC logo as window icon without importing Pillow at startup."""
        try:
            if os.path.exists(FCC_ICON):
                self._fcc_img = tk.PhotoImage(file=FCC_ICON)
                self.iconphoto(True, self._fcc_img)
                return
            if os.path.exists(FCC_ICO):
                self.iconbitmap(FCC_ICO)
        except Exception:
            pass

    def _build_menu(self):
        m = tk.Menu(self)
        dbm = tk.Menu(m, tearoff=False)
        dbm.add_command(label="Select DB Folder...", command=self._browse_db)
        dbm.add_command(label="Select ham.db File...", command=self._browse_db_file)
        dbm.add_separator()
        dbm.add_command(label="Browse Records", command=self._show_browser)
        dbm.add_separator()
        dbm.add_command(label="Update FCC DB", command=self._do_update_fcc)
        dbm.add_command(label="Update Canadian DB", command=self._do_update_canadian)
        dbm.add_command(label="Download / Update ZIP Centers", command=self._do_update_zip_centers)
        dbm.add_separator()
        dbm.add_command(label="Exit", command=self.destroy)
        m.add_cascade(label="Database", menu=dbm)

        hm = tk.Menu(m, tearoff=False)
        hm.add_command(label="About", command=self._show_about)
        m.add_cascade(label="Help", menu=hm)
        self.config(menu=m)

    def _build_ui(self):
        # ── Header - centered ─────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=PANEL, pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text=APP_NAME,
                 font=('Arial',20,'bold'), bg=PANEL, fg=ACCENT).pack()
        tk.Label(hdr, text="USA  &  Canada",
                 font=('Arial',12), bg=PANEL, fg='#a8d8f0').pack()
        tk.Label(hdr, text=AUTHOR_CREDIT,
                 font=('Arial',8), bg=PANEL, fg=SUBTEXT).pack(pady=(1,0))

        # ── DB path bar ───────────────────────────────────────────────────────
        dbbar = tk.Frame(self, bg=PANEL, pady=6)
        dbbar.pack(fill='x')

        tk.Label(dbbar, text="FCC DB:", font=('Arial',11,'bold'),
                 bg=PANEL, fg=GOLD, padx=12).pack(side='left')

        self._db_path_var = tk.StringVar(value=BASE_DIR)
        tk.Label(dbbar, textvariable=self._db_path_var,
                 font=('Courier New',11,'bold'),
                 bg=ENTRY_BG, fg=WHITE,
                 anchor='w', padx=10, pady=4,
                 relief='flat', width=44).pack(side='left', padx=(0,10))

        tk.Button(dbbar, text="Browse...",
                  font=('Arial',9), bg=BTN_BG, fg=BTN_FG,
                  activebackground=ACCENT, activeforeground=BG,
                  relief='flat', padx=10, pady=3,
                  cursor='hand2', command=self._browse_db).pack(side='left')

        # ── Auto-update buttons row ───────────────────────────────────────────
        updbar = tk.Frame(self, bg=PANEL, pady=4)
        updbar.pack(fill='x', padx=12)
        self._upd_btns = []
        b1 = tk.Button(updbar, text="Update FCC DB",
                  font=('Arial',10,'bold'), bg='#1e3a5f', fg=WHITE,
                  activebackground=ACCENT, activeforeground=BG,
                  relief='flat', padx=16, pady=5,
                  cursor='hand2', command=self._do_update_fcc)
        b1.pack(side='left', padx=(0,8))
        self._upd_btns.append(b1)
        b2 = tk.Button(updbar, text="Update Canadian DB",
                  font=('Arial',10,'bold'), bg='#1e3a5f', fg=WHITE,
                  activebackground=ACCENT, activeforeground=BG,
                  relief='flat', padx=16, pady=5,
                  cursor='hand2', command=self._do_update_canadian)
        b2.pack(side='left', padx=(0,8))
        self._upd_btns.append(b2)
        tk.Button(updbar, text="Browse Records",
                  font=('Arial',10,'bold'), bg=BTN_BG, fg=WHITE,
                  activebackground=ACCENT, activeforeground=BG,
                  relief='flat', padx=14, pady=5, cursor='hand2',
                  command=self._show_browser).pack(side='left', padx=(0,8))
        # ── Callsign search bar ───────────────────────────────────────────────
        bar = tk.Frame(self, bg=BG, pady=12)
        bar.pack(fill='x', padx=20)
        tk.Label(bar, text="Callsign:", font=('Arial',11),
                 bg=BG, fg=TEXT).pack(side='left')
        # Entry box with integrated X clear button
        entry_frame = tk.Frame(bar, bg=ENTRY_BG, bd=1, relief='flat')
        entry_frame.pack(side='left', padx=(8,10), ipady=2)

        self._call_var = tk.StringVar()
        self._call_var.trace_add('write', self._force_upper)
        self._entry = tk.Entry(entry_frame, textvariable=self._call_var,
            font=('Courier New',14,'bold'), bg=ENTRY_BG, fg=ACCENT,
            insertbackground=ACCENT, relief='flat', width=10, bd=0)
        self._entry.pack(side='left', padx=(6,0), ipady=4)
        self._entry.bind('<Return>',  lambda e: self._lookup())
        self._entry.bind('<Escape>',  lambda e: self._clear())
        self._entry.focus_set()

        # X button inside the entry frame
        self._clear_btn = tk.Label(entry_frame, text="x", font=('Arial',14,'bold'),
            bg=ENTRY_BG, fg='#ffffff', cursor='hand2', padx=6)
        self._clear_btn.pack(side='left', padx=(2,4))
        self._clear_btn.bind('<Button-1>', lambda e: self._clear())
        self._clear_btn.bind('<Enter>',    lambda e: self._clear_btn.config(fg=RED))
        self._clear_btn.bind('<Leave>',    lambda e: self._clear_btn.config(fg=WHITE))

        tk.Button(bar, text="Look Up", font=('Arial',10,'bold'),
            bg=BTN_BG, fg=BTN_FG, activebackground=ACCENT, activeforeground=BG,
            relief='flat', padx=14, pady=5, cursor='hand2',
            command=self._lookup).pack(side='left')

        tk.Label(bar, text="Home:", font=('Arial',10,'bold'),
                 bg=BG, fg=GOLD).pack(side='left', padx=(18,4))
        self._home_call_var = tk.StringVar(value=self._settings.get('home_call', ''))
        self._home_entry = tk.Entry(bar, textvariable=self._home_call_var,
            font=('Courier New',11,'bold'), bg=ENTRY_BG, fg=GOLD,
            insertbackground=GOLD, relief='flat', width=8, bd=0,
            justify='center')
        self._home_entry.pack(side='left', padx=(0,6), ipady=4)
        self._home_entry.bind('<Return>', lambda e: self._save_home_call())
        tk.Button(bar, text="Set", font=('Arial',9,'bold'),
            bg=BTN_BG, fg=BTN_FG, activebackground=GOLD, activeforeground=BG,
            relief='flat', padx=10, pady=4, cursor='hand2',
            command=self._save_home_call).pack(side='left')

        # ── Result card ───────────────────────────────────────────────────────
        card = tk.Frame(self, bg=CARD, padx=20, pady=16)
        card.pack(fill='both', expand=True, padx=20, pady=(0,10))
        self._country_lbl = tk.Label(card, text="", font=('Arial',11,'bold'),
                                     bg=CARD, fg=ACCENT, anchor='w')
        self._country_lbl.pack(fill='x')
        self._call_lbl = tk.Label(card,
            text="Enter a callsign and press Look Up",
            font=('Arial',20,'bold'), bg=CARD, fg=TEXT, anchor='w')
        self._call_lbl.pack(fill='x', pady=(2,8))
        self._rows = {}
        for label in ('Name','City','Class','Distance','Direction'):
            r = tk.Frame(card, bg=CARD)
            r.pack(fill='x', pady=5)
            # Fixed-width label column plus padding keeps Distance/Direction
            # aligned with Name/City instead of crowding the returned value.
            tk.Label(r, text=f"{label}:", font=('Arial',12,'bold'), bg=CARD,
                     fg='#c8d0e0', width=10, anchor='w').pack(side='left', padx=(0,8))
            v = tk.Label(r, text="", font=('Arial',13,'bold'), bg=CARD,
                         fg=WHITE, anchor='w', wraplength=430, justify='left')
            v.pack(side='left', fill='x', expand=True)
            self._rows[label] = v

        # ── Status bar ────────────────────────────────────────────────────────
        status_frame = tk.Frame(self, bg=PANEL)
        status_frame.pack(fill='x', side='bottom')
        self._status_var = tk.StringVar(value="Checking database...")
        tk.Label(status_frame, textvariable=self._status_var, font=('Arial',8),
                 bg=PANEL, fg=SUBTEXT, anchor='w', padx=10, pady=4).pack(side='left', fill='x', expand=True)
        tk.Label(status_frame, text=APP_DISPLAY_NAME,
                 font=('Arial',8), bg=PANEL, fg='#555577',
                 anchor='e', padx=10, pady=4).pack(side='right')

        # Progress bar — pack then immediately hide
        self._prog = ttk.Progressbar(self, mode='indeterminate')
        self._prog.pack(fill='x', side='bottom')
        self._prog.pack_forget()

    # ── Browse ────────────────────────────────────────────────────────────────
    def _browse_db(self):
        chosen = filedialog.askdirectory(
            title="Select FCC DB Folder (containing ham.db)",
            initialdir=BASE_DIR if os.path.isdir(BASE_DIR) else os.path.expanduser("~"))
        if chosen:
            chosen = os.path.normpath(chosen)
            set_base_dir(chosen)
            self._db_path_var.set(chosen)
            self._refresh_status_async()

    def _browse_db_file(self):
        chosen = filedialog.askopenfilename(
            title="Select ham.db",
            initialdir=BASE_DIR if os.path.isdir(BASE_DIR) else os.path.expanduser("~"),
            filetypes=[("ham.db", "ham.db"), ("SQLite database", "*.db"), ("All files", "*.*")])
        if chosen:
            folder = os.path.dirname(os.path.abspath(chosen))
            set_base_dir(folder)
            self._db_path_var.set(folder)
            self._refresh_status_async()

    def _require_db(self):
        if not os.path.exists(DB_PATH):
            messagebox.showerror("Database Not Found",
                f"ham.db was not found in:\n{BASE_DIR}\n\nUse Browse to select the folder that contains ham.db, or run Update FCC DB.")
            return False
        if not ensure_db_ready():
            messagebox.showerror("Database Error",
                f"The database exists but could not be opened/upgraded:\n{DB_PATH}\n\n{LAST_DB_ERROR or 'Unknown error'}")
            return False
        return True

    # ── Home / distance helpers ─────────────────────────────────────────────────
    def _save_home_call(self):
        call = self._home_call_var.get().strip().upper()
        self._home_call_var.set(call)
        self._settings['home_call'] = call
        self._settings['home_call_user_set'] = bool(call)
        ok = save_settings(self._settings)
        if not ok:
            self._status_var.set(
                f"  Home set to {call} for this session only - could not write {SETTINGS_FILE}"
                if call else
                f"  Home cleared for this session only - could not write {SETTINGS_FILE}")
        elif call:
            self._status_var.set(f"  Home callsign set to {call}")
        else:
            self._status_var.set("  Home callsign cleared")
        # Recalculate current result, if one is displayed.
        current = self._call_var.get().strip().upper()
        if current:
            self._lookup()

    def _get_home_position(self):
        call = self._home_call_var.get().strip().upper() if hasattr(self, '_home_call_var') else self._settings.get('home_call', '')
        if not call:
            return None, None, None, 'no home callsign set'
        row = lookup_callsign_full(call)
        if not row:
            return None, None, call, 'home callsign not found in ham.db'
        lat, lon, source = position_for_record(row.get('city'), row.get('state'), row.get('zip'), row.get('country'), row.get('lat'), row.get('lon'))
        if lat is None or lon is None:
            return None, None, call, source
        return lat, lon, call, source

    def _distance_text_for_record(self, city, state, zip_code, country, lat, lon):
        hlat, hlon, hcall, hsrc = self._get_home_position()
        if hlat is None or hlon is None:
            return '', '', f"Set Home callsign first ({hsrc})."
        tlat, tlon, tsrc = position_for_record(city, state, zip_code, country, lat, lon)
        if tlat is None or tlon is None:
            return '', '', f"No target position available ({tsrc})."
        miles, bearing = distance_bearing_miles(hlat, hlon, tlat, tlon)
        km = miles * 1.609344
        direction = compass_from_bearing(bearing)
        distance_text = f"{miles:,.0f} M / {km:,.0f} KM"
        direction_text = f"{direction} ({bearing:03.0f}°)"
        return distance_text, direction_text, ''

    # ── Lookup ────────────────────────────────────────────────────────────────
    def _force_upper(self, *args):
        val = self._call_var.get()
        upper = val.upper()
        if val != upper:
            self._call_var.set(upper)

    def _clear(self):
        self._call_var.set('')
        self._country_lbl.config(text="", fg=ACCENT)
        self._call_lbl.config(text="Enter a callsign and press Look Up", fg=TEXT)
        for k in ('Name','City','Class','Distance','Direction'):
            self._rows[k].config(text="")
        self._entry.focus_set()

    def _lookup(self):
        call = self._call_var.get().strip().upper()
        if not call: return
        if not os.path.exists(DB_PATH):
            self._country_lbl.config(text="No database found", fg=RED)
            self._call_lbl.config(text="", fg=TEXT)
            self._rows['Name'].config(
                text=f"ham.db not found in {BASE_DIR} -- use Browse to select the correct folder or run Update FCC DB.")
            for k in ('City','Class','Distance','Direction'): self._rows[k].config(text="")
            return
        row = lookup_callsign_full(call)
        if row:
            name  = row.get('name')
            city  = row.get('city')
            state = row.get('state')
            zip_  = row.get('zip')
            cls   = row.get('class')
            country = row.get('country') or 'US'
            lat = row.get('lat')
            lon = row.get('lon')
            if country == 'CA':
                clr,ctry,cls_disp = CA_CLR,"[CA]  Canada",cls or 'Amateur'
            else:
                clr,ctry = ACCENT,"[US]  United States"
                cls_disp = US_CLASSES.get(cls, cls or 'Unknown')
            self._country_lbl.config(text=ctry, fg=clr)
            self._call_lbl.config(text=call, fg=clr)
            loc = f"{city}, {state}  {zip_}".strip().strip(',').strip()
            self._rows['Name'].config(text=format_display_name(name) or '--')
            self._rows['City'].config(text=loc or '--')
            self._rows['Class'].config(text=cls_disp)
            dist_text, dir_text, detail = self._distance_text_for_record(city, state, zip_, country, lat, lon)
            if detail:
                self._rows['Distance'].config(text=detail)
                self._rows['Direction'].config(text='')
            else:
                self._rows['Distance'].config(text=dist_text or '--')
                self._rows['Direction'].config(text=dir_text or '--')
        else:
            self._country_lbl.config(text="", fg=TEXT)
            self._call_lbl.config(text=call, fg=RED)
            self._rows['Name'].config(text=f"'{call}' was not found in the database.")
            for k in ('City','Class','Distance','Direction'): self._rows[k].config(text="")

    # ── Database browser / map ─────────────────────────────────────────────────
    def _show_browser(self):
        if not self._require_db():
            return

        win = tk.Toplevel(self)
        win.title("Browse ham.db Records")
        win.geometry("980x620")
        win.minsize(820,480)
        win.configure(bg=BG)
        try: win.transient(self)
        except Exception: pass

        top = tk.Frame(win, bg=PANEL, padx=10, pady=8)
        top.pack(fill='x')
        tk.Label(top, text="Search:", font=('Arial',10,'bold'), bg=PANEL, fg=TEXT).pack(side='left')
        qvar = tk.StringVar()
        ent = tk.Entry(top, textvariable=qvar, font=('Courier New',11), bg=ENTRY_BG, fg=WHITE,
                       insertbackground=ACCENT, relief='flat', width=28)
        ent.pack(side='left', padx=(6,10), ipady=3)
        tk.Label(top, text="Country:", font=('Arial',10,'bold'), bg=PANEL, fg=TEXT).pack(side='left')
        cvar = tk.StringVar(value='ALL')
        combo = ttk.Combobox(top, textvariable=cvar, values=['ALL','US','CA'], width=5, state='readonly')
        combo.pack(side='left', padx=(6,10))
        status = tk.StringVar(value="")
        tk.Button(top, text="Refresh", font=('Arial',9,'bold'), bg=BTN_BG, fg=WHITE, relief='flat',
                  padx=12, pady=4, command=lambda: refresh()).pack(side='left', padx=(0,8))
        tk.Button(top, text="Use Selected", font=('Arial',9,'bold'), bg=BTN_BG, fg=WHITE, relief='flat',
                  padx=12, pady=4, command=lambda: use_selected()).pack(side='left')

        cols = ('Callsign','Name','City','State','Zip','Class','Country','Miles','Bearing')
        frame = tk.Frame(win, bg=BG, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=18)
        vsb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        widths = {'Callsign':100,'Name':220,'City':145,'State':110,'Zip':85,'Class':110,'Country':70,'Miles':80,'Bearing':90}
        for col in cols:
            tree.heading(col, text=col, command=lambda c=col: sort_tree(c, False))
            tree.column(col, width=widths.get(col,120), anchor='w')
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(win, textvariable=status, font=('Arial',9), bg=PANEL, fg=SUBTEXT,
                 anchor='w', padx=10, pady=4).pack(fill='x', side='bottom')

        def query_rows():
            where, params = [], []
            if cvar.get() != 'ALL':
                where.append("UPPER(COALESCE(country,'US'))=?")
                params.append(cvar.get())
            q = qvar.get().strip().upper()
            if q:
                like = f"%{q}%"
                where.append("(UPPER(callsign) LIKE ? OR UPPER(COALESCE(name,'')) LIKE ? OR UPPER(COALESCE(city,'')) LIKE ? OR UPPER(COALESCE(state,'')) LIKE ?)")
                params.extend([like, like, like, like])
            sql = "SELECT callsign,name,city,state,zip,class,country,lat,lon FROM callsigns"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY callsign LIMIT 1000"
            conn = get_conn()
            rows = conn.execute(sql, params).fetchall()
            conn.close()
            return rows

        def refresh():
            if not self._require_db(): return
            for item in tree.get_children():
                tree.delete(item)
            try:
                rows = query_rows()
                for r in rows:
                    call,name,city,state,zip_,cls,country,lat,lon = r
                    miles_txt, bear_txt, _detail = self._distance_text_for_record(city, state, zip_, country, lat, lon)
                    vals = (call,format_display_name(name),city,state,zip_,cls,country,miles_txt,bear_txt)
                    tree.insert('', 'end', values=tuple('' if v is None else v for v in vals))
                suffix = "  (limited to first 1,000 matches)" if len(rows) >= 1000 else ""
                status.set(f"Showing {len(rows):,} records from {DB_PATH}{suffix}")
            except Exception as e:
                status.set(f"Browse error: {e}")

        def sort_tree(col, reverse):
            data = [(tree.set(k, col), k) for k in tree.get_children('')]
            data.sort(key=lambda x: x[0], reverse=reverse)
            for index, (_val, k) in enumerate(data):
                tree.move(k, '', index)
            tree.heading(col, command=lambda: sort_tree(col, not reverse))

        def use_selected():
            item = tree.focus()
            if not item: return
            vals = tree.item(item, 'values')
            if vals:
                self._call_var.set(str(vals[0]).upper())
                self._lookup()
                self.lift()

        ent.bind('<Return>', lambda e: refresh())
        tree.bind('<Double-1>', lambda e: use_selected())
        refresh()
        ent.focus_set()

    # ── DB loaders ────────────────────────────────────────────────────────────
    def _do_update_zip_centers(self):
        if self._busy: return
        if messagebox.askyesno("Download ZIP Centers",
                "Download U.S. Census ZIP/ZCTA center points?\n\n"
                "This makes the Distance row use ZIP-to-ZIP centers instead of state-center estimates.\n"
                "The file will be saved as zip_latlon.csv in your FCC DB folder.\n\nContinue?"):
            self._run_in_thread(download_zip_centers)

    def _do_update_fcc(self):
        if self._busy: return
        if messagebox.askyesno("Update FCC DB",
                "Download the latest FCC amateur database\nfrom fcc.gov and import it?\n\n"
                "This may take several minutes.\nContinue?"):
            self._run_in_thread(download_and_update_fcc)

    def _do_update_canadian(self):
        if self._busy: return
        if messagebox.askyesno("Update Canadian DB",
                "Download the latest Canadian amateur database\n"
                "from Industry Canada and import it?\n\n"
                "This may take a few minutes.\nContinue?"):
            self._run_in_thread(download_and_update_canadian)

    def _do_load_fcc(self):
        if self._busy: return
        if not os.path.exists(FCC_AM) or not os.path.exists(FCC_EN):
            messagebox.showerror("Files Not Found",
                f"AM.dat and EN.dat must be in:\n{BASE_DIR}\n\n"
                "Download from fcc.gov/uls > Amateur > Weekly.")
            return
        if messagebox.askyesno("Load FCC Data",
                f"Import AM.dat and EN.dat from:\n{BASE_DIR}\n\n"
                "Replaces existing US records.\nTakes 1-2 minutes. Continue?"):
            self._run_in_thread(load_fcc)

    def _do_load_canadian(self):
        if self._busy: return
        if messagebox.askyesno("Load Canadian Data",
                f"Import:\n{CDN_FILE}\n\nReplaces existing Canadian records.\n\nContinue?"):
            self._run_in_thread(load_canadian)

    def _do_load_both(self):
        if self._busy: return
        if not messagebox.askyesno("Reload Both",
                "Reload FCC (US) then Canadian?\nTakes a few minutes.\n\nContinue?"): return
        def after_fcc(ok, msg):
            if ok: self._run_in_thread(load_canadian)
            else:  self._finish_load(ok, msg)
        self._run_in_thread(load_fcc, done_override=after_fcc)

    def _run_in_thread(self, fn, done_override=None):
        self._busy = True
        self.config(cursor='watch')
        for btn in self._upd_btns:
            btn.config(state='disabled', cursor='watch')
        self._prog.pack(fill='x', side='bottom')
        self._prog.start(10)
        done_cb = done_override or self._finish_load
        def worker():
            fn(progress_cb=lambda m: self.after(0, lambda msg=m: self._status_var.set(msg)),
               done_cb=lambda ok,m: self.after(0, lambda o=ok,msg=m: done_cb(o,msg)))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_load(self, ok, msg):
        self._prog.stop()
        self._prog.pack_forget()
        self._busy = False
        self.config(cursor='')
        for btn in self._upd_btns:
            btn.config(state='normal', cursor='hand2')
        self._refresh_status()
        if ok: messagebox.showinfo("Done", msg)
        else:  messagebox.showerror("Error", msg)

    def _refresh_status_async(self):
        """Refresh database status without freezing the Tk main thread."""
        if self._status_busy:
            self._status_seq += 1
            return
        self._status_busy = True
        self._status_seq += 1
        seq = self._status_seq
        self._status_var.set(f"  Checking database... ({DB_PATH})")

        def worker():
            us, ca = db_counts()
            err = LAST_DB_ERROR
            exists = os.path.exists(DB_PATH)
            base = BASE_DIR
            dbp = DB_PATH
            self.after(0, lambda: self._apply_status(seq, us, ca, err, exists, base, dbp))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_status(self, seq, us, ca, err, exists, base, dbp):
        self._status_busy = False
        if seq != self._status_seq:
            self._refresh_status_async()
            return
        if err:
            self._status_var.set(f"  Database error in {dbp}: {err}")
        elif us == 0 and ca == 0:
            if exists:
                self._status_var.set(f"  ham.db found but no records counted in {base} -- try Update FCC DB.")
            else:
                self._status_var.set(f"  No ham.db found in {base} -- use Browse or Update FCC DB.")
        else:
            parts = []
            if us: parts.append(f"US: {us:,} records")
            if ca: parts.append(f"CA: {ca:,} records")
            self._status_var.set("  " + "   |   ".join(parts) + f"   -- Ready   ({dbp})")

    def _refresh_status(self):
        # Backward-compatible wrapper for any old callbacks.
        self._refresh_status_async()

    def _show_about(self):
        messagebox.showinfo("About FCC Lookup",
            f"{APP_DISPLAY_NAME}\n\n"
            "Offline callsign lookup for USA and Canada.\n"
            "Shares ham.db with JS8Map.\n"
            "Includes callsign lookup, database browsing, ZIP-center download, and distance/bearing from Home callsign.\n\n"
            "US data:   fcc.gov/uls\n"
            "CA data:   apc-cap.ic.gc.ca/datafiles/amateur_delim.zip\n\n"
            f"Created by {AUTHOR_CALL}")

if __name__ == '__main__':
    try:
        app = FccLookup()
        app.mainloop()
    except Exception as e:
        import traceback
        log = _writable("error_log.txt")
        try:
            with open(log, "w") as f:
                traceback.print_exc(file=f)
        except Exception:
            pass
        raise
