from cx_Freeze import setup, Executable

options_build_exe = {
    "packages": ["mediapipe", "cv2", "numpy"],
    "include_files": [
        "functions/",
        "ressources/",
        "menu_fct.py",
        "metrics_collection.py"
    ],
}

setup(
    name = "Souris Virtuelle",
    version = "0.2",
    author = "Alex Mathieu",
    description = "Application permettant d'utiliser une souris virtuelle avec votre doigt en utilisant la reconnaissance IA, avec suivi des métriques.",
    options = {"build_exe": options_build_exe},
    executables = [Executable("menu.py", base="Win32GUI", icon="./ressources/virtual_mouse_logo.ico")]
)

# Exécutez "python setup.py build" pour obtenir le .exe de l'application