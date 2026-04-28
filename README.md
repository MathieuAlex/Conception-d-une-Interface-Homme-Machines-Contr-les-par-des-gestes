# 🖱️ Souris Virtuelle — Contrôle de la souris par reconnaissance gestuelle en temps réel

> **Projet de vision par ordinateur** combinant intelligence artificielle, traitement d'image et interaction homme-machine sans contact physique.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-FF6F00?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)
[![Tkinter](https://img.shields.io/badge/Interface-Tkinter-2196F3?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)

---

## 🎯 Contexte & Problème

Dans de nombreux environnements (milieu médical, industrie propre, accessibilité numérique), **l'utilisation d'un périphérique physique comme la souris est une contrainte majeure** :

- 🏥 Risques de contamination en milieu hospitalier
- ♿ Inaccessibilité pour les personnes avec des limitations motrices des mains
- 🏭 Impossibilité d'interagir avec un ordinateur en portant des gants ou dans des environnements contraints

**Comment permettre à un utilisateur de contrôler son ordinateur sans toucher aucun périphérique, en utilisant uniquement sa main devant une caméra ordinaire ?**

---

## 💡 Solution — Architecture technique

Ce projet répond à cette problématique avec une solution 100 % logicielle en temps réel, basée sur la vision par ordinateur et l'apprentissage automatique.

### Pipeline de traitement

```
Flux vidéo (webcam)
      │
      ▼
┌──────────────────────────────────────┐
│  OpenCV — Capture & prétraitement    │  Retournement horizontal, conversion BGR→RGB
└──────────────────────┬───────────────┘
                       │
                       ▼
┌──────────────────────────────────────┐
│  MediaPipe Hands — Détection IA      │  21 landmarks 3D en temps réel
└──────────────────────┬───────────────┘
                       │
                       ▼
┌──────────────────────────────────────┐
│  Moteur gestuel — Interprétation     │  Mapping gestes → actions système
└──────────────────────┬───────────────┘
                       │
                       ▼
┌──────────────────────────────────────┐
│  PyAutoGUI — Contrôle OS             │  Déplacement, clic, scroll
└──────────────────────────────────────┘
```

### Correspondance gestes → actions

| Geste | Action |
|-------|--------|
| ☝️ Index levé seul | Déplacement du curseur (interpolation linéaire + lissage) |
| ✌️ Index + Majeur rapprochés (< 40px) | Clic gauche |
| 🤙 Index + Auriculaire levés | Clic droit |
| 👌 Pouce + Index < 20px | Défilement vers le bas |
| 👌 Pouce + Index entre 20–40px | Défilement vers le haut |

### Modules développés

```
📁 functions/
├── HandTrackingModuleVM.py   # Classe HandDetector — wrapper MediaPipe
│   ├── findHands()           # Détection & dessin des landmarks
│   ├── findPosition()        # Extraction des coordonnées 21 points
│   ├── fingersUp()           # Logique de reconnaissance des doigts levés
│   ├── findDistance()        # Calcul de distance euclidienne inter-landmarks
│   └── fps()                 # Affichage temps réel du framerate
│
└── virtual_mouse.py          # Moteur principal
    ├── VirtualMouseMetrics   # Système de métriques de session (clic, FPS, uptime)
    └── virtual_mouse()       # Boucle de capture et de traitement

📁 (racine)/
├── menu.py                   # Interface graphique Tkinter (thème jour/nuit)
├── menu_fct.py               # Composants UI réutilisables (centrage, métriques)
├── setup.py                  # Packaging avec cx_Freeze
└── start-app.bat             # Lanceur Windows
```

---

## 📊 Résultats & Métriques

### Performance temps réel
- ✅ **Détection MediaPipe** avec confiance minimale de 50 % pour filtrager le bruit
- ✅ **Lissage du curseur** (facteur 3) pour éliminer la tremblement naturel de la main
- ✅ **Cooldown anti-rebond** de 500 ms pour éviter les clics non intentionnels répétés
- ✅ **Zone active délimitée** (frameR = 80px) pour maximiser la précision de mapping

### Métriques de session collectées automatiquement
```python
{
  'clicks': int,                     # Clics gauche effectués
  'right_clicks': int,               # Clics droit effectués
  'scrolls': int,                    # Défilements effectués
  'average_fps': float,              # FPS moyen (stabilité du flux)
  'average_hand_detection_time': float,  # Temps de détection moyen (ms)
  'uptime': float                    # Durée totale de session (s)
}
```

---

## 🚀 Impact & Valeur ajoutée

| Dimension | Impact |
|-----------|--------|
| 🎯 **Accessibilité** | Permet aux personnes ayant une mobilité réduite des doigts d'interagir avec un PC |
| 🏥 **Hygiène** | Élimination du contact physique — applicable en milieu médical ou stérile |
| 🛠️ **Extensibilité** | Architecture modulaire : `HandDetector` réutilisable pour tout projet de vision gestuelle |
| 📦 **Déployable** | Packaging en exécutable Windows via `cx_Freeze` (aucune dépendance à installer pour l'utilisateur final) |
| 📈 **Observabilité** | Système de métriques intégré pour analyser et améliorer les performances de session |

---

## 🛠️ Technologies utilisées

| Technologie | Version | Rôle |
|------------|---------|------|
| Python | 3.10+ | Langage principal |
| OpenCV | 4.8.1 | Capture vidéo & traitement d'image |
| MediaPipe | — | Détection de main par IA (21 landmarks) |
| PyAutoGUI | 0.9.54 | Contrôle du système d'exploitation |
| Tkinter | stdlib | Interface graphique native |
| NumPy | 1.26.2 | Calcul vectoriel & interpolation |
| cx_Freeze | 6.15.16 | Packaging en exécutable |
| Pillow | 10.1.0 | Gestion des images dans l'UI |

---

## ⚙️ Installation & Lancement

### Prérequis
- Python 3.10 ou supérieur
- Une webcam fonctionnelle

### Installation

```bash
# Cloner le projet
git clone <url-du-repo>
cd souris-virtuelle

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate        # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
# Via Python
python menu.py

# Via le lanceur Windows (double-clic)
start-app.bat

# Réinitialiser l'environnement virtuel si besoin
reset-env.bat
```

### Utilisation

1. Cliquer sur **"Souris Virtuelle"** dans le menu
2. Saisir le numéro de caméra (généralement `0` pour la webcam intégrée)
3. Saisir la résolution souhaitée (ex : largeur `640`, hauteur `480`)
4. Choisir d'afficher ou non le FPS en temps réel
5. Placer la main devant la caméra et utiliser les gestes définis
6. Appuyer sur **`Espace`** pour terminer la session — les métriques s'affichent automatiquement

---

## 📂 Structure du projet

```
souris-virtuelle/
├── functions/
│   ├── HandTrackingModuleVM.py   # Module de détection gestuelle
│   └── virtual_mouse.py          # Moteur de contrôle & métriques
├── ressources/
│   └── poly.png                  # Logo de l'interface
├── menu.py                       # Point d'entrée — interface principale
├── menu_fct.py                   # Fonctions UI réutilisables
├── setup.py                      # Configuration du packaging exécutable
├── requirements.txt              # Dépendances Python
├── start-app.bat                 # Lanceur Windows
└── reset-env.bat                 # Script de réinitialisation de l'environnement
```

---

## 🔮 Pistes d'évolution

- [ ] Ajout d'un geste de **double-clic**
- [ ] Support **multi-caméra simultané** (architecture déjà amorcée dans le menu)
- [ ] Calibration automatique de la sensibilité selon la résolution de l'écran
- [ ] Export des métriques de session en **CSV / JSON** pour analyse
- [ ] Mode **accessibilité vocale** combiné à la détection gestuelle
- [ ] Interface de configuration des gestes personnalisable par l'utilisateur

---

## 👤 Auteur

**Alex Mathieu**
Projet réalisé dans le cadre du cours **Sciences Cognitives & Traitement d'Image**

> *Ce projet illustre ma capacité à concevoir une solution complète alliant vision par ordinateur, IA embarquée et interface utilisateur — du prototype au packaging déployable.*

---

*Licence : usage académique — ∂ Tous droits réservés*
