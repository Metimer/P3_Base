import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Dictionnaire des ligues avec les noms des pays et leurs URL
ligues = {
    'France': '13/Statistiques-Ligue-1',
    'Italie': '11/Statistiques-Serie-A',
    'Espagne': '12/Statistiques-La-Liga',
    'Allemagne': '20/Statistiques-Bundesliga',
    'Angleterre': '9/Statistiques-Premier-League'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Fonction pour récupérer les statistiques d'une ligue en fonction d'un ID de tableau
def fetch_league_data(ligues, table_id, prefix):
    df_ligues = {}

    for pays, url_part in ligues.items():
        url = f'https://fbref.com/fr/comps/{url_part}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération de la page pour {pays}.")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"id": table_id})  # On cherche un tableau spécifique
        if not table:
            print(f"⚠️ Table {table_id} non trouvée pour {pays}.")
            continue

        tbody = table.find("tbody")
        if not tbody:
            print(f"⚠️ Aucun <tbody> trouvé pour {pays}.")
            continue

        teams = []
        stats = []

        for row in tbody.find_all("tr"):
            cells = row.find_all(attrs={"data-stat": True})
            row_data = {}

            current_team = None
            for cell in cells:
                data_stat = cell["data-stat"]
                text = cell.get_text(strip=True)

                if data_stat == "team":
                    current_team = text
                    teams.append(current_team)
                elif current_team:
                    row_data[f"{prefix}{data_stat}"] = text  # On ajoute un préfixe aux colonnes

            if current_team:
                stats.append(row_data)

        # Convertir en DataFrame pandas et remplir les valeurs manquantes
        df = pd.DataFrame(stats, index=teams).fillna('N/A')

        df_ligues[pays] = df

        print(f"✅ Données récupérées pour {pays} ({table_id})")

    return df_ligues


# 🔹 Récupérer les statistiques standard
df_ligues_stats = fetch_league_data(ligues, "stats_squads_standard_for", "stats_")

# 🔹 Enregistrer les fichiers CSV
save_path = r'C:\Users\metin\OneDrive\Bureau\SpotValueBet'
os.makedirs(save_path, exist_ok=True)  # Assurer que le dossier existe

for pays, df in df_ligues_stats.items():
    filename = f"Advanced1_{pays}.csv"
    file_path = os.path.join(save_path, filename)

    try:
        df.to_csv(file_path)
        print(f"📁 Fichier sauvegardé : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du fichier {filename} : {e}")
