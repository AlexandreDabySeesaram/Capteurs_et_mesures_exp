
# Méthodes expérimentales : labs

* Site : [https://alexandredabyseesaram.github.io/Tracking_video/](https://alexandredabyseesaram.github.io/Tracking_video/)

## Organisation

```
_quarto.yml, index.qmd   site Quarto : accueil (tuiles Cours / Labs), cours.qmd (vidéos), labs.qmd (tuiles des labs)
assets/                  styles et images du site
tools/                   build_marimo.py (notebooks à compléter -> site WASM) et sa documentation
labs/
  _modele/               squelette à copier pour créer un nouveau lab
  lab01_tracking/        Lab 1 : suivi d'objet dans une vidéo
    index.qmd            page du lab
    *.ipynb, *.py        notebooks de démonstration d'origine
    Resources/           vidéo du pendule, bibliographie
    marimo/              notebooks marimo à compléter (maîtres, versions étudiant, corrigés, site WASM)
```

Voir `tools/README_marimo.md` et `labs/_modele/README.md`.

## Lab 1 : run the tracking notebooks locally

To run the notebook locally you'll need to setup an environment with opencv, matplotlib and numpy. Follow these steps to create a Conda environment named `tracking-ev` with Python 3.13 and all required packages:

```bash
# Create a new conda environment with Python 3.13
conda create -n tracking-env python=3.13 -y

# Activate the environment
conda activate tracking-env

# Install required packages: OpenCV (with contrib modules), NumPy, and Matplotlib
conda install -c conda-forge opencv=4.8.0 matplotlib numpy -y
```