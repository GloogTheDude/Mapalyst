import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
from extraction_xl import Formator

# Charger les données géographiques
gdf_communes = gpd.read_file("Mapalyst\\geojson\\geojson1_corrige.json")  # Communes
gdf_provinces = gpd.read_file("Mapalyst\\geojson\\Belgique_provinces.json")  # Provinces

# Charger les données Excel
ext = Formator(r'Mapalyst\\rapport.xlsx', 'Agenten-Agences')
tableau_compte = ext.get_tableau_compte('POS ZIP', 'POS Name')

# Fonction pour compter les POS par code postal
def count_pos_for_commune(postal_codes, tableau_compte):
    total_pos = 0
    for code in postal_codes.split(','):
        code = code.strip()
        if code.isdigit():
            total_pos += tableau_compte[tableau_compte["POS ZIP"] == int(code)]["POS Name"].count()
    return total_pos

# Ajouter une colonne 'count_POS' en appliquant la fonction avec lambda
gdf_communes["count_POS"] = gdf_communes["POSTAL_CODE"].apply(lambda x: count_pos_for_commune(x, tableau_compte))

# Définir des seuils et catégories pour colorier les polygones
thresholds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
gdf_communes['category'] = pd.cut(gdf_communes['count_POS'], bins=thresholds, labels=labels, right=False)

# Palette de couleurs pour les polygones
cmap = plt.get_cmap("nipy_spectral", len(labels))
colors = {labels[i]: cmap(i / len(labels)) for i in range(len(labels))}

# Vérifier et corriger les données géographiques
gdf_communes = gdf_communes.dropna(subset=["geometry"])
gdf_communes = gdf_communes[gdf_communes.is_valid]

# Extraire les polygones et centroïdes en objets Shapely
gdf_communes["centroid"] = gdf_communes.geometry.centroid

# Tracer avec Shapely et Matplotlib
fig, ax = plt.subplots(figsize=(10, 10))

# Tracer les polygones des communes avec les couleurs correspondantes
for _, row in gdf_communes.iterrows():
    polygon = row.geometry
    color = colors.get(row["category"], "white")  # Si pas de catégorie, couleur blanche

    if isinstance(polygon, Polygon):
        x, y = polygon.exterior.xy
        ax.fill(x, y, color=color, edgecolor="black", linewidth=0.6, alpha=0.7)

# Tracer les provinces (contours noirs)
for _, row in gdf_provinces.iterrows():
    polygon = row.geometry
    if isinstance(polygon, Polygon):
        x, y = polygon.exterior.xy
        ax.plot(x, y, color="black", linewidth=2)

# Tracer les centroïdes en points rouges
x_centroids = gdf_communes["centroid"].apply(lambda p: p.x)
y_centroids = gdf_communes["centroid"].apply(lambda p: p.y)
ax.scatter(x_centroids, y_centroids, color='red', label="Centroïdes des communes", s=10)

plt.legend()
plt.title("Répartition du nombre de POS par code postal (Shapely)")
plt.show()
