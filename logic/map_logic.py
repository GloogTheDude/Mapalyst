import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def generate_plot_gdf(controller, op, col, group, level, cmap_choice, custom_colors):
    geojson_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "ressources", "geojson")
    )

    gdf_communes = gpd.read_file(os.path.join(geojson_dir, "geojson1_corrige.json"))
    gdf_communes["POSTAL_CODE"] = gdf_communes["POSTAL_CODE"].astype(str)
    gdf_communes["NAME_4"] = gdf_communes["NAME_4"].astype(str)

    all_dfs = []
    for loaded_file in controller.data_manager.files:
        for sheet in loaded_file.sheets:
            df = sheet.dataframe.copy()
            df["__sheet"] = sheet.name
            df["__file"] = loaded_file.path
            all_dfs.append(df)

    if not all_dfs:
        raise RuntimeError("Aucune donnée Excel disponible.")

    full_df = pd.concat(all_dfs, ignore_index=True)

    zip_col = controller.data_manager.zip_column
    if not zip_col:
        raise RuntimeError("Aucune colonne ZIP définie.")

    zip_path, zip_sheet, zip_name = zip_col

    zip_df = None
    for lf in controller.data_manager.files:
        if lf.path == zip_path:
            for s in lf.sheets:
                if s.name == zip_sheet:
                    zip_df = s.dataframe.copy()
                    break

    if zip_df is None:
        raise RuntimeError("Feuille ZIP non trouvée.")

    zip_df[zip_name] = zip_df[zip_name].astype(str)
    zip_df = zip_df.assign(__zip_clean=zip_df[zip_name].str.split(",")).explode("__zip_clean")
    zip_df["__zip_clean"] = zip_df["__zip_clean"].str.extract(r"(\d+)").dropna()
    zip_df["__zip_clean"] = zip_df["__zip_clean"].astype(int)

    if op == "sum":
        zip_df[col] = pd.to_numeric(zip_df[col], errors="coerce")

    zip_grouped = zip_df.groupby("__zip_clean")[col].agg("count" if op == "count" else "sum").to_dict()

    def compute_commune_value(postal_codes):
        total = 0
        for raw in str(postal_codes).split(","):
            try:
                z = int(raw.strip())
                total += zip_grouped.get(z, 0)
            except:
                continue
        return total

    gdf_communes["value"] = gdf_communes["POSTAL_CODE"].apply(compute_commune_value)

    if cmap_choice == "personnalisée" and custom_colors:
        values = gdf_communes["value"].fillna(0).astype(float)
        bins = np.linspace(values.min(), values.max(), len(custom_colors) + 1)
        categories = np.digitize(values, bins, right=False) - 1
        categories = np.clip(categories, 0, len(custom_colors) - 1)
        gdf_communes["_color"] = [custom_colors[i] for i in categories]
        gdf_communes["_bin"] = categories
        gdf_communes["_legend"] = [f"{int(bins[i])} - {int(bins[i+1])}" for i in categories]

    if level == "Commune":
        return gdf_communes.copy()
    elif level == "Province":
        gdf = gpd.read_file(os.path.join(geojson_dir, "Belgique_provinces.json"))
        gdf["NAME_2"] = gdf["NAME_2"].apply(lambda x: x[0] if isinstance(x, list) else x)
        province_totals = gdf_communes.groupby("NAME_3")["value"].sum().to_dict()
        gdf["value"] = gdf["NAME_2"].map(province_totals).fillna(0)
        return gdf
    elif level == "Région":
        gdf = gpd.read_file(os.path.join(geojson_dir, "Belgique_region.json"))
        gdf["NAME_1"] = gdf["NAME_1"].apply(lambda x: x[0] if isinstance(x, list) else x)
        region_totals = gdf_communes.groupby("NAME_1")["value"].sum().to_dict()
        gdf["value"] = gdf["NAME_1"].map(region_totals).fillna(0)
        return gdf
    else:
        raise ValueError(f"Niveau de carte inconnu : {level}")
