#bibliothèques
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium  #carte interactive
from collections import Counter
import chardet
from folium.plugins import MarkerCluster
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import tempfile
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
from PIL import Image, ImageTk
import base64

# Configuration pour l'affichage
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class Application5G(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyse des Expérimentations 5G en France")
        self.geometry("1200x800")
        self.df = None
        
        # Configuration de l'interface
        self.create_widgets()
        
    def create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text=" Analyse des Expérimentations 5G en France", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Boutons simplifiés
        ttk.Button(button_frame, text=" Charger les données", 
                  command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=" Afficher les graphiques", 
                  command=self.show_charts).pack(side=tk.LEFT, padx=5)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Graphiques
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Graphiques")
        
        # Label d'attente pour les graphiques
        self.charts_waiting_label = ttk.Label(self.charts_frame, 
                                     text="Veuillez charger les données et afficher les graphiques",
                                     font=("Arial", 12))
        self.charts_waiting_label.pack(expand=True)
        
        # Onglet Carte
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Carte")
        
        # Label d'attente pour la carte
        self.map_waiting_label = ttk.Label(self.map_frame, 
                                     text="La carte sera affichée ici après le chargement des données",
                                     font=("Arial", 12))
        self.map_waiting_label.pack(expand=True)
        
    def load_data(self):
        """Charge les données depuis le fichier CSV"""
        try:
            file_path = 'experimentations_5G.csv'
            if not os.path.exists(file_path):
                messagebox.showerror("Erreur", f"Fichier {file_path} non trouvé!")
                return
                
            self.df = load_and_clean_data(file_path)
            messagebox.showinfo("Succès", "Données chargées avec succès!\nLa carte et les graphiques sont maintenant disponibles.")
            
            # Afficher automatiquement la carte
            self.show_map()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")
    
    def show_charts(self):
        """Affiche les graphiques"""
        if self.df is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger les données!")
            return
            
        try:
            # Supprimer le label d'attente
            self.charts_waiting_label.pack_forget()
            
            # Nettoyage du frame des graphiques
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
                
            # Création des graphiques
            fig = create_complete_charts(self.df)
            
            # Intégration dans Tkinter
            canvas = FigureCanvasTkAgg(fig, self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Ajouter un bouton pour sauvegarder
            save_frame = ttk.Frame(self.charts_frame)
            save_frame.pack(fill=tk.X, pady=5)
            ttk.Button(save_frame, text=" Sauvegarder les graphiques", 
                      command=lambda: self.save_charts(fig)).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des graphiques: {e}")
    
    def show_map(self):
        """Affiche la carte dans l'onglet"""
        if self.df is None:
            return
            
        try:
            # Supprimer le label d'attente
            self.map_waiting_label.pack_forget()
            
            # Nettoyage du frame de la carte
            for widget in self.map_frame.winfo_children():
                widget.destroy()
            
            # Créer un frame avec scrollbar pour la carte
            map_container = ttk.Frame(self.map_frame)
            map_container.pack(fill=tk.BOTH, expand=True)
            
            # Créer un canvas pour la carte
            canvas = tk.Canvas(map_container, bg='white')
            scrollbar_y = ttk.Scrollbar(map_container, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(map_container, orient=tk.HORIZONTAL, command=canvas.xview)
            
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Frame pour le contenu de la carte
            map_content = ttk.Frame(canvas)
            
            # Créer la carte HTML
            self.create_map_file()
            
            # Afficher la carte dans un label avec instructions
            map_label = ttk.Label(map_content, text=" Carte des Expérimentations 5G\n\n" +
                                                  "La carte a été sauvegardée dans le fichier:\n" +
                                                  "'carte_experimentations_5g.html'\n\n" +
                                                  "Ouvrez ce fichier dans votre navigateur pour voir la carte interactive.",
                                  font=("Arial", 11), justify=tk.CENTER)
            map_label.pack(pady=20)
            
            # Bouton pour ouvrir la carte
            ttk.Button(map_content, text=" Ouvrir la carte dans le navigateur", 
                      command=self.open_map_in_browser).pack(pady=10)
            
            # Bouton pour regénérer la carte
            ttk.Button(map_content, text=" Recréer la carte", 
                      command=self.regenerate_map).pack(pady=5)
            
            # Informations sur la carte
            info_text = f"""
 Informations sur la carte:
• {len(self.df)} expérimentations chargées
• {self.df[['Latitude', 'Longitude']].notna().all(axis=1).sum()} sites avec coordonnées valides
• Couleurs: Rouge=3.8GHz, Bleu=2.6GHz, Vert=26GHz

 Utilisation:
• Cliquez sur les marqueurs pour voir les détails
• Zoom avec la molette de la souris
• Déplacement en cliquant-glissant
            """
            info_label = ttk.Label(map_content, text=info_text, font=("Arial", 9), 
                                  justify=tk.LEFT)
            info_label.pack(pady=10)
            
            # Configuration du canvas scrollable
            canvas.create_window((0, 0), window=map_content, anchor="nw")
            map_content.update_idletasks()
            
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # Placement des widgets
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage de la carte: {e}")
    
    def create_map_file(self):
        """Crée le fichier HTML de la carte"""
        try:
            carte = create_interactive_map(self.df)
            carte.save('carte_experimentations_5g.html')
            print(" Carte sauvegardée : carte_experimentations_5g.html")
        except Exception as e:
            print(f" Erreur lors de la création de la carte: {e}")
    
    def open_map_in_browser(self):
        """Ouvre la carte dans le navigateur par défaut"""
        try:
            map_file = 'carte_experimentations_5g.html'
            if os.path.exists(map_file):
                webbrowser.open('file://' + os.path.realpath(map_file))
            else:
                messagebox.showwarning("Attention", "La carte n'a pas encore été générée!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture de la carte: {e}")
    
    def regenerate_map(self):
        """Regénère la carte"""
        if self.df is None:
            messagebox.showwarning("Attention", "Aucune donnée chargée!")
            return
            
        try:
            self.create_map_file()
            messagebox.showinfo("Succès", "Carte regénérée avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la regénération: {e}")
    
    def save_charts(self, fig):
        """Sauvegarde les graphiques"""
        try:
            fig.savefig('analyses_5g_complete.png', dpi=300, bbox_inches='tight')
            messagebox.showinfo("Succès", "Graphiques sauvegardés dans 'analyses_5g_complete.png'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

# Fonctions d'analyse
def load_and_clean_data(file_path):
    """Charge et nettoie les données du fichier CSV"""
    # Détection de l'encodage
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    
    # Chargement avec les paramètres spécifiques
    df = pd.read_csv(file_path, 
                    encoding=encoding,  
                    sep=';',
                    quotechar='"',
                    low_memory=False)
    
    # Conversion des coordonnées géographiques (format français avec virgules)
    df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
    df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)
    
    print(f"✅ Données chargées : {len(df)} expérimentations")
    return df

def create_interactive_map(df):
    """Crée une carte interactive des expérimentations"""
    # Filtrage des données avec coordonnées valides
    valid_coords = df.dropna(subset=['Latitude', 'Longitude'])
    
    # Création d'une carte centrée sur la France
    france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    
    # Cluster pour gérer les marqueurs
    marker_cluster = MarkerCluster().add_to(france_map)
    
    # Couleurs par type de bande de fréquence
    frequency_colors = {
        '3,8 GHz': 'red',
        '2,6 GHz TDD': 'blue', 
        '26 GHz': 'green'
    }
    
    # Ajout des marqueurs pour chaque site valide
    for idx, row in valid_coords.iterrows():
        # Couleur selon la bande de fréquence
        bande = row['Bande de fréquences']
        color = frequency_colors.get(bande, 'gray')
        
        # Technologies activées
        tech_columns = [col for col in df.columns if col.startswith('Techno - ')]
        technologies = [tech.replace('Techno - ', '') for tech in tech_columns if row[tech] == 1]
        
        # Usages
        usage_columns = [col for col in df.columns if col.startswith('Usage - ')]
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

def create_complete_charts(df):
    """Crée un ensemble complet de graphiques"""
    # Configuration des graphiques
    fig = plt.figure(figsize=(15, 12))
    
    # 1. Répartition par région
    ax1 = plt.subplot(2, 3, 1)
    region_data = df['Région'].value_counts()
    bars = ax1.bar(range(len(region_data)), region_data.values, color='skyblue', alpha=0.8)
    ax1.set_title('Expérimentations par région', fontsize=12, fontweight='bold')
    ax1.set_xticks(range(len(region_data)))
    ax1.set_xticklabels(region_data.index, rotation=45, ha='right', fontsize=8)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylabel('Nombre d\'expérimentations')
    
    # Ajout des valeurs sur les barres
    for bar, value in zip(bars, region_data.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(value), ha='center', va='bottom', fontsize=8)
    
    # 2. Top expérimentateurs
    ax2 = plt.subplot(2, 3, 2)
    top_experimentateurs = df['Expérimentateur'].value_counts().head(10)
    bars = ax2.bar(range(len(top_experimentateurs)), top_experimentateurs.values, 
                  color='lightcoral', alpha=0.8)
    ax2.set_title('Top 10 des expérimentateurs', fontsize=12, fontweight='bold')
    ax2.set_xticks(range(len(top_experimentateurs)))
    ax2.set_xticklabels(top_experimentateurs.index, rotation=45, ha='right', fontsize=8)
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Répartition par bande de fréquences
    ax3 = plt.subplot(2, 3, 3)
    frequences = df['Bande de fréquences'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    wedges, texts, autotexts = ax3.pie(frequences.values, labels=frequences.index, 
                                      autopct='%1.1f%%', startangle=90, colors=colors)
    ax3.set_title('Bandes de fréquences', fontsize=12, fontweight='bold')
    
    # 4. Technologies utilisées
    ax4 = plt.subplot(2, 3, 4)
    tech_columns = [col for col in df.columns if col.startswith('Techno - ')]
    tech_counts = {col.replace('Techno - ', ''): df[col].sum() for col in tech_columns}
    tech_names = list(tech_counts.keys())
    tech_values = list(tech_counts.values())
    
    bars = ax4.barh(tech_names, tech_values, color='lightgreen', alpha=0.8)
    ax4.set_title('Technologies utilisées', fontsize=12, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    ax4.set_xlabel('Nombre d\'expérimentations')
    
    # Ajout des valeurs sur les barres horizontales
    for bar, value in zip(bars, tech_values):
        ax4.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                str(value), ha='left', va='center', fontsize=8)
    
    # 5. Cas d'usage
    ax5 = plt.subplot(2, 3, 5)
    usage_columns = [col for col in df.columns if col.startswith('Usage - ')]
    usage_counts = {col.replace('Usage - ', ''): df[col].sum() for col in usage_columns}
    usage_names = list(usage_counts.keys())
    usage_values = list(usage_counts.values())
    
    bars = ax5.barh(usage_names, usage_values, color='gold', alpha=0.8)
    ax5.set_title('Cas d\'usage', fontsize=12, fontweight='bold')
    ax5.grid(axis='x', alpha=0.3)
    ax5.set_xlabel('Nombre d\'expérimentations')
    
    # 6. Statistiques temporelles
    ax6 = plt.subplot(2, 3, 6)
    df['Année_début'] = pd.to_datetime(df['Début']).dt.year
    yearly_stats = df['Année_début'].value_counts().sort_index()
    ax6.plot(yearly_stats.index, yearly_stats.values, marker='o', linewidth=2, 
            markersize=6, color='purple', alpha=0.8)
    ax6.set_title('Évolution par année', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.set_xlabel('Année')
    ax6.set_ylabel('Nombre d\'expérimentations')
    
    # Ajout des valeurs sur le graphique temporel
    for year, count in zip(yearly_stats.index, yearly_stats.values):
        ax6.text(year, count + 0.5, str(count), ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return fig

# Lancement de l'application
if __name__ == "__main__":
    app = Application5G()
    app.mainloop()