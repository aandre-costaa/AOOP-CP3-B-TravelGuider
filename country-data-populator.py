import os
import json
import time
import requests

# ──────────────────────────────────────────────────────────────────────────────
# 1) Configuration
# ──────────────────────────────────────────────────────────────────────────────

API_KEY = "25787596bb944d40991b94233c5cb118"  # ← Replace with your actual Geoapify API key

# Output folder for JSON files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Radius (in meters) around each capital to fetch POIs; adjust as needed
RADIUS_METERS = 100000  # 100 km

# List of countries with their capital’s coordinates.
# “popular” flag indicates a higher limit for most-visited countries.
COUNTRIES = [
    {"name": "Afghanistan",         "lat": 34.5553,   "lon": 69.2075,    "popular": False},  # Kabul
    {"name": "Albania",             "lat": 41.3275,   "lon": 19.8187,    "popular": False},  # Tirana
    {"name": "Algeria",             "lat": 36.7538,   "lon": 3.0588,     "popular": False},  # Algiers
    {"name": "Andorra",             "lat": 42.5462,   "lon": 1.6016,     "popular": False},  # Andorra la Vella
    {"name": "Angola",              "lat": -8.8390,   "lon": 13.2894,    "popular": False},  # Luanda
    {"name": "Argentina",           "lat": -34.6037,  "lon": -58.3816,   "popular": True},   # Buenos Aires
    {"name": "Armenia",             "lat": 40.1792,   "lon": 44.4991,    "popular": False},  # Yerevan
    {"name": "Australia",           "lat": -35.2809,  "lon": 149.1300,   "popular": True},   # Canberra
    {"name": "Austria",             "lat": 48.2082,   "lon": 16.3738,    "popular": True},   # Vienna
    {"name": "Azerbaijan",          "lat": 40.4093,   "lon": 49.8671,    "popular": False},  # Baku
    {"name": "Bahamas",             "lat": 25.0343,   "lon": -77.3963,   "popular": False},  # Nassau
    {"name": "Bahrain",             "lat": 26.2235,   "lon": 50.5876,    "popular": False},  # Manama
    {"name": "Bangladesh",          "lat": 23.8103,   "lon": 90.4125,    "popular": False},  # Dhaka
    {"name": "Belarus",             "lat": 53.9045,   "lon": 27.5615,    "popular": False},  # Minsk
    {"name": "Belgium",             "lat": 50.8503,   "lon": 4.3517,     "popular": True},   # Brussels
    {"name": "Belize",              "lat": 17.1899,   "lon": -88.4976,   "popular": False},  # Belmopan
    {"name": "Benin",               "lat": 6.3690,    "lon": 2.6323,     "popular": False},  # Porto-Novo
    {"name": "Bhutan",              "lat": 27.4728,   "lon": 89.6390,    "popular": False},  # Thimphu
    {"name": "Bolivia",             "lat": -16.4897,  "lon": -68.1193,   "popular": False},  # La Paz
    {"name": "Bosnia_and_Herzegovina","lat": 43.8563,"lon": 18.4131,    "popular": False},  # Sarajevo
    {"name": "Botswana",            "lat": -24.6282,  "lon": 25.9231,    "popular": False},  # Gaborone
    {"name": "Brazil",              "lat": -15.7939,  "lon": -47.8828,   "popular": True},   # Brasília
    {"name": "Brunei",              "lat": 4.9031,    "lon": 114.9398,   "popular": False},  # Bandar Seri Begawan
    {"name": "Bulgaria",            "lat": 42.6977,   "lon": 23.3219,    "popular": False},  # Sofia
    {"name": "Burkina_Faso",        "lat": 12.3714,   "lon": -1.5197,    "popular": False},  # Ouagadougou
    {"name": "Burundi",             "lat": -3.3822,   "lon": 29.3644,    "popular": False},  # Gitega
    {"name": "Cambodia",            "lat": 11.5564,   "lon": 104.9282,   "popular": False},  # Phnom Penh
    {"name": "Cameroon",            "lat": 3.8480,    "lon": 11.5021,    "popular": False},  # Yaoundé
    {"name": "Canada",              "lat": 45.4215,   "lon": -75.6972,   "popular": True},   # Ottawa
    {"name": "Cape_Verde",          "lat": 14.9330,   "lon": -23.5133,   "popular": False},  # Praia
    {"name": "Central_African_Republic","lat":4.3947,"lon":18.5582, "popular": False},  # Bangui
    {"name": "Chad",                "lat": 12.1348,   "lon": 15.0557,    "popular": False},  # N'Djamena
    {"name": "Chile",               "lat": -33.4489,  "lon": -70.6693,   "popular": True},   # Santiago
    {"name": "China",               "lat": 39.9042,   "lon": 116.4074,   "popular": True},   # Beijing
    {"name": "Colombia",            "lat": 4.7110,    "lon": -74.0721,   "popular": True},   # Bogotá
    {"name": "Comoros",             "lat": -11.7172,  "lon": 43.2473,    "popular": False},  # Moroni
    {"name": "Costa_Rica",          "lat": 9.7489,    "lon": -83.7534,   "popular": False},  # San José
    {"name": "Croatia",             "lat": 45.8150,   "lon": 15.9819,    "popular": False},  # Zagreb
    {"name": "Cuba",                "lat": 23.1136,   "lon": -82.3666,   "popular": False},  # Havana
    {"name": "Cyprus",              "lat": 35.1856,   "lon": 33.3823,    "popular": False},  # Nicosia
    {"name": "Czech_Republic",      "lat": 50.0755,   "lon": 14.4378,    "popular": False},  # Prague
    {"name": "Democratic_Republic_of_the_Congo","lat":-4.4419,"lon":15.2663,"popular":False},  # Kinshasa
    {"name": "Denmark",             "lat": 55.6761,   "lon": 12.5683,    "popular": False},  # Copenhagen
    {"name": "Djibouti",            "lat": 11.8251,   "lon": 42.5903,    "popular": False},  # Djibouti (city)
    {"name": "Dominica",            "lat": 15.3092,   "lon": -61.3794,   "popular": False},  # Roseau
    {"name": "Dominican_Republic",  "lat": 18.4861,   "lon": -69.9312,   "popular": False},  # Santo Domingo
    {"name": "Ecuador",             "lat": -0.1807,   "lon": -78.4678,   "popular": False},  # Quito
    {"name": "Egypt",               "lat": 30.0444,   "lon": 31.2357,    "popular": True},   # Cairo
    {"name": "El_Salvador",         "lat": 13.6929,   "lon": -89.2182,   "popular": False},  # San Salvador
    {"name": "Equatorial_Guinea",   "lat": 3.7504,    "lon": 8.7835,     "popular": False},  # Malabo
    {"name": "Eritrea",             "lat": 15.3229,   "lon": 38.9251,    "popular": False},  # Asmara
    {"name": "Estonia",             "lat": 59.4370,   "lon": 24.7536,    "popular": False},  # Tallinn
    {"name": "Eswatini",            "lat": -26.3054,  "lon": 31.1367,    "popular": False},  # Mbabane
    {"name": "Ethiopia",            "lat": 8.9806,    "lon": 38.7578,    "popular": False},  # Addis Ababa
    {"name": "Fiji",                "lat": -17.7134,  "lon": 178.0650,   "popular": False},  # Suva
    {"name": "Finland",             "lat": 60.1699,   "lon": 24.9384,    "popular": False},  # Helsinki
    {"name": "France",              "lat": 48.8566,   "lon": 2.3522,     "popular": True},   # Paris
    {"name": "Gabon",               "lat": -0.8037,   "lon": 11.6094,    "popular": False},  # Libreville
    {"name": "Gambia",              "lat": 13.4549,   "lon": -16.5790,   "popular": False},  # Banjul
    {"name": "Georgia",             "lat": 41.7151,   "lon": 44.8271,    "popular": False},  # Tbilisi
    {"name": "Germany",             "lat": 52.5200,   "lon": 13.4050,    "popular": True},   # Berlin
    {"name": "Ghana",               "lat": 5.6037,    "lon": -0.1870,    "popular": False},  # Accra
    {"name": "Greece",              "lat": 37.9838,   "lon": 23.7275,    "popular": True},   # Athens
    {"name": "Grenada",             "lat": 12.0561,   "lon": -61.7488,   "popular": False},  # St. George's
    {"name": "Guatemala",           "lat": 14.6349,   "lon": -90.5069,   "popular": False},  # Guatemala City
    {"name": "Guinea",              "lat": 9.6412,    "lon": -13.5784,   "popular": False},  # Conakry
    {"name": "Guinea-Bissau",       "lat": 11.8636,   "lon": -15.5977,   "popular": False},  # Bissau
    {"name": "Guyana",              "lat": 6.8013,    "lon": -58.1551,   "popular": False},  # Georgetown
    {"name": "Haiti",               "lat": 18.5944,   "lon": -72.3074,   "popular": False},  # Port-au-Prince
    {"name": "Honduras",            "lat": 14.0723,   "lon": -87.1921,   "popular": False},  # Tegucigalpa
    {"name": "Hungary",             "lat": 47.4979,   "lon": 19.0402,    "popular": False},  # Budapest
    {"name": "Iceland",             "lat": 64.1265,   "lon": -21.8174,   "popular": False},  # Reykjavik
    {"name": "India",               "lat": 28.6139,   "lon": 77.2090,    "popular": True},   # New Delhi
    {"name": "Indonesia",           "lat": -6.2088,   "lon": 106.8456,   "popular": True},   # Jakarta
    {"name": "Iran",                "lat": 35.6892,   "lon": 51.3890,    "popular": False},  # Tehran
    {"name": "Iraq",                "lat": 33.3152,   "lon": 44.3661,    "popular": False},  # Baghdad
    {"name": "Ireland",             "lat": 53.3498,   "lon": -6.2603,    "popular": False},  # Dublin
    {"name": "Israel",              "lat": 31.7683,   "lon": 35.2137,    "popular": False},  # Jerusalem
    {"name": "Italy",               "lat": 41.9028,   "lon": 12.4964,    "popular": True},   # Rome
    {"name": "Jamaica",             "lat": 18.1096,   "lon": -77.2975,   "popular": False},  # Kingston
    {"name": "Japan",               "lat": 35.6895,   "lon": 139.6917,   "popular": True},   # Tokyo
    {"name": "Jordan",              "lat": 31.9454,   "lon": 35.9284,    "popular": False},  # Amman
    {"name": "Kazakhstan",          "lat": 51.1605,   "lon": 71.4704,    "popular": False},  # Nur-Sultan
    {"name": "Kenya",               "lat": -1.2864,   "lon": 36.8172,    "popular": False},  # Nairobi
    {"name": "Kiribati",            "lat": 1.4518,    "lon": 172.9716,   "popular": False},  # South Tarawa
    {"name": "Kosovo",              "lat": 42.6629,   "lon": 21.1655,    "popular": False},  # Pristina
    {"name": "Kuwait",              "lat": 29.3759,   "lon": 47.9774,    "popular": False},  # Kuwait City
    {"name": "Kyrgyzstan",          "lat": 42.8746,   "lon": 74.5698,    "popular": False},  # Bishkek
    {"name": "Laos",                "lat": 17.9757,   "lon": 102.6331,   "popular": False},  # Vientiane
    {"name": "Latvia",              "lat": 56.9496,   "lon": 24.1052,    "popular": False},  # Riga
    {"name": "Lebanon",             "lat": 33.8547,   "lon": 35.8623,    "popular": False},  # Beirut
    {"name": "Lesotho",             "lat": -29.3158,  "lon": 27.4860,    "popular": False},  # Maseru
    {"name": "Liberia",             "lat": 6.2907,    "lon": -10.7605,   "popular": False},  # Monrovia
    {"name": "Libya",               "lat": 32.8872,   "lon": 13.1913,    "popular": False},  # Tripoli
    {"name": "Liechtenstein",       "lat": 47.1660,   "lon": 9.5554,     "popular": False},  # Vaduz
    {"name": "Lithuania",           "lat": 54.6872,   "lon": 25.2797,    "popular": False},  # Vilnius
    {"name": "Luxembourg",          "lat": 49.6116,   "lon": 6.1319,     "popular": False},  # Luxembourg City
    {"name": "Madagascar",          "lat": -18.8792,  "lon": 47.5079,    "popular": False},  # Antananarivo
    {"name": "Malawi",              "lat": -13.9626,  "lon": 33.7741,    "popular": False},  # Lilongwe
    {"name": "Malaysia",            "lat": 3.1390,    "lon": 101.6869,   "popular": True},   # Kuala Lumpur
    {"name": "Maldives",            "lat": 4.1755,    "lon": 73.5093,    "popular": False},  # Malé
    {"name": "Mali",                "lat": 12.6392,   "lon": -8.0029,    "popular": False},  # Bamako
    {"name": "Malta",               "lat": 35.9375,   "lon": 14.3754,    "popular": False},  # Valletta
    {"name": "Mauritania",          "lat": 18.0735,   "lon": -15.9650,   "popular": False},  # Nouakchott
    {"name": "Mauritius",           "lat": -20.3484,  "lon": 57.5522,    "popular": False},  # Port Louis
    {"name": "Mexico",              "lat": 19.4326,   "lon": -99.1332,   "popular": True},   # Mexico City
    {"name": "Micronesia",          "lat": 6.9147,    "lon": 158.1610,   "popular": False},  # Palikir
    {"name": "Moldova",             "lat": 47.0105,   "lon": 28.8638,    "popular": False},  # Chișinău
    {"name": "Monaco",              "lat": 43.7384,   "lon": 7.4246,     "popular": False},  # Monaco (city)
    {"name": "Mongolia",            "lat": 47.9212,   "lon": 106.9186,   "popular": False},  # Ulaanbaatar
    {"name": "Montenegro",          "lat": 42.4304,   "lon": 19.2594,    "popular": False},  # Podgorica
    {"name": "Morocco",             "lat": 33.9716,   "lon": -6.8498,    "popular": False},  # Rabat
    {"name": "Mozambique",          "lat": -25.9655,  "lon": 32.5892,    "popular": False},  # Maputo
    {"name": "Myanmar",             "lat": 16.8409,   "lon": 96.1735,    "popular": False},  # Naypyidaw
    {"name": "Namibia",             "lat": -22.5609,  "lon": 17.0658,    "popular": False},  # Windhoek
    {"name": "Nepal",               "lat": 27.7172,   "lon": 85.3240,    "popular": False},  # Kathmandu
    {"name": "Netherlands",         "lat": 52.3676,   "lon": 4.9041,     "popular": True},   # Amsterdam
    {"name": "New_Zealand",         "lat": -41.2865,  "lon": 174.7762,   "popular": False},  # Wellington
    {"name": "Nicaragua",           "lat": 12.1364,   "lon": -86.2514,   "popular": False},  # Managua
    {"name": "Niger",               "lat": 13.5128,   "lon": 2.1127,     "popular": False},  # Niamey
    {"name": "Nigeria",             "lat": 9.0765,    "lon": 7.3986,     "popular": False},  # Abuja
    {"name": "North_Macedonia",     "lat": 41.9973,   "lon": 21.4280,    "popular": False},  # Skopje
    {"name": "Norway",              "lat": 59.9139,   "lon": 10.7522,    "popular": False},  # Oslo
    {"name": "Oman",                "lat": 23.5859,   "lon": 58.4059,    "popular": False},  # Muscat
    {"name": "Pakistan",            "lat": 33.6844,   "lon": 73.0479,    "popular": False},  # Islamabad
    {"name": "Panama",              "lat": 8.9833,    "lon": -79.5167,   "popular": False},  # Panama City
    {"name": "Papua_New_Guinea",    "lat": -9.4780,   "lon": 147.1500,   "popular": False},  # Port Moresby
    {"name": "Paraguay",            "lat": -25.2637,  "lon": -57.5759,   "popular": False},  # Asunción
    {"name": "Peru",                "lat": -12.0464,  "lon": -77.0428,   "popular": True},   # Lima
    {"name": "Philippines",         "lat": 14.5995,   "lon": 120.9842,   "popular": True},   # Manila
    {"name": "Poland",              "lat": 52.2297,   "lon": 21.0122,    "popular": False},  # Warsaw
    {"name": "Portugal",            "lat": 38.7223,   "lon": -9.1393,    "popular": False},  # Lisbon
    {"name": "Qatar",               "lat": 25.2854,   "lon": 51.5310,    "popular": False},  # Doha
    {"name": "Romania",             "lat": 44.4268,   "lon": 26.1025,    "popular": False},  # Bucharest
    {"name": "Russia",              "lat": 55.7558,   "lon": 37.6173,    "popular": True},   # Moscow
    {"name": "Rwanda",              "lat": -1.9706,   "lon": 30.1044,    "popular": False},  # Kigali
    {"name": "Saint_Kitts_and_Nevis","lat":17.3578,   "lon": -62.782998, "popular": False},  # Basseterre
    {"name": "Saint_Lucia",         "lat": 14.0101,   "lon": -60.9875,   "popular": False},  # Castries
    {"name": "Saint_Vincent_and_the_Grenadines","lat":13.2528,"lon":-61.1971,"popular":False},  # Kingstown
    {"name": "Samoa",               "lat": -13.7590,  "lon": -172.1046,  "popular": False},  # Apia
    {"name": "San_Marino",          "lat": 43.9424,   "lon": 12.4578,    "popular": False},  # San Marino (city)
    {"name": "Sao_Tome_and_Principe","lat":0.18636,   "lon": 6.6131,     "popular": False},  # São Tomé
    {"name": "Saudi_Arabia",        "lat": 24.7136,   "lon": 46.6753,    "popular": True},   # Riyadh
    {"name": "Senegal",             "lat": 14.6928,   "lon": -17.4467,   "popular": False},  # Dakar
    {"name": "Serbia",              "lat": 44.7872,   "lon": 20.4573,    "popular": False},  # Belgrade
    {"name": "Seychelles",          "lat": -4.6796,   "lon": 55.4919,    "popular": False},  # Victoria
    {"name": "Sierra_Leone",        "lat": 8.4844,    "lon": -13.2344,   "popular": False},  # Freetown
    {"name": "Singapore",           "lat": 1.3521,    "lon": 103.8198,   "popular": True},   # Singapore (city)
    {"name": "Slovakia",            "lat": 48.1486,   "lon": 17.1077,    "popular": False},  # Bratislava
    {"name": "Slovenia",            "lat": 46.0569,   "lon": 14.5058,    "popular": False},  # Ljubljana
    {"name": "Solomon_Islands",     "lat": -9.4456,   "lon": 159.9729,   "popular": False},  # Honiara
    {"name": "Somalia",             "lat": 2.0469,    "lon": 45.3182,    "popular": False},  # Mogadishu
    {"name": "South_Africa",        "lat": -25.7479,  "lon": 28.2293,    "popular": True},   # Pretoria
    {"name": "South_Korea",         "lat": 37.5665,   "lon": 126.9780,   "popular": True},   # Seoul
    {"name": "South_Sudan",         "lat": 4.8594,    "lon": 31.5713,    "popular": False},  # Juba
    {"name": "Spain",               "lat": 40.4168,   "lon": -3.7038,    "popular": True},   # Madrid
    {"name": "Sri_Lanka",           "lat": 6.9271,    "lon": 79.8612,    "popular": False},  # Colombo
    {"name": "Sudan",               "lat": 15.5007,   "lon": 32.5599,    "popular": False},  # Khartoum
    {"name": "Suriname",            "lat": 5.8520,    "lon": -55.2038,   "popular": False},  # Paramaribo
    {"name": "Sweden",              "lat": 59.3293,   "lon": 18.0686,    "popular": False},  # Stockholm
    {"name": "Switzerland",         "lat": 46.9480,   "lon": 7.4474,     "popular": True},   # Bern
    {"name": "Syria",               "lat": 33.5138,   "lon": 36.2765,    "popular": False},  # Damascus
    {"name": "Taiwan",              "lat": 25.0330,   "lon": 121.5654,   "popular": False},  # Taipei
    {"name": "Tajikistan",          "lat": 38.8610,   "lon": 71.2761,    "popular": False},  # Dushanbe
    {"name": "Tanzania",            "lat": -6.7924,   "lon": 39.2083,    "popular": False},  # Dodoma
    {"name": "Thailand",            "lat": 13.7563,   "lon": 100.5018,   "popular": True},   # Bangkok
    {"name": "Togo",                "lat": 6.1725,    "lon": 1.2314,     "popular": False},  # Lomé
    {"name": "Tonga",               "lat": -21.1790,  "lon": -175.1982,  "popular": False},  # Nukuʻalofa
    {"name": "Trinidad_and_Tobago", "lat": 10.6660,   "lon": -61.5169,   "popular": False},  # Port of Spain
    {"name": "Tunisia",             "lat": 36.8065,   "lon": 10.1815,    "popular": False},  # Tunis
    {"name": "Turkey",              "lat": 39.9334,   "lon": 32.8597,    "popular": True},   # Ankara
    {"name": "Turkmenistan",        "lat": 37.9601,   "lon": 58.3261,    "popular": False},  # Ashgabat
    {"name": "Tuvalu",              "lat": -7.1095,   "lon": 177.6493,   "popular": False},  # Funafuti
    {"name": "Uganda",              "lat": 0.3476,    "lon": 32.5825,    "popular": False},  # Kampala
    {"name": "Ukraine",             "lat": 50.4501,   "lon": 30.5234,    "popular": False},  # Kyiv
    {"name": "United_Arab_Emirates","lat": 24.4539,   "lon": 54.3773,    "popular": True},   # Abu Dhabi
    {"name": "United_Kingdom",      "lat": 51.5074,   "lon": -0.1278,    "popular": True},   # London
    {"name": "United_States",       "lat": 38.9072,   "lon": -77.0369,   "popular": True},   # Washington, D.C.
    {"name": "Uruguay",             "lat": -34.9011,  "lon": -56.1645,   "popular": False},  # Montevideo
    {"name": "Uzbekistan",          "lat": 41.2995,   "lon": 69.2401,    "popular": False},  # Tashkent
    {"name": "Vanuatu",             "lat": -17.7333,  "lon": 168.3273,   "popular": False},  # Port Vila
    {"name": "Vatican_City",        "lat": 41.9029,   "lon": 12.4534,    "popular": False},  # Vatican City
    {"name": "Venezuela",           "lat": 10.4806,   "lon": -66.9036,   "popular": False},  # Caracas
    {"name": "Vietnam",             "lat": 21.0278,   "lon": 105.8342,   "popular": True},   # Hanoi
    {"name": "Yemen",               "lat": 15.3694,   "lon": 44.1910,    "popular": False},  # Sana'a
    {"name": "Zambia",              "lat": -15.3875,  "lon": 28.3228,    "popular": False},  # Lusaka
    {"name": "Zimbabwe",            "lat": -17.8252,  "lon": 31.0335,    "popular": False},  # Harare
]

# Default limit for “normal” countries
DEFAULT_LIMIT = 100
# Increased limit for most-visited countries
POPULAR_LIMIT = 200

# Categories param for tourism attractions
CATEGORIES = "tourism.attraction"

def fetch_country_pois(country_name, lat, lon, limit):
    """
    Sends a GET request to Geoapify’s Places API for POIs around (lat, lon).
    Returns the parsed JSON response (a Python dict) or None on failure.
    """
    base_url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": CATEGORIES,
        "limit": limit,
        "filter": f"circle:{lon},{lat},{RADIUS_METERS}",
        "apiKey": API_KEY
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"[Error] {country_name}: HTTP {response.status_code} – {response.text}")
        return None

    return response.json()

# Main loop
def main():
    for entry in COUNTRIES:
        name = entry["name"]
        lat = entry["lat"]
        lon = entry["lon"]
        is_popular = entry["popular"]

        limit = POPULAR_LIMIT if is_popular else DEFAULT_LIMIT
        print(f"Fetching POIs for {name} (limit={limit}, center=({lat}, {lon}))...")

        pois = fetch_country_pois(name, lat, lon, limit)
        if pois is None:
            print(f"  → Skipped {name} due to error.")
            continue

        # Save to data/<country>.json
        filename = os.path.join(OUTPUT_DIR, f"{name}.json")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(pois, f, ensure_ascii=False, indent=2)
            print(f"  → Saved {len(pois.get('features', []))} POIs to {filename}")
        except Exception as e:
            print(f"  → Failed to save {name}.json: {e}")

        # Respectful rate limiting: pause a bit between requests
        time.sleep(1.0)

    print("All done.")


if __name__ == "__main__":
    main()