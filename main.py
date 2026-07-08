import csv
import os
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------- CONFIG ----------------

cities = [
    # --- NORTH AMERICA: UNITED STATES ---
    "New York City", "Los Angeles", "Chicago", "Houston", "Phoenix", 
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", 
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington D.C.",
    "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City", 
    "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore",
    "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento", 
    "Mesa", "Kansas City", "Atlanta", "Omaha", "Colorado Springs",
    "Raleigh", "Long Beach", "Virginia Beach", "Miami", "Oakland", 
    "Minneapolis", "Tulsa", "Bakersfield", "Wichita", "Arlington",
    "New Orleans", "Cleveland", "Tampa", "Honolulu", "St. Louis", 
    "Pittsburgh", "Cincinnati", "Anchorage", "Boise", "Des Moines", 
    "Salt Lake City", "Orlando", "Reno", "Buffalo", "Richmond", 
    "Hartford", "Providence", "Juneau", "Tallahassee", "Topeka",

    # --- NORTH AMERICA: CANADA ---
    "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", 
    "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Mississauga",
    "Victoria", "Halifax", "Windsor", "Saskatoon", "Regina", 
    "St. John's", "Charlottetown", "Fredericton", "Moncton", "Guelph",
    "Kingston", "Sudbury", "Thunder Bay", "Kelowna", "Nanaimo", 
    "Whitehorse", "Yellowknife", "Iqaluit", "Sherbrooke", "Trois-Rivieres",

    # --- EUROPE: UNITED KINGDOM & IRELAND ---
    "London", "Birmingham", "Manchester", "Glasgow", "Liverpool", 
    "Leeds", "Sheffield", "Edinburgh", "Bristol", "Leicester",
    "Coventry", "Belfast", "Cardiff", "Nottingham", "Newcastle upon Tyne", 
    "Southampton", "Aberdeen", "Plymouth", "Dublin", "Cork",
    "Galway", "Limerick", "Waterford",

    # --- EUROPE: GERMANY & FRANCE ---
    "Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", 
    "Stuttgart", "Dusseldorf", "Leipzig", "Dresden", "Hannover",
    "Nuremberg", "Bremen", "Bonn", "Muenster", "Karlsruhe", 
    "Augsburg", "Wiesbaden", "Paris", "Marseille", "Lyon", 
    "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", 
    "Bordeaux", "Lille",

    # --- EUROPE: WESTERN & CENTRAL ---
    "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", 
    "Malaga", "Murcia", "Palma de Mallorca", "Las Palmas", "Bilbao",
    "Rome", "Milan", "Naples", "Turin", "Palermo", 
    "Genoa", "Bologna", "Florence", "Bari", "Catania",
    "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", 
    "Groningen", "Tilburg", "Almere", "Breda", "Nijmegen",
    "Brussels", "Antwerp", "Ghent", "Charleroi", "Liege", 
    "Bruges", "Namur", "Leuven", "Zurich", "Geneva", 
    "Basel", "Bern", "Lausanne", "Lucerne", "Lugano",
    "Vienna", "Salzburg", "Graz", "Innsbruck", "Linz",

    # --- EUROPE: NORDICS & EASTERN EUROPE ---
    "Copenhagen", "Aarhus", "Odense", "Aalborg", "Oslo", 
    "Bergen", "Trondheim", "Stavanger", "Stockholm", "Gothenburg",
    "Malmo", "Uppsala", "Helsinki", "Espoo", "Tampere", 
    "Turku", "Tallinn", "Riga", "Vilnius", "Warsaw", 
    "Krakow", "Lodz", "Wroclaw", "Poznan", "Gdansk",
    "Prague", "Brno", "Ostrava", "Plzen", "Bratislava",
    "Budapest", "Debrecen", "Szeged", "Miskolc", "Pecs",
    "Bucharest", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta",

    # --- OCEANIA: AUSTRALIA & NEW ZEALAND ---
    "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", 
    "Gold Coast", "Newcastle", "Canberra", "Wollongong", "Hobart",
    "Auckland", "Christchurch", "Wellington", "Hamilton", "Tauranga", 
    "Dunedin",

    # --- ASIA: JAPAN ---
    "Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", 
    "Kobe", "Kyoto", "Fukuoka", "Kawasaki", "Saitama",
    "Hiroshima", "Sendai", "Kitakyushu", "Chiba", "Sakai", 
    "Niigata", "Hamamatsu", "Shizuoka", "Sagamihara", "Okayama",
    "Kumamoto", "Kagoshima", "Kanazawa", "Nagasaki",

    # --- ASIA: SOUTH KOREA ---
    "Seoul", "Busan", "Incheon", "Daegu", "Daejeon", 
    "Gwangju", "Suwon", "Ulsan", "Changwon", "Seongnam",
    "Goyang", "Yongin", "Jeonju", "Cheongju", "Jeju City", 
    "Chuncheon", "Mokpo", "Pohang", "Gumi", "Asan",

    # --- SOUTH AMERICA ---
    "Rio de Janeiro", "Sao Paulo", "Brasilia", "Salvador", "Fortaleza", 
    "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre",
    "Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata",
    "Santiago", "Valparaiso", "Concepcion", "Bogota", "Medellin", 
    "Cali", "Barranquilla", "Lima", "Arequipa", "Trujillo",
    "Quito", "Guayaquil", "Caracas", "Maracaibo", "Maracay",
    "Montevideo", "Asuncion", "La Paz", "Sucre", "Santa Cruz de la Sierra",

    # --- AFRICA ---
    "Pretoria", "Johannesburg", "Cape Town", "Durban", "Port Elizabeth", 
    "Bloemfontein", "Windhoek", "Gaborone", "Maputo", "Nairobi", 
    "Mombasa", "Dar es Salaam", "Kampala", "Kigali", "Lusaka"
]


OUTPUT_DIR = Path("city_flags")
OUTPUT_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 0.4      # ~2.5 requests/sec

# ----------------------------------------

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

session.mount("https://", HTTPAdapter(max_retries=retry))

session.headers.update({
    "User-Agent": "CityFlagDownloader/1.0 (your@email.com)"
})

API = "https://commons.wikimedia.org/w/api.php"

failed = []


def api_search(search):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search,
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }

    r = session.get(API, params=params, timeout=20)
    r.raise_for_status()

    return r.json()


def find_svg(city):
    searches = [
        f'intitle:"Flag of {city}" filetype:svg',
        f'{city} flag filetype:svg',
    ]

    for search in searches:
        data = api_search(search)

        if "query" not in data:
            continue

        pages = sorted(
            data["query"]["pages"].values(),
            key=lambda p: p["title"]
        )

        for page in pages:
            if page["title"].lower().endswith(".svg"):
                return page["imageinfo"][0]["url"]

        time.sleep(REQUEST_DELAY)

    return None


for city in cities:

    filename = OUTPUT_DIR / f"{city.lower().replace(' ', '_')}.svg"

    if filename.exists():
        print(f"Skipping {city}")
        continue

    print(city)

    try:
        url = find_svg(city)

        if url is None:
            print("   No SVG found")
            failed.append(city)
            continue

        r = session.get(url, timeout=30)
        r.raise_for_status()

        filename.write_bytes(r.content)

        print("   Downloaded")

    except Exception as e:
        print(e)
        failed.append(city)

    time.sleep(REQUEST_DELAY)

if failed:
    with open("failed.csv", "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(["city"])
        for city in failed:
            writer.writerow([city])

print()
print(f"Finished. Failed: {len(failed)}")