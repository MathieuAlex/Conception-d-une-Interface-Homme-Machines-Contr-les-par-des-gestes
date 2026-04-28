# =============================================================================
# Projet  : Souris Virtuelle
# Auteur  : Alex Mathieu
# Fichier : menu_fct.py — Composants UI réutilisables (thème, centrage, métriques)
# =============================================================================

import tkinter as tk
from tkinter import ttk


def appliquer_theme(root, theme):
    """
    Applique le thème jour ou nuit à l'interface Tkinter.

    :param root: La fenêtre Tkinter principale.
    :param theme: Le thème à appliquer (jour ou nuit).
    """
    if theme == "nuit":
        root.tk_setPalette(background='#1a237e', foreground='#ffffff', activeBackground='#3949ab',
                           activeForeground='#ffffff')
    elif theme == "jour":
        root.tk_setPalette(background='#ffffff', foreground='#000000', activeBackground='#bbdefb',
                           activeForeground='#000000')


def theme_application(root):
    """
    Applique le thème nuit par défaut à l'application lors du démarrage.
    """
    appliquer_theme(root, "nuit")


def centrer_fenetre(root, largeur, hauteur):
    """
    Centre la fenêtre Tkinter sur l'écran et ajuste la taille minimale et maximale.
    """
    # Obtenir les dimensions de l'écran
    largeur_ecran = root.winfo_screenwidth()
    hauteur_ecran = root.winfo_screenheight()

    # Calculer la position pour centrer la fenêtre
    x = (largeur_ecran / 2) - (largeur / 2)
    y = (hauteur_ecran / 2) - (hauteur / 2)

    # Positionner la fenêtre au centre de l'écran
    root.geometry('%dx%d+%d+%d' % (largeur, hauteur, x, y))

    # Définir la taille minimale et maximale de la fenêtre
    largeur_min = largeur - 7
    hauteur_min = hauteur - 7
    root.minsize(largeur_min, hauteur_min)


def creer_fenetre_metrique(parent):
    """
    Crée une nouvelle fenêtre pour afficher les métriques.

    :param parent: La fenêtre parente (généralement la fenêtre principale)
    :return: La nouvelle fenêtre créée
    """
    fenetre = tk.Toplevel(parent)
    fenetre.title("Métriques de la souris virtuelle")
    centrer_fenetre(fenetre, 300, 200)  # Ajustez la taille selon vos besoins
    return fenetre


def ajouter_metrique(fenetre, label, valeur):
    """
    Ajoute une métrique à la fenêtre des métriques.

    :param fenetre: La fenêtre des métriques
    :param label: Le nom de la métrique
    :param valeur: La valeur de la métrique
    """
    frame = ttk.Frame(fenetre)
    frame.pack(fill=tk.X, padx=5, pady=2)

    ttk.Label(frame, text=label).pack(side=tk.LEFT)
    ttk.Label(frame, text=str(valeur)).pack(side=tk.RIGHT)