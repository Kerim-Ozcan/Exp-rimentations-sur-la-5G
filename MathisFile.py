import folium
import webview
import os
import random
import tkinter as tk
from tkinter import ttk



# Création de la carte
carte = folium.Map(location=[46.078025, 6.409053], zoom_start=13)

fenetre= tk.Tk()
fenetre.geometry("600x800")
fenetre.title("exploration des widgets")
frm = ttk.Frame(fenetre)
frm.grid()

text=ttk.Label(frm, text="text 2")
text.grid(column=0, row=0, padx=100, pady=15)






# Sauvegarde de la carte
def fenetremap ():
    # folium.Marker(location=[46.078025, 6.409053], popup="test!").add_to(carte)

    # Coordonnées de base
    BatD = [46.549075, 3.288174]
    
    titre = "Bâtiment D"
    couleur = "darkpurple"
    
    # Ajout de 10 marqueurs aléatoires autour du point de base
    for i in range(100):
        lat = BatD[0] + random.uniform(-10.001, 10.001)
        lon = BatD[1] + random.uniform(-10.01, 10.001)
        folium.Marker(
            location=[lat, lon],
            popup=f"{titre} {i+1}",
            icon=folium.Icon(color=couleur, icon='glyphicon-home')
        ).add_to(carte)
    map_path = os.path.abspath("map.html")
    carte.save(map_path)
    window = webview.create_window("DataSetViewPro", map_path, width=800, height=600)
    webview.start()




btn1=ttk.Button(frm, text="ouvrir la map", command=fenetremap)
btn1.grid(column=1, row=1, pady=15)

fenetre.mainloop()
