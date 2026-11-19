
# Méthodes expérimentales : labs

* Site : [https://alexandredabyseesaram.github.io/Tracking_video/](https://alexandredabyseesaram.github.io/Tracking_video/)

## Organisation

```
_quarto.yml, index.qmd   site Quarto : accueil (tuiles Cours / Labs), cours.qmd (vidéos), labs.qmd (tuiles des labs)
assets/                  styles et images du site
tools/                   build_marimo.py (notebooks à compléter -> site WASM) et sa documentation
labs/
  _modele/               squelette à copier pour créer un nouveau lab
  lab01_tracking/        Lab 1 : pendule de Huygens par analyse d'images
    index.qmd            page du lab
    *.ipynb, *.py        PoC initiale
    Resources/           vidéo du pendule, bibliographie
    marimo/              notebooks marimo à compléter (maîtres, versions étudiant, corrigés, site WASM)
```

Voir `tools/README_marimo.md` et `labs/_modele/README.md`.

## Fonctionnement du repo

**Principe : on n'édite qu'un fichier par notebook, le fichier maître** (`labs/<lab>/marimo/maitres/*.py`).
C'est un notebook marimo complet qui tourne avec la solution. Aux endroits à compléter, il contient deux blocs :

```python
# >>> ETUDIANT
# x = None  # TODO          <- en commentaire : ce que voit l'étudiant
# <<< ETUDIANT
# >>> SOLUTION
x = calcul_correct()        # <- la solution, retirée de la version étudiant
# <<< SOLUTION
```

`python tools/build_marimo.py --site` en déduit tout le reste :

| Dossier (dans `labs/<lab>/marimo/`) | Contenu | Publié ? |
|---|---|---|
| `maitres/`, `lab.json`, `public/` | **à éditer** : notebooks maîtres, titres, données | non |
| `notebooks/` | version étudiant (TODO), générée | non |
| `solutions/` | corrigé, généré | non |
| `site/` | version étudiant compilée en WASM, générée | **oui** |
| `site_solutions/` | corrigés en WASM (avec `--site-solutions`) | non |

Ne jamais modifier les dossiers générés à la main : ils sont écrasés à chaque build.

**Au quotidien :**

* Modifier seulement des pages `.qmd` : `quarto publish gh-pages`, c'est tout.
* Modifier un notebook maître, `lab.json` ou `public/` :
  ```bash
  python tools/build_marimo.py --site   # une fois : pip install marimo
  quarto publish gh-pages
  ```

<!-- Pour ne plus avoir à lancer le build à la main, on peut ajouter `pre-render: python tools/build_marimo.py --site` -->
<!-- sous `project:` dans `_quarto.yml` (marimo doit alors être installé dans le `python` utilisé par Quarto, et chaque rendu prend 20 à 40 s de plus). -->

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