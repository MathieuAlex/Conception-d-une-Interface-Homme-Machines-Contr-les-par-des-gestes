@echo off
REM ========================
REM Script de réinitialisation d'un environnement virtuel Python
REM Par exemple pour ton projet : Souris Virtuel - Copie
REM ========================

echo.
echo [1/4] Suppression de l'ancien environnement virtuel...
rmdir /S /Q .env

echo.
echo [2/4] Création d'un nouvel environnement virtuel...
python -m venv .env

if errorlevel 1 (
    echo [ERREUR] La création de l'environnement a échoué. Vérifie que Python est bien installé.
    pause
    exit /b 1
)

echo.
echo [3/4] Activation de l'environnement et installation des dépendances...
call .env\Scripts\activate
pip install --upgrade pip

if exist requirements.txt (
    pip install -r requirements.txt
    echo [OK] Les paquets ont été installés à partir de requirements.txt.
) else (
    echo [INFO] Aucun fichier requirements.txt trouvé. Installation manuelle nécessaire.
)

echo.
echo [4/4] Environnement prêt. Tu peux maintenant lancer ton projet.
pause
