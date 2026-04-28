# =============================================================================
# Projet  : Souris Virtuelle
# Auteur  : Alex Mathieu
# Fichier : menu.py — Interface graphique principale (Tkinter)
# =============================================================================

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import threading
import cv2
import os
import sys

# Ajoutez le répertoire parent au chemin Python pour permettre l'import de modules personnalisés
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from functions.virtual_mouse import virtual_mouse
from menu_fct import centrer_fenetre, theme_application, appliquer_theme, creer_fenetre_metrique, ajouter_metrique

# Dictionnaire pour suivre les caméras actuellement utilisées
cameras_utilisees = {}

# Variable pour stocker le thème actuel (jour/nuit)
theme_actuel = "nuit"


def basculer_theme():
    """
    Basculer entre le mode jour et nuit.
    """
    global theme_actuel
    if theme_actuel == "nuit":
        appliquer_theme(root, "jour")
        theme_actuel = "jour"
    else:
        appliquer_theme(root, "nuit")
        theme_actuel = "nuit"


def afficher_metriques(metrics):
    """
    Affiche les métriques dans une nouvelle fenêtre.
    """
    metrics_window = creer_fenetre_metrique(root)

    for key, value in metrics.items():
        if key == "uptime":
            value = f"{value:.2f} secondes"
        elif key in ["average_fps", "average_hand_detection_time"]:
            value = f"{value:.2f}"
        ajouter_metrique(metrics_window, key, value)


def demarrer_souris_virtuelle():
    """
    Démarre la souris virtuelle et gère l'affichage des métriques.
    """
    root.withdraw()

    num_cam = simpledialog.askinteger("Info Caméra", "Entrez le numéro de la caméra")
    largeur_cam = simpledialog.askinteger("Largeur Caméra", "Entrez la largeur de la caméra")
    hauteur_cam = simpledialog.askinteger("Hauteur Caméra", "Entrez la hauteur de la caméra")
    fps = messagebox.askquestion("FPS", "Afficher les FPS ?")
    if fps == 'yes':
        fps = True
    else:
        fps = False

    if num_cam is not None and largeur_cam is not None and hauteur_cam is not None:
        if num_cam in cameras_utilisees:
            messagebox.showinfo("Info", "Cette caméra est déjà utilisée.")
            return

        cameras_utilisees[num_cam] = True

        def run_virtual_mouse():
            metrics = virtual_mouse(num_cam, largeur_cam, hauteur_cam, fps)
            root.after(0, lambda: afficher_metriques(metrics))

        threading.Thread(target=run_virtual_mouse).start()
    else:
        messagebox.showerror("Erreur", "Veuillez entrer tous les paramètres essentiels.")

    root.deiconify()


def info_camera():
    """
    Affiche les informations de la caméra sélectionnée.
    """
    root.withdraw()

    num_cam = simpledialog.askinteger("Caméra", "Entrez le numéro de la caméra")
    cap = cv2.VideoCapture(num_cam)

    if not cap.isOpened():
        messagebox.showerror("Erreur", "Impossible d'ouvrir la capture vidéo.")
    else:
        largeur = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        hauteur = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        messagebox.showinfo("Informations vidéo", f"Largeur vidéo: {largeur}\nHauteur vidéo: {hauteur}")

    cap.release()
    root.deiconify()


# Création de la fenêtre principale
root = tk.Tk()
root.title("Souris Virtuelle")

# Agrandir l'interface (ex: 400x400)
centrer_fenetre(root, largeur=400, hauteur=400)

# Appliquer le thème par défaut
theme_application(root)

# Charger l'image et la redimensionner
image = Image.open("./ressources/poly.png")
image = image.resize((200, 200), Image.LANCZOS)
image = ImageTk.PhotoImage(image)

# Créer un label avec l'image
etiquette_image = tk.Label(root, image=image, bg='#1a237e')
etiquette_image.pack(pady=20)

# Créer un style pour les boutons
style = ttk.Style()
style.configure('TButton', font=('Inter', 12), background='#3f51b5', foreground='black')

# Créer les boutons
bouton1 = ttk.Button(root, text="Souris Virtuelle", command=demarrer_souris_virtuelle, style='TButton')
bouton2 = ttk.Button(root, text="Info Caméra", command=info_camera, style='TButton')
bouton_theme = ttk.Button(root, text="Basculer Jour/Nuit", command=basculer_theme, style='TButton')

# Positionner les boutons au milieu de la fenêtre avec rembourrage
bouton1.pack(padx=20, pady=10)
bouton2.pack(padx=20, pady=10)
bouton_theme.pack(padx=20, pady=10)

root.mainloop()