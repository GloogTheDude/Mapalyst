import json

# Charger les fichiers JSON
with open("Mapalyst\\geojson\\Belgique_communes.json", "r", encoding="utf-8") as f1, open("Mapalyst\\geojson\\postal-codes-belgium.geojson", "r", encoding="utf-8") as f2:
    geojson1 = json.load(f1)
    geojson2 = json.load(f2)

# Créer un dictionnaire où la clé est le nom de la commune et la valeur est une liste de codes postaux
commune_zip_map = {}

# Ajouter les codes postaux dans le dictionnaire
for feature in geojson2["features"]:
    commune_nl = feature["properties"]["municipality_name_dutch"]
    commune_fr = feature["properties"]["municipality_name_french"]
    commune_ger = feature["properties"]["municipality_name_german"]
    postal_code = str(feature["properties"]["post_code"])  # S'assurer que c'est une chaîne

    for commune in (commune_nl, commune_fr, commune_ger):
        if commune:  # Éviter les None
            if commune not in commune_zip_map:
                commune_zip_map[commune] = set()  # Utilisation d'un set pour éviter les doublons
            commune_zip_map[commune].add(postal_code)

# Ajouter les codes postaux à JSON1 sous forme de string (séparés par une virgule)
for feature in geojson1["features"]:
    commune = feature["properties"]["NAME_4"]  # Nom de la commune dans JSON1
    if commune in commune_zip_map:
        feature["properties"]["POSTAL_CODE"] = ", ".join(sorted(commune_zip_map[commune]))  # Convertir en string

# Sauvegarder le GeoJSON corrigé
with open("geojson1_corrige.json", "w", encoding="utf-8") as f_out:
    json.dump(geojson1, f_out, indent=4, ensure_ascii=False)

print("✅ Mise à jour terminée, fichier corrigé enregistré sous geojson1_corrige.json")
