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
        "query": "area:France AND (type:person OR type:group)",
        "fmt": "json",
        "limit": limit
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            artists = data.get("artists", [])

            print(f"Nombre d'artistes récupérés : {len(artists)}")

            

            return artists
        else:
            print("Erreur API :", response.status_code)
            print(response.text)
            return []

    except Exception as e:
        print("Erreur API :", e)
        return []

def fetch_release_groups(artist_mbid):
    url = "https://musicbrainz.org/ws/2/release-group/"
    
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100
    }

    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("release-groups", [])
    else:
        print("Erreur release_group :", response.status_code)
        return []


def fetch_recordings(artist_mbid):
    url = "https://musicbrainz.org/ws/2/recording/"
    
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100
    }

    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("recordings", [])
    else:
        print("Erreur recording :", response.status_code)
        return []

def fetch_releases(artist_mbid):
    url = "https://musicbrainz.org/ws/2/release/"
    
    params = {
        "artist": artist_mbid,
        "fmt": "json",
        "limit": 100,
        "inc": "labels"
    }

    response = requests.get(url, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("releases", [])
    else:
        print("Erreur release :", response.status_code)
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

def insert_release_groups(artist_mbid, release_groups):
    try:
        with psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        ) as conn:

            with conn.cursor() as cur:

                for rg in release_groups:
                    
                    # 👇 FILTRE ICI
                    if rg.get("primary-type") is None or rg.get("primary-type") != "Album":
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

            print(f"{len(release_groups)} albums insérés pour {artist_mbid}")

    except Exception as e:
        print("Erreur insertion release_group :", e)


def insert_recordings(artist_mbid, recordings):
    try:
        with psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        ) as conn:

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
        with psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        ) as conn:

            with conn.cursor() as cur:

                count = 0

                for rel in releases:
                    label_info_list = rel.get("label-info", [])

                    for label_info in label_info_list:
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
                            label.get("country")
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

    # 🔥 NOUVEAU
    for artist in artists:
        mbid = artist.get("id")

        release_groups = fetch_release_groups(mbid)
        insert_release_groups(mbid, release_groups)

    # 🔥 RECORDINGS
    for artist in artists:
        mbid = artist.get("id")

        recordings = fetch_recordings(mbid)
        insert_recordings(mbid, recordings)

    # 🔥 LABELS
    for artist in artists:
        mbid = artist.get("id")

        releases = fetch_releases(mbid)
        insert_labels_from_releases(mbid, releases)

        time.sleep(1)