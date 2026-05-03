import requests
import psycopg
import time
import os
import random
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://musicbrainz.org/ws/2/artist/"
HEADERS = {
    "User-Agent": "musicbrainz-analytics/1.0 (00nana712@gmail.com)"
}

def safe_get(url, params, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            time.sleep(1 + random.uniform(0, 0.5))
            return response
        except requests.exceptions.RequestException as e:
            print(f"Retry {i+1}/{retries} : {e}")
            time.sleep(2 + random.uniform(0, 1))
    print(f"Échec après {retries} tentatives pour {url}")
    return None

def fetch_french_artists(limit=5):
    params = {
        "query": "area:France AND (type:person OR type:group)",
        "fmt": "json",
        "limit": limit
    }
    response = safe_get(BASE_URL, params)
    if response:
        artists = response.json().get("artists", [])
        print(f"Nombre d'artistes récupérés : {len(artists)}")
        return artists
    return []

def fetch_release_groups(artist_mbid):
    url = "https://musicbrainz.org/ws/2/release-group/"
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100
    }
    response = safe_get(url, params)
    if response:
        return response.json().get("release-groups", [])
    return []

def fetch_recordings(artist_mbid):
    url = "https://musicbrainz.org/ws/2/recording/"
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100
    }
    response = safe_get(url, params)
    if response:
        return response.json().get("recordings", [])
    return []

def fetch_releases(artist_mbid):
    url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100,
        "inc": "labels"
    }
    response = safe_get(url, params)
    if response:
        return response.json().get("releases", [])
    return []

def get_db_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def insert_artists(artists):
    try:
        print("DB utilisée :", os.getenv("DB_NAME"))
        with get_db_connection() as conn:
            with conn.cursor() as cur:
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
        print("Erreur insertion artistes :", e)

def insert_release_groups(artist_mbid, release_groups):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                count = 0
                for rg in release_groups:
                    if rg.get("primary-type") != "Album":
                        continue
                    cur.execute("""
                        INSERT INTO musicbrainz_raw.release_group
                        (mbid, artist_mbid, title, primary_type, first_release_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (mbid) DO NOTHING;
                    """, (
                        rg.get("id"),
                        artist_mbid,
                        rg.get("title"),
                        rg.get("primary-type"),
                        rg.get("first-release-date")
                    ))
                    count += 1
        print(f"{count} albums insérés pour {artist_mbid}")
    except Exception as e:
        print("Erreur insertion release_group :", e)

def insert_recordings(artist_mbid, recordings):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for rec in recordings:
                    cur.execute("""
                        INSERT INTO musicbrainz_raw.recording
                        (mbid, artist_mbid, title, length)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (mbid) DO NOTHING;
                    """, (
                        rec.get("id"),
                        artist_mbid,
                        rec.get("title"),
                        rec.get("length")
                    ))
        print(f"{len(recordings)} recordings insérés pour {artist_mbid}")
    except Exception as e:
        print("Erreur insertion recording :", e)

def insert_labels_from_releases(artist_mbid, releases):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                count = 0
                for rel in releases:
                    for label_info in rel.get("label-info", []):
                        label = label_info.get("label")
                        if not label:
                            continue
                        cur.execute("""
                            INSERT INTO musicbrainz_raw.label
                            (mbid, artist_mbid, name, country)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (mbid) DO NOTHING;
                        """, (
                            label.get("id"),
                            artist_mbid,
                            label.get("name"),
                            label.get("area", {}).get("name")
                        ))
                        count += 1
        print(f"{count} labels insérés pour {artist_mbid}")
    except Exception as e:
        print("Erreur insertion label :", e)

if __name__ == "__main__":
    print("🚀 Lancement du pipeline")

    artists = fetch_french_artists(limit=5)
    for artist in artists:
        print(f"→ {artist['name']}")
    insert_artists(artists)

    for artist in artists:
        mbid = artist.get("id")
        name = artist.get("name")
        print(f"\n🎵 Traitement de {name} ({mbid})")

        release_groups = fetch_release_groups(mbid)
        insert_release_groups(mbid, release_groups)

        recordings = fetch_recordings(mbid)
        insert_recordings(mbid, recordings)

        releases = fetch_releases(mbid)
        insert_labels_from_releases(mbid, releases)

    print("\n✅ Pipeline terminé")