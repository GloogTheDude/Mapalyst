import matplotlib.pyplot as plt
import geopandas as gpd

# Charger les données
gdf_communes = gpd.read_file("Mapalyst\geojson\Belgique_communes.json")  # Communes
gdf_provinces = gpd.read_file("Mapalyst\geojson\Belgique_provinces.json")  # Provinces

# Définir les couleurs des communes
fig, ax = plt.subplots(figsize=(10, 10))

# Tracer les communes (fond gris, bordures vertes)
gdf_communes.plot(ax=ax, edgecolor="green", color="lightgrey", alpha=0.7)

# Tracer les provinces (bordures noires, sans remplissage)
gdf_provinces.plot(ax=ax, edgecolor="black", facecolor="none", linewidth=2)

# Colorier "Liège" en rouge avec une bordure violette
gdf_communes[gdf_communes["NAME_4"] == "Liège"].plot(ax=ax, color="red", edgecolor="purple")

plt.show()

