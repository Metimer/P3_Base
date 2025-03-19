import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from git import Repo  # Importer la bibliothèque git

# Dictionnaire des ligues avec les noms des pays et les suffixes urls
ligues = {
    'France': 'l1-mcdonald-s/45452',
    'Italie': 'serie-a/45402',
    'Espagne': 'laliga/45456',
    'Allemagne': 'bundesliga-1/45399',
    'Angleterre': 'premier-league/45457'
}

navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'

# Initialisation d'une liste pour stocker les données sous forme de dictionnaire
match_data = []

# Boucle à travers les ligues
for pays, url_part in ligues.items():
    url = f'https://www.pointdevente.parionssport.fdj.fr/paris-ouverts/football/{url_part}'
    response = requests.get(url, headers={'User-Agent': navigator})

    if response.status_code != 200:
        print(f"Erreur lors de la récupération de la page pour {pays}.")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')

    # Récupération des numéros de paris, des dates et heures
    dates_heures = soup.find_all('p', class_='match-home_time')
    pattern = r"N°(\d+)\s+.*Fin de valid\.\s+(\d{2}\/\d{2})\s+(\d{2}h\d{2})"

    # Liste temporaire pour stocker les infos des matchs
    matchs_info = []
    for date_heure in dates_heures:
        match_text = date_heure.text.strip()
        match_result = re.match(pattern, match_text)
        if match_result:
            matchs_info.append({
                "Pays": pays,
                "Ligue": url_part.split('/')[0],
                "Numéro de Pari": match_result.group(1),
                "Date du Match": match_result.group(2),
                "Heure de Fin de Validité": match_result.group(3),
                "Equipe Domicile": None,
                "Equipe Extérieure": None,
                "Cote Domicile": None,
                "Cote Nul": None,
                "Cote Extérieur": None
            })

    # Récupération des matchs et équipes
    matchs = soup.find_all('div', class_='match-home_title')
    match_pattern = r"([^\-]+)-([^\-]+)"

    for i, match_ in enumerate(matchs):
        match_text = match_.text.strip()
        match_result = re.match(match_pattern, match_text)
        if match_result and i < len(matchs_info):
            matchs_info[i]["Equipe Domicile"] = match_result.group(1).strip()
            matchs_info[i]["Equipe Extérieure"] = match_result.group(2).strip()

    # Extraction des cotes
    cotes_vdomicile = [c.text.strip() for c in soup.find_all('span', class_='outcomeButton_value', attrs={"data": "app-market-template|outcome-1|outcomeButton_value"})]
    cotes_nul = [c.text.strip() for c in soup.find_all('span', class_='outcomeButton_value', attrs={"data": "app-market-template|outcome-N|outcomeButton_value"})]
    cotes_vexterieur = [c.text.strip() for c in soup.find_all('span', class_='outcomeButton_value', attrs={"data": "app-market-template|outcome-2|outcomeButton_value"})]

    # Associer les cotes aux matchs
    for i in range(len(matchs_info)):
        matchs_info[i]["Cote Domicile"] = cotes_vdomicile[i] if i < len(cotes_vdomicile) else None
        matchs_info[i]["Cote Nul"] = cotes_nul[i] if i < len(cotes_nul) else None
        matchs_info[i]["Cote Extérieur"] = cotes_vexterieur[i] if i < len(cotes_vexterieur) else None

    # Ajouter à la liste globale
    match_data.extend(matchs_info)

# Création du DataFrame à partir de la liste de dictionnaires
df = pd.DataFrame(match_data)

# Enregistrer le CSV dans le répertoire du projet (à la racine)
csv_filename = "cotes_du_jour.csv"
save_path = os.getcwd()  # S'assure que les fichiers sont enregistrés à la racine du repo GitHub

try:
    # Sauvegarde du fichier CSV
    df.to_csv(csv_filename, index=False)  # index=False pour ne pas inclure l'index du DataFrame dans le fichier CSV
    print(f"📁 Fichier sauvegardé : {csv_filename}")
except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde du fichier {csv_filename} : {e}")

# 🔹 Ajouter, commettre et pousser sur GitHub
try:
    # Charger le repo GitHub
    repo = Repo(save_path)  # Repos GitHub cloné dans le répertoire courant
    origin = repo.remote(name='origin')  # Définir le remote 'origin'

    # Ajouter le fichier CSV au suivi de Git
    file_path = os.path.join(save_path, csv_filename)
    repo.git.add(file_path)  # Ajouter chaque fichier CSV

    # Commit des fichiers avec un message
    repo.index.commit("Mise à jour des fichiers CSV des cotes")

    # Push les changements sur GitHub
    origin.push()  # Pousse les changements vers GitHub
    print("🚀 Fichiers CSV mis à jour sur GitHub avec succès !")

except Exception as e:
    print(f"❌ Erreur lors de la mise à jour sur GitHub : {e}")
