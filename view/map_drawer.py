import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, colorchooser
import os
import sys
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from logic.map_logic import generate_plot_gdf


class MapDrawer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.controller = None

        # --- Variables Tkinter ---
        self.operation_var = tk.StringVar(value="count")
        self.column_var = tk.StringVar()
        self.group_var = tk.StringVar(value="Commune")
        self.map_level_var = tk.StringVar(value="Commune")
        self.colormap_var = tk.StringVar(value="OrRd")

        self.custom_colors = []  # Liste de couleurs personnalisées (ordre = intervalles)

        # --- Cadre principal ---
        control_frame = tk.Frame(self)
        control_frame.pack(padx=10, pady=10, fill="x")

        # Opération : count ou sum
        tk.Label(control_frame, text="Opération :").grid(row=0, column=0, sticky="w")
        operation_menu = ttk.Combobox(control_frame, textvariable=self.operation_var,
                                      values=["count", "sum"], state="readonly")
        operation_menu.grid(row=0, column=1, sticky="w")
        operation_menu.bind("<<ComboboxSelected>>", self.update_phrase)

        # Phrase dynamique
        self.phrase_label = tk.Label(control_frame, text="")
        self.phrase_label.grid(row=1, column=0, columnspan=3, pady=(5, 10), sticky="w")

        # Colonne à compter/sommer
        tk.Label(control_frame, text="Colonne :").grid(row=2, column=0, sticky="w")
        self.column_menu = ttk.Combobox(control_frame, textvariable=self.column_var, state="readonly")
        self.column_menu.grid(row=2, column=1, sticky="w")

        # Groupe : commune ou rôle
        tk.Label(control_frame, text="Grouper par :").grid(row=3, column=0, sticky="w")
        self.group_menu = ttk.Combobox(control_frame, textvariable=self.group_var, state="readonly")
        self.group_menu.grid(row=3, column=1, sticky="w")

        # Niveau de carte
        tk.Label(control_frame, text="Niveau de carte :").grid(row=4, column=0, sticky="w")
        map_level_menu = ttk.Combobox(control_frame, textvariable=self.map_level_var,
                                      values=["Commune", "Province", "Région"], state="readonly")
        map_level_menu.grid(row=4, column=1, sticky="w")

        # Palette de couleurs
        tk.Label(control_frame, text="Palette de couleurs :").grid(row=5, column=0, sticky="w")
        cmap_options = ["OrRd", "Blues", "Greens", "Purples", "YlOrBr", "coolwarm", "plasma", "viridis", "cividis", "personnalisée"]
        cmap_menu = ttk.Combobox(control_frame, textvariable=self.colormap_var, values=cmap_options, state="readonly")
        cmap_menu.grid(row=5, column=1, sticky="w")
        cmap_menu.bind("<<ComboboxSelected>>", self.toggle_custom_color_frame)

        # Bouton Afficher
        tk.Button(control_frame, text="Afficher la carte", command=self.generate_and_draw_map).grid(row=6, column=0, columnspan=2, pady=10)

        # Bouton Refresh
        tk.Button(control_frame, text="🔄 Rafraîchir", command=self.refresh_fields).grid(row=7, column=0, columnspan=2, pady=(0, 10))

        # Gestion des couleurs personnalisées
        self.custom_color_label = tk.Label(control_frame, text="Couleurs personnalisées :")
        self.custom_color_label.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        self.color_frame = tk.Frame(control_frame)
        self.color_frame.grid(row=9, column=0, columnspan=2, sticky="ew")
        self.add_color_button = tk.Button(control_frame, text="Ajouter une couleur", command=self.add_color)
        self.add_color_button.grid(row=10, column=0, pady=5)
        self.remove_color_button = tk.Button(control_frame, text="Supprimer la dernière couleur", command=self.remove_color)
        self.remove_color_button.grid(row=10, column=1, pady=5)

        self.toggle_custom_color_frame()
        self.plot_gdf = None

    def toggle_custom_color_frame(self, *_):
        show = self.colormap_var.get() == "personnalisée"
        for widget in [self.custom_color_label, self.color_frame, self.add_color_button, self.remove_color_button]:
            widget.grid() if show else widget.grid_remove()

    def add_color(self):
        color = colorchooser.askcolor(title="Choisir une couleur")[1]
        if color:
            self.custom_colors.append(color)
            self.refresh_color_preview()

    def remove_color(self):
        if self.custom_colors:
            self.custom_colors.pop()
            self.refresh_color_preview()

    def refresh_color_preview(self):
        for widget in self.color_frame.winfo_children():
            widget.destroy()
        for c in self.custom_colors:
            label = tk.Label(self.color_frame, text=c, bg=c, fg="white", width=10)
            label.pack(side="left", padx=2, pady=2)

    def set_controller(self, controller):
        self.controller = controller
        self.populate_dynamic_fields()
        self.update_phrase()

    def populate_dynamic_fields(self):
        metadata = self.controller.data_manager.sheet_column_metadata
        selected_columns = [key[2] for key, meta in metadata.items() if meta.get("selected")]
        self.column_menu["values"] = selected_columns
        if selected_columns:
            self.column_var.set(selected_columns[0])

        roles = list(self.controller.data_manager.role_columns.keys())
        self.group_menu["values"] = ["Commune"] + roles
        self.group_var.set("Commune")

    def update_phrase(self, *_):
        op = self.operation_var.get()
        col = self.column_var.get() or "..."
        group = self.group_var.get() or "..."
        if op == "count":
            phrase = f"Le compte des « {col} » à afficher par « {group} »"
        elif op == "sum":
            phrase = f"Le total des « {col} » à afficher par « {group} »"
        else:
            phrase = ""
        self.phrase_label.config(text=phrase)

    def refresh_fields(self):
        if self.controller:
            self.populate_dynamic_fields()
            self.update_phrase()

    def generate_and_draw_map(self):
        try:
            self.plot_gdf = generate_plot_gdf(
                self.controller,
                self.operation_var.get(),
                self.column_var.get(),
                self.group_var.get(),
                self.map_level_var.get(),
                self.colormap_var.get(),
                self.custom_colors
            )

            self.draw_map()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur génération carte : {e}")

    def draw_map(self):
        op = self.operation_var.get()
        col = self.column_var.get()
        group = self.group_var.get()
        cmap_choice = self.colormap_var.get()

        if self.plot_gdf is None:
            messagebox.showerror("Erreur", "Aucune carte à afficher. Veuillez générer les données d'abord.")
            return

        try:
            fig, ax = plt.subplots(figsize=(10, 10))

            if cmap_choice == "personnalisée" and self.custom_colors:
                values = self.plot_gdf["value"].fillna(0).astype(float)
                bins = np.linspace(values.min(), values.max(), len(self.custom_colors) + 1)
                categories = np.digitize(values, bins, right=False) - 1
                categories = np.clip(categories, 0, len(self.custom_colors) - 1)

                self.plot_gdf["_color"] = [self.custom_colors[i] for i in categories]
                self.plot_gdf["_bin"] = categories

                # Génération des étiquettes de légende
                legend_labels = [f"{int(bins[i])} - {int(bins[i + 1])}" for i in range(len(self.custom_colors))]
                handles = [mpatches.Patch(color=self.custom_colors[i], label=legend_labels[i]) for i in range(len(self.custom_colors))]

                self.plot_gdf.plot(ax=ax, color=self.plot_gdf["_color"], edgecolor="black")
                ax.legend(handles=handles, title="Valeurs", loc="lower left")

            else:
                self.plot_gdf.plot(column="value", ax=ax, cmap=cmap_choice, legend=True, edgecolor="black")

            ax.set_title(f"{op.upper()} de '{col}' par {group}", fontsize=14)
            ax.set_aspect("equal")
            ax.set_axis_off()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur affichage carte : {e}")

