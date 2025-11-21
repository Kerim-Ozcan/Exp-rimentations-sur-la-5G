# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#bibliothèques
import pandas as pd
import matplotlib.pyplot as plt
import webview
import seaborn as sns
import folium
import chardet
from folium.plugins import MarkerCluster
import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Config de l'affichage
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class Application5G(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyse des Expérimentations 5G en France") # Config de l'interface
        self.geometry("2000x2000")
        self.creer_widgt()
        self.load_data() # chargement des données
        self.show_charts() # Chargement des char (graphiques)
        
    def creer_widgt(self):
        # page principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        titre_page = ttk.Label(main_frame, text=" Analyse des Expérimentations 5G en France", 
                               font=("Arial", 16, "bold"))
        titre_page.pack(pady=10)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Boutons
        ttk.Button(button_frame, text="Afficher les graphiques", command=self.show_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Afficher la carte", command=self.show_map).pack(side=tk.LEFT, padx=5)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet de lancement
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Graphiques")
        
    def load_data(self): #chargement du fichier CSV
        try:
            chemin = 'experimentations_5G.csv'
            if not os.path.exists(chemin):
                messagebox.showerror("impossible de charger les données")
                return
            self.df = load_and_clean_data(chemin)
            self.show_map()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")

    def show_map(self):
        try:
            # vide les élément de la fenetres
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
            self.notebook.add(self.charts_frame, text="Carte")
            carte = create_interactive_map(self.df) # opn viens charger la map dans la fenetre vide
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html") # 
            carte.save(temp_file.name)
            temp_file.close()
            # utilisation de webview pour afficher la map
            webview.create_window("Carte des expérimentations 5G", temp_file.name, width=1000, height=700)
            webview.start()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger la carte: {e}")

    def show_charts(self):
        try:            
            # Nettoyage du frame des graphiques
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
            fig = create_complete_charts(self.df)
            self.notebook.add(self.charts_frame, text="Graphiques")
            
            # Intégration dans Tkinter
            canvas = FigureCanvasTkAgg(fig, self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Ajouter un bouton pour sauvegarder
            save_frame = ttk.Frame(self.charts_frame)
            save_frame.pack(fill=tk.X, pady=5)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des graphiques: {e}")


    
    def save_charts(self, fig):
        """Sauvegarde les graphiques"""
        try:
            fig.savefig('analyses_5g_complete.png', dpi=300, bbox_inches='tight')
            messagebox.showinfo("Succès", "Graphiques sauvegardés dans 'analyses_5g_complete.png'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

# Fonctions d'analyse
def load_and_clean_data(file_path):
    # Détection de l'encodage (évite les problèmes de lecture...)
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    # chargement params spécifiques
    pf = pd.read_csv(file_path, encoding=encoding, sep=';', quotechar='"',low_memory=False)
    # Conversion des coordonnées géographiques (latitude, longitude)
    pf['Latitude'] = pf['Latitude'].astype(str).str.replace(',', '.').astype(float)
    pf['Longitude'] = pf['Longitude'].astype(str).str.replace(',', '.').astype(float)
    print(f"Données chargées : {len(pf)} expérimentations")
    return pf

def create_interactive_map(pf):
    # Filtrage des données avec coordonnées valides
    valid_coords = pf.dropna(subset=['Latitude', 'Longitude'])
    # Création d'une carte centrée sur la France
    france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    # Cluster pour gérer les marqueurs
    marker_cluster = MarkerCluster().add_to(france_map)
    # Couleurs par type de bande de fréquence
    frequency_colors = {'3,8 GHz': 'red','2,6 GHz TDD': 'blue', '26 GHz': 'green'}
    # Ajout des marqueurs pour chaque site valide
    for idx, row in valid_coords.iterrows():
        bande = row['Bande de fréquences']# Couleur selon la bande de fréquence
        color = frequency_colors.get(bande, 'gray')
        tech_columns = [col for col in pf.columns if col.startswith('Techno - ')]# Technologies activées
        technologies = [tech.replace('Techno - ', '') for tech in tech_columns if row[tech] == 1]
        # Usages
        usage_columns = [col for col in pf.columns if col.startswith('Usage - ')]
        usages = [usage.replace('Usage - ', '') for usage in usage_columns if row[usage] == 1]
        popup_content = f"""
        <div style="width: 300px;">
            <h4>{row['Expérimentateur']}</h4>
            <b> Lieu:</b> {row['Commune']}, {row['Région']}<br>
            <b> Bande:</b> {bande}<br>
            <b> Période:</b> {row['Début']} à {row['Fin']}<br>
            <b> Technologies:</b> {', '.join(technologies[:3])}{'...' if len(technologies) > 3 else ''}<br>
            <b> Usages:</b> {', '.join(usages[:3])}{'...' if len(usages) > 3 else ''}
        </div>
        """        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=400),
            tooltip=f"{row['Expérimentateur']} - {row['Commune']}",
            icon=folium.Icon(color=color, icon='signal', prefix='fa')
        ).add_to(marker_cluster)
    return france_map

def create_complete_charts(pf):
    # Configuration des graphiques - TAILLE RÉDUITE
    fig = plt.figure(figsize=(12, 8))  # Réduit de 15,12 à 12,8
    
    # 1. Répartition par régions
    ax1 = plt.subplot(2, 3, 1)
    region_data = pf['Région'].value_counts()
    bars = ax1.bar(range(len(region_data)), region_data.values, color='skyblue', alpha=0.8)
    ax1.set_title('Expérimentations par région', fontsize=10, fontweight='bold')  # Taille police réduite
    ax1.set_xticks(range(len(region_data)))
    ax1.set_xticklabels(region_data.index, rotation=50, ha='right', fontsize=7)  # Police plus petite
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylabel('Nombre d\'expérimentations', fontsize=8)
    # Ajout des valeurs sur les barres
    for bar, value in zip(bars, region_data.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(value), ha='center', va='bottom', fontsize=7)  # Police réduite
    
    # 2. Top expérimentateurs
    ax2 = plt.subplot(2, 3, 2)
    top_experimentateurs = pf['Expérimentateur'].value_counts().head(10)
    bars = ax2.bar(range(len(top_experimentateurs)), top_experimentateurs.values, color='lightcoral', alpha=0.8)
    ax2.set_title('Top 10 des expérimentateurs', fontsize=10, fontweight='bold')
    ax2.set_xticks(range(len(top_experimentateurs)))
    ax2.set_xticklabels(top_experimentateurs.index, rotation=45, ha='right', fontsize=7)
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Répartition par bande de fréquences
    ax3 = plt.subplot(2, 3, 3)
    frequences = pf['Bande de fréquences'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    wedges, texts, autotexts = ax3.pie(frequences.values, labels=frequences.index, autopct='%1.1f%%', startangle=90, colors=colors)
    ax3.set_title('Bandes de fréquences', fontsize=10, fontweight='bold')
    # Réduire la taille de police du pie chart
    for text in texts:
        text.set_fontsize(7)
    for autotext in autotexts:
        autotext.set_fontsize(7)
    
    # 4. Technologies utilisées
    ax4 = plt.subplot(2, 3, 4)
    tech_columns = [col for col in pf.columns if col.startswith('Techno - ')]
    tech_counts = {col.replace('Techno - ', ''): pf[col].sum() for col in tech_columns}
    tech_names = list(tech_counts.keys())
    tech_values = list(tech_counts.values())
    
    bars = ax4.barh(tech_names, tech_values, color='lightgreen', alpha=0.8)
    ax4.set_title('Technologies utilisées', fontsize=10, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    ax4.set_xlabel('Nombre d\'expérimentations', fontsize=8)
    ax4.tick_params(axis='y', labelsize=7)  # Réduire taille des labels y
    
    # Ajout des valeurs sur les barres horizontales
    for bar, value in zip(bars, tech_values):
        ax4.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                str(value), ha='left', va='center', fontsize=7)
    
    # 5. Cas d'usage
    ax5 = plt.subplot(2, 3, 5)
    usage_columns = [col for col in pf.columns if col.startswith('Usage - ')]
    usage_counts = {col.replace('Usage - ', ''): pf[col].sum() for col in usage_columns}
    usage_names = list(usage_counts.keys())
    usage_values = list(usage_counts.values())
    
    bars = ax5.barh(usage_names, usage_values, color='gold', alpha=0.8)
    ax5.set_title('Cas d\'usage', fontsize=10, fontweight='bold')
    ax5.grid(axis='x', alpha=0.3)
    ax5.set_xlabel('Nombre d\'expérimentations', fontsize=8)
    ax5.tick_params(axis='y', labelsize=7)  # Réduire taille des labels y
    
    # 6. Statistiques temporelles
    ax6 = plt.subplot(2, 3, 6)
    pf['Année_début'] = pd.to_datetime(pf['Début']).dt.year
    yearly_stats = pf['Année_début'].value_counts().sort_index()
    ax6.plot(yearly_stats.index, yearly_stats.values, marker='o', linewidth=2, markersize=4, color='purple', alpha=0.8)  # Marqueurs réduits
    ax6.set_title('Évolution par année', fontsize=10, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.set_xlabel('Année', fontsize=8)
    ax6.set_ylabel('Nombre d\'expérimentations', fontsize=8)
    ax6.tick_params(axis='both', labelsize=7)  # Réduire taille des ticks
    
    # Ajout des valeurs sur le graphique temporel
    for year, count in zip(yearly_stats.index, yearly_stats.values):
        ax6.text(year, count + 0.5, str(count), ha='center', va='bottom', fontsize=7)
    
    plt.tight_layout(pad=2.0)  # Ajout de padding pour éviter le chevauchement
    return fig
    
if __name__ == "__main__":
    app = Application5G()
    app.mainloop()