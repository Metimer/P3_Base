import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess
from git import Repo 
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

df_ligues = {}

# Boucle à travers les ligues
for pays, url_part in ligues.items():
    url = f'https://fbref.com/fr/comps/{url_part}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération de la page pour {pays}.")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')

    # Récupérer uniquement la section <tbody>
    tbody = soup.find("tbody")
    if not tbody:
        print(f"⚠️ Aucun tableau trouvé pour {pays}.")
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
                row_data[data_stat] = text

        if current_team:
            stats.append(row_data)

    # Convertir en DataFrame pandas
    df = pd.DataFrame(stats, index=teams).fillna('N/A')

    # Stocker le DataFrame dans un dictionnaire
    df_ligues[pays] = df

    print(f"✅ Données récupérées pour {pays} ({url_part})")

save_path = os.getcwd()  # S'assure que les fichiers sont enregistrés à la racine du repo GitHub

# 🔹 Sauvegarder les fichiers CSV
for pays, df in df_ligues.items():
    filename = f"Classement_{pays}.csv"  # Change le préfixe selon le type de données
    file_path = os.path.join(save_path, filename)

    try:
        df.to_csv(file_path)  # Sauvegarde le fichier
        print(f"📁 Fichier sauvegardé : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du fichier {filename} : {e}")

# 🔹 Ajouter, commettre et pousser sur GitHub
try:
    # Charger le repo GitHub
    repo = Repo(save_path)  # Repos GitHub cloné dans le répertoire courant
    origin = repo.remote(name='origin')  # Définir le remote 'origin'

    # Ajouter les fichiers CSV extraits au commit
    for pays in df_ligues.keys():
        file_path = os.path.join(save_path, f"Classement_{pays}.csv")
        repo.git.add(file_path)  # Ajouter chaque fichier CSV

    # Commit les fichiers avec un message
    repo.index.commit("Mise à jour des fichiers CSV des Classements")

    # Push les changements sur GitHub
    origin.push()  # Pousse les changements vers GitHub
    print("🚀 Fichiers CSV mis à jour sur GitHub avec succès !")

except Exception as e:
    print(f"❌ Erreur lors de la mise à jour sur GitHub : {e}")
