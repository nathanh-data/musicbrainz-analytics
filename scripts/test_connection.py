import psycopg
import os
from dotenv import load_dotenv

# 1. Charger le fichier .env
load_dotenv()

def test_connection():
    try:
        # 2. Récupérer les variables depuis .env
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")

        # 3. Connexion avec ces variables
        with psycopg.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        ) as conn:

            print("Connexion réussie !")

            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print("Test requête OK :", cur.fetchone())

    except Exception as e:
        print("Erreur :", e)


if __name__ == "__main__":
    test_connection()