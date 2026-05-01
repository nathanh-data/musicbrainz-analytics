import requests
import psycopg
import time
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://musicbrainz.org/ws/2/artist/"

HEADERS = {
    "User-Agent": "musicbrainz-analytics/1.0 (00nana712@gmail.com)"
}

def fetch_french_artists(limit=5):
    params = {
        "query": "area:France AND type:person OR type:group",
        "fmt": "json",
        "limit": limit
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            artists = data.get("artists", [])

            print(f"Nombre d'artistes récupérés : {len(artists)}")

            # Debug (très utile)
            for artist in artists:
                print("→", artist.get("name"))

            return artists
        else:
            print("Erreur API :", response.status_code)
            print(response.text)
            return []

    except Exception as e:
        print("Erreur API :", e)
        return []


def insert_artists(artists):
    try:
        print("DB utilisée :", os.getenv("DB_NAME"))
        with psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        ) as conn:

            with conn.cursor() as cur:
                cur.execute("SELECT schema_name FROM information_schema.schemata;")
                print(cur.fetchall())

                for artist in artists:
                    cur.execute("""
                        INSERT INTO musicbrainz_raw.artist (mbid, name, country, disambiguation, type)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (mbid) DO NOTHING;
                    """, (
                        artist.get("id"),
                        artist.get("name"),
                        artist.get("country"),
                        artist.get("disambiguation"),
                        artist.get("type")
                    ))

            print(f"{len(artists)} artistes traités")

    except Exception as e:
        print("Erreur insertion :", e)


if __name__ == "__main__":
    print("🚀 Lancement du pipeline")

    artists = fetch_french_artists(limit=5)

    if artists:
        insert_artists(artists)
    else:
        print("Aucune donnée à insérer")

    time.sleep(1)