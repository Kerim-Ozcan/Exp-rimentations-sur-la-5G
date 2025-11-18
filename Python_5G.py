import pandas as pd
import matplotlib.pyplot as plt
import folium
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from folium.plugins import MarkerCluster

class Application5G(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Carte 5G France")
        self.geometry("1000x700")
        self.df = None
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(main_frame, text="Charger données", command=self.load_data).pack(pady=5)
        ttk.Button(main_frame, text="Voir stats", command=self.show_charts).pack(pady=5)
        ttk.Button(main_frame, text="Créer carte", command=self.show_map).pack(pady=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.charts_frame = ttk.Frame(self.notebook)
        self.map_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Stats")
        self.notebook.add(self.map_frame, text="Carte")
    
    def load_data(self):
        try:
            self.df = pd.read_csv('experimentations_5G.csv', sep=';', encoding='latin-1')
            self.df['Latitude'] = self.df['Latitude'].str.replace(',', '.').astype(float)
            self.df['Longitude'] = self.df['Longitude'].str.replace(',', '.').astype(float)
            messagebox.showinfo("OK", f"{len(self.df)} données chargées")
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème: {e}")
    
    def show_charts(self):
        if self.df is None:
            messagebox.showwarning("Oops", "Charge les données d'abord!")
            return
            
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        self.df['Région'].value_counts().head(10).plot(kind='bar', ax=axes[0,0], color='skyblue')
        axes[0,0].set_title('Top Régions')
        
        self.df['Bande de fréquences'].value_counts().plot(kind='pie', ax=axes[0,1], autopct='%1.1f%%')
        axes[0,1].set_title('Fréquences')
        
        tech_cols = [col for col in self.df.columns if col.startswith('Techno - ')]
        tech_data = {col.replace('Techno - ', ''): self.df[col].sum() for col in tech_cols}
        pd.Series(tech_data).plot(kind='barh', ax=axes[1,0], color='lightgreen')
        axes[1,0].set_title('Technos')
        
        self.df['Année'] = pd.to_datetime(self.df['Début']).dt.year
        self.df['Année'].value_counts().sort_index().plot(kind='line', ax=axes[1,1], marker='o')
        axes[1,1].set_title('Évolution')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_map(self):
        if self.df is None:
            messagebox.showwarning("Oops", "Charge les données d'abord!")
            return
            
        for widget in self.map_frame.winfo_children():
            widget.destroy()
            
        valid_coords = self.df.dropna(subset=['Latitude', 'Longitude'])
        carte = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
        marker_cluster = MarkerCluster().add_to(carte)
        
        for _, row in valid_coords.iterrows():
            # Infos détaillées pour le popup
            tech_columns = [col for col in self.df.columns if col.startswith('Techno - ')]
            technologies = [tech_col.replace('Techno - ', '') for tech_col in tech_columns 
                          if tech_col in row and row[tech_col] == 1]
            
            usage_columns = [col for col in self.df.columns if col.startswith('Usage - ')]
            usages = [usage_col.replace('Usage - ', '') for usage_col in usage_columns 
                     if usage_col in row and row[usage_col] == 1]
            
            popup_content = f"""
            <div style="width: 300px;">
                <h3>{row['Expérimentateur']}</h3>
                <p><b>Lieu:</b> {row['Commune']}, {row['Région']}</p>
                <p><b>Fréquence:</b> {row['Bande de fréquences']}</p>
                <p><b>Période:</b> {row['Début']} à {row['Fin']}</p>
                <p><b>Technos:</b> {', '.join(technologies[:3])}</p>
                <p><b>Usages:</b> {', '.join(usages[:3])}</p>
            </div>
            """
            
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_content, max_width=400),
                tooltip=row['Expérimentateur'],
                icon=folium.Icon(color='red', icon='wifi')
            ).add_to(marker_cluster)
        
        carte.save('carte_5g.html')
        
        ttk.Label(self.map_frame, text="Carte créée: carte_5g.html").pack(pady=20)
        ttk.Button(self.map_frame, text="Ouvrir la carte", 
                  command=lambda: webbrowser.open('carte_5g.html')).pack()

if __name__ == "__main__":
    app = Application5G()
    app.mainloop()