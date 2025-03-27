import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import mplcursors
import numpy as np
from extraction_xl import extractor
from shapely.geometry import Point

# Charger les données géographiques
gdf_communes = gpd.read_file("Mapalyst\\geojson\\geojson1_corrige.json")  # Communes
gdf_provinces = gpd.read_file("Mapalyst\\geojson\\Belgique_provinces.json")  # Provinces

# Charger les données Excel
ext = extractor(r'Mapalyst\\rapport.xlsx', 'Agenten-Agences')
tableau_compte = ext.prep_tableau_compte('POS ZIP', 'POS Name')  # Crée le dictionnaire avec les comptes

# Fonction pour compter les POS pour chaque code postal
def count_pos_for_commune(postal_codes, tableau_compte):
    total_pos = 0
    # Parcourir chaque code postal de la commune et additionner les 'POS Name' correspondants
    for code in postal_codes.split(','):  # En supposant que les codes postaux sont séparés par une virgule
        code = code.strip()  # Nettoyer les espaces
        if code.isdigit():  # Assurer que c'est un code postal valide
            total_pos += tableau_compte[tableau_compte["POS ZIP"] == int(code)]["POS Name"].count()
            print(f"code = {code} => {tableau_compte[tableau_compte["POS ZIP"] == int(code)]["POS Name"].count()}")
    
    print(f"postal_codes: {postal_codes} = total_pos : {total_pos}")   

    return total_pos

# Ajouter une colonne 'count_POS' à gdf_communes en mappant chaque code postal
gdf_communes["count_POS"] = gdf_communes["POSTAL_CODE"].apply(count_pos_for_commune)
print(f"max? {gdf_communes['count_POS'].max()}")


# Définir des seuils pour diviser les données en catégories (par exemple : faible, moyen, élevé)
thresholds = [0,1,2,3,4,5,6,7,8,9,10,11]  # Tu peux ajuster ces seuils selon tes données
labels = ["0","1","2","3","4","5","6","7","8","9","10"]

# Catégoriser les communes en fonction du nombre de POS
gdf_communes['category'] = pd.cut(gdf_communes['count_POS'], bins=thresholds, labels=labels, right=False)

# Définir une palette de couleurs distinctes
cmap = plt.get_cmap("nipy_spectral", len(labels))  # Palette de couleurs distinctes

# Vérifier et corriger les données géographiques
gdf_communes = gdf_communes.dropna(subset=["geometry"])
gdf_communes = gdf_communes[gdf_communes.is_valid]

# Sauvegarder le tableau des comptes en CSV
ext.tableau_compte.to_csv('tableau_compte.csv', index=False)

# Tracer la carte
fig, ax = plt.subplots(figsize=(10, 10))

# Tracer les communes avec la couleur en fonction de la catégorie
gdf_communes.plot(ax=ax, column="category", cmap=cmap, edgecolor="black", linewidth=0.6, alpha=0.7, legend=True)

# Tracer les provinces
gdf_provinces.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=2)

# Ajouter une barre de couleurs pour voir l'échelle
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=len(labels)-1))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, ticks=range(len(labels)))
cbar.set_ticklabels(labels)
cbar.set_label("Nombre de POS")

# Ajouter un gestionnaire de clic avec mplcursors
def on_click(sel):
    # Récupérer les coordonnées du clic
    click_x, click_y = sel.target
    
    # Créer un point à partir des coordonnées du clic
    cursor_point = Point(click_x, click_y)  # Convertir sel.target en un objet Point

    # Trouver le polygone qui contient ce point (la commune)
    commune_idx = gdf_communes[gdf_communes.contains(cursor_point)].index
    
    if len(commune_idx) > 0:
        idx = commune_idx[0]  # Prendre le premier polygone trouvé

        # Récupérer les informations de la commune
        commune_name = gdf_communes.iloc[idx]["NAME_4"]
        zip_code = gdf_communes.iloc[idx]["POSTAL_CODE"]
        total = gdf_communes.iloc[idx]["count_POS"]

        # Ajouter l'annotation avec le nom de la commune et le nombre de POS
        sel.annotation.set_text(f"{commune_name} - {total}")
    else:
        sel.annotation.set_text("Pas de commune trouvée à cet endroit")

mplcursors.cursor(gdf_communes.plot(ax=ax, column="category", cmap=cmap, edgecolor="black", linewidth=0.6, alpha=0.7, legend=True), hover=False).connect(
    "add", on_click
)

plt.title("Répartition du nombre de POS par code postal")
plt.show()

# Afficher les nouvelles valeurs min/max
print(f"Min: {gdf_communes['count_POS'].min()}, Max: {gdf_communes['count_POS'].max()}")

# class MyDrawer():
    
#     def __init__(self):
#         pass

#     def draw_map(self, coord_path):
#         coords=None
#         if isinstance(coord_path,list):
#             coords = list()
#             for c in coord_path:
#                 coords.append(gpd.read_file(c))
#         if isinstance(coord_path, str):
#             coords = gpd.read_file(coord_path)
    
#     def 
            
            