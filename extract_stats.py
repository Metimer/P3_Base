import zipfile
import requests
import io
import os

# URL du fichier ZIP
zipfile_url = 'https://www.football-data.co.uk/mmz4281/2425/data.zip'

# Dossier de destination où les fichiers seront enregistrés
dossier_de_sortie = r'C:\Users\metin\OneDrive\Bureau\SpotValueBet'

# Créer le dossier si nécessaire (au cas où il n'existe pas déjà)
os.makedirs(dossier_de_sortie, exist_ok=True)

# Télécharger le fichier ZIP depuis l'URL
response = requests.get(zipfile_url)

# Vérifier que la demande a réussi (code 200)
if response.status_code == 200:
    # Ouvrir le ZIP depuis le contenu téléchargé (en mémoire)
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        # Lister le contenu du fichier ZIP
        zip_list = zip_ref.namelist()

        # Dictionnaire de correspondance pour les nouveaux noms
        correspondance_noms = {
            'D1.csv': 'allemagne_stats_score.csv',
            'E0.csv': 'angleterre_stats_score.csv',
            'F1.csv': 'france_stats_score.csv',
            'SP1.csv': 'espagne_stats_score.csv',
            'I1.csv': 'italie_stats_score.csv'
        }

        # Extraire et renommer les fichiers spécifiés
        for fichier in zip_list:
            # Vérifier si le fichier fait partie de ceux que nous voulons extraire
            if fichier in correspondance_noms:
                # Définir le chemin de sortie complet
                chemin_sortie = os.path.join(dossier_de_sortie, correspondance_noms[fichier])

                # Extraire le fichier et le renommer avec le nouveau nom
                with open(chemin_sortie, 'wb') as f_out:
                    f_out.write(zip_ref.read(fichier))
                print(f"Fichier extrait et renommé : {fichier} -> {chemin_sortie}")
else:
    print(f"Échec du téléchargement du fichier. Code de statut: {response.status_code}")
