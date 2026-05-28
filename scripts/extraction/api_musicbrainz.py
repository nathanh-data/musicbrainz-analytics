import requests
import psycopg
import time
import os
import random
from datetime import datetime
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

def get_last_pipeline_run():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT last_run
                    FROM staging.pipeline_state
                    WHERE pipeline_name = 'musicbrainz_api';
                """)
                result = cur.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        print("Erreur récupération pipeline_state :", e)
    return None

def fetch_french_artists(limit=100):
    all_artists = []
    offset = 0

    while True:
        params = {
            "query": "area:France AND (type:person OR type:group)",
            "fmt": "json",
            "limit": 100,
            "offset": offset
        }
        response = safe_get(BASE_URL, params)
        if not response:
            break

        artists = response.json().get("artists", [])
        if not artists:
            break

        all_artists.extend(artists)
        print(f"{len(all_artists)} artistes récupérés...")

        if len(all_artists) >= limit:
            break

        offset += 100

    return all_artists[:limit]

def fetch_release_groups(artist_mbid, max_rg=20):
    url = "https://musicbrainz.org/ws/2/release-group/"
    all_release_groups = []
    offset = 0

    while True:
        params = {
            "artist": artist_mbid,
            "fmt": "json",
            "limit": 100,
            "offset": offset
        }
        response = safe_get(url, params)
        if not response:
            break

        release_groups = response.json().get("release-groups", [])
        if not release_groups:
            break

        all_release_groups.extend(release_groups)
        print(f"    {len(all_release_groups)} release_groups récupérés...")

        if len(all_release_groups) >= max_rg:
            break

        offset += 100

    return all_release_groups[:max_rg]

def fetch_releases_by_release_group(rg_mbid, max_releases=10):
    url = "https://musicbrainz.org/ws/2/release/"
    all_releases = []
    offset = 0

    while True:
        params = {
            "release-group": rg_mbid,
            "fmt": "json",
            "limit": 100,
            "offset": offset,
            "inc": "recordings"
        }
        response = safe_get(url, params)
        if not response:
            break

        releases = response.json().get("releases", [])
        if not releases:
            break

        all_releases.extend(releases)
        print(f"      {len(all_releases)} releases récupérées...")

        if len(all_releases) >= max_releases:
            break

        offset += 100

    return all_releases[:max_releases]

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

def insert_releases_and_tracks(releases, rg_mbid):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                release_count = 0
                track_count = 0

                for rel in releases:
                    release_id = rel.get("id")
                    cur.execute("""
                        INSERT INTO musicbrainz_raw.release
                        (mbid, release_group_mbid, title)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (mbid) DO NOTHING;
                    """, (
                        release_id,
                        rg_mbid,
                        rel.get("title")
                    ))
                    release_count += 1

                    for medium in rel.get("media", []):
                        for track in medium.get("tracks", []):
                            recording = track.get("recording")
                            if not recording:
                                continue
                            cur.execute("""
                                INSERT INTO musicbrainz_raw.track
                                (mbid, release_mbid, recording_mbid, title, length)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (mbid) DO NOTHING;
                            """, (
                                track.get("id"),
                                release_id,
                                recording.get("id"),
                                track.get("title"),
                                track.get("length")
                            ))
                            track_count += 1

        print(f"{release_count} releases insérés | {track_count} tracks insérés")
    except Exception as e:
        print("Erreur insertion releases/tracks :", e)

def update_pipeline_run():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE staging.pipeline_state
                    SET last_run = %s
                    WHERE pipeline_name = 'musicbrainz_api';
                """, (datetime.now(),))
        print("✅ pipeline_state mis à jour")
    except Exception as e:
        print("Erreur update pipeline_state :", e)

if __name__ == "__main__":
    print("🚀 Lancement du pipeline")

    last_run = get_last_pipeline_run()
    print("Dernier run pipeline :", last_run)

    artists = fetch_french_artists(limit=10)
    for artist in artists:
        print(f"→ {artist['name']}")
    insert_artists(artists)

    for artist in artists:
        mbid = artist.get("id")
        name = artist.get("name")
        print(f"\n🎵 Traitement de {name} ({mbid})")

        release_groups = fetch_release_groups(mbid, max_rg=20)
        insert_release_groups(mbid, release_groups)

        for rg in release_groups:
            if rg.get("primary-type") != "Album":
                continue

            rg_mbid = rg.get("id")
            rg_title = rg.get("title")
            print(f"  📀 Album : {rg_title}")

            releases = fetch_releases_by_release_group(rg_mbid, max_releases=10)
            insert_releases_and_tracks(releases, rg_mbid)
    
    update_pipeline_run()

    print("\n✅ Pipeline terminé")