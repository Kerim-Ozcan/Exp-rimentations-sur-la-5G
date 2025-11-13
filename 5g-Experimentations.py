# -*- coding: utf-8 -*-
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
import tempfile
import os
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        title_label = ttk.Label(main_frame, text="📡 Analyse des Expérimentations 5G en France", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Boutons
        ttk.Button(button_frame, text="📁 Charger les données", 
                  command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗺️ Afficher la carte", 
                  command=self.show_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📈 Graphiques", 
                  command=self.show_charts).pack(side=tk.LEFT, padx=5)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Résultats
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Résultats")
        
        # Text widget pour afficher les résultats
        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, width=100, height=30)
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Onglet Carte
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.map_frame, text="Carte")
        
        # Label pour la carte (sera remplacé par le navigateur web)
        self.map_label = ttk.Label(self.map_frame, text="La carte s'affichera ici après analyse", 
                                  font=("Arial", 12))
        self.map_label.pack(expand=True)
        
        # Onglet Graphiques
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Graphiques")
        
    def load_data(self):
        """Charge les données depuis le fichier CSV"""
        try:
            file_path = 'experimentations_5G.csv'
            if not os.path.exists(file_path):
                messagebox.showerror("Erreur", f"Fichier {file_path} non trouvé!")
                return
                
            self.df = load_and_clean_data(file_path)
            self.results_text.insert(tk.END, "✅ Données chargées avec succès!\n\n")
            messagebox.showinfo("Succès", "Données chargées avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {e}")
    
            
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "🔍 ANALYSE EN COURS...\n")
            self.results_text.insert(tk.END, "="*50 + "\n\n")
            
            # Analyses
            region_stats = analyze_by_region(self.df)
            tech_data = analyze_technologies(self.df)
            usage_data = analyze_usages(self.df)
            
            # Affichage dans la textbox
            self.results_text.insert(tk.END, "📊 RÉSULTATS DE L'ANALYSE\n")
            self.results_text.insert(tk.END, "="*50 + "\n\n")
            
            self.results_text.insert(tk.END, "RÉGIONS:\n")
            for region, count in region_stats.items():
                self.results_text.insert(tk.END, f"• {region}: {count} expérimentations\n")
            
            self.results_text.insert(tk.END, "\nTECHNOLOGIES:\n")
            for tech_name, count, percentage in tech_data:
                self.results_text.insert(tk.END, f"• {tech_name}: {count} ({percentage:.1f}%)\n")
                
            self.results_text.insert(tk.END, "\nUSAGES:\n")
            for usage_name, count, percentage in usage_data:
                self.results_text.insert(tk.END, f"• {usage_name}: {count} ({percentage:.1f}%)\n")
                
            messagebox.showinfo("Succès", "Analyse terminée avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {e}")
    
    def show_map(self):
        """Affiche la carte interactive"""
        if self.df is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger les données!")
            return
            
        try:
            # Création de la carte
            carte = create_interactive_map(self.df)
            
            # Sauvegarde temporaire pour affichage
            temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
            carte.save(temp_file.name)
            
            # Ouverture dans le navigateur par défaut
            webbrowser.open('file://' + os.path.realpath(temp_file.name))
            
            messagebox.showinfo("Carte", "La carte s'ouvre dans votre navigateur!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la carte: {e}")
    
    def show_charts(self):
        """Affiche les graphiques"""
        if self.df is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger les données!")
            return
            
        try:
            # Nettoyage du frame des graphiques
            for widget in self.charts_frame.winfo_children():
                widget.destroy()
                
            tech_data = analyze_technologies(self.df)
            usage_data = analyze_usages(self.df)
            
            # Création des graphiques
            fig = create_tkinter_charts(self.df, tech_data, usage_data)
            
            # Intégration dans Tkinter
            canvas = FigureCanvasTkAgg(fig, self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création des graphiques: {e}")
            
        try:
            # Création d'une nouvelle fenêtre pour le rapport
            report_window = tk.Toplevel(self)
            report_window.title("Rapport Synthétique")
            report_window.geometry("600x400")
            
            text_widget = tk.Text(report_window, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Génération du rapport
            report_text = generate_detailed_report(self.df)
            text_widget.insert(tk.END, report_text)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du rapport: {e}")

# Fonctions d'analyse (adaptées pour Tkinter)
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
    
    return df

def analyze_by_region(df):
    """Analyse les statistiques par région"""
    return df['Région'].value_counts()

def analyze_technologies(df):
    """Analyse des technologies 5G utilisées"""
    tech_columns = [col for col in df.columns if col.startswith('Techno - ')]
    
    tech_data = []
    for tech_col in tech_columns:
        tech_name = tech_col.replace('Techno - ', '')
        count = df[tech_col].sum()
        percentage = (count / len(df)) * 100
        tech_data.append((tech_name, count, percentage))
    
    return tech_data

def analyze_usages(df):
    """Analyse des cas d'usage"""
    usage_columns = [col for col in df.columns if col.startswith('Usage - ')]
    
    usage_data = []
    for usage_col in usage_columns:
        usage_name = usage_col.replace('Usage - ', '')
        count = df[usage_col].sum()
        percentage = (count / len(df)) * 100
        usage_data.append((usage_name, count, percentage))
    
    return usage_data

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
            <b>📍 Lieu:</b> {row['Commune']}, {row['Région']}<br>
            <b>📡 Bande:</b> {bande}<br>
            <b>📅 Période:</b> {row['Début']} à {row['Fin']}<br>
            <b>🔧 Technologies:</b> {', '.join(technologies[:3])}{'...' if len(technologies) > 3 else ''}<br>
            <b>🎯 Usages:</b> {', '.join(usages[:3])}{'...' if len(usages) > 3 else ''}
        </div>
        """
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=400),
            tooltip=f"{row['Expérimentateur']} - {row['Commune']}",
            icon=folium.Icon(color=color, icon='signal', prefix='fa')
        ).add_to(marker_cluster)
    
    return france_map

def create_tkinter_charts(df, tech_data, usage_data):
    """Crée les graphiques pour Tkinter"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Graphique par région
    region_data = df['Région'].value_counts()
    bars = axes[0,0].bar(range(len(region_data)), region_data.values, color='skyblue')
    axes[0,0].set_title('Expérimentations par région', fontsize=12, fontweight='bold')
    axes[0,0].set_xticks(range(len(region_data)))
    axes[0,0].set_xticklabels(region_data.index, rotation=45, ha='right', fontsize=8)
    axes[0,0].grid(axis='y', alpha=0.3)
    
    # 2. Top expérimentateurs
    top_experimentateurs = df['Expérimentateur'].value_counts().head(8)
    bars = axes[0,1].bar(range(len(top_experimentateurs)), top_experimentateurs.values, color='lightcoral')
    axes[0,1].set_title('Top expérimentateurs', fontsize=12, fontweight='bold')
    axes[0,1].set_xticks(range(len(top_experimentateurs)))
    axes[0,1].set_xticklabels(top_experimentateurs.index, rotation=45, ha='right', fontsize=8)
    axes[0,1].grid(axis='y', alpha=0.3)
    
    # 3. Répartition par bande de fréquences
    frequences = df['Bande de fréquences'].value_counts()
    axes[1,0].pie(frequences.values, labels=frequences.index, autopct='%1.1f%%', 
                  startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    axes[1,0].set_title('Bandes de fréquences', fontsize=12, fontweight='bold')
    
    # 4. Technologies les plus utilisées
    tech_names = [item[0] for item in tech_data]
    tech_values = [item[1] for item in tech_data]
    
    bars = axes[1,1].barh(tech_names, tech_values, color='lightgreen')
    axes[1,1].set_title('Technologies utilisées', fontsize=12, fontweight='bold')
    axes[1,1].grid(axis='x', alpha=0.3)
    axes[1,1].tick_params(axis='y', labelsize=8)
    
    plt.tight_layout()
    return fig


# Lancement de l'application
if __name__ == "__main__":
    app = Application5G()
    app.mainloop()

