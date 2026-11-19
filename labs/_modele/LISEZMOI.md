# Créer un nouveau lab

1. Copier ce dossier : `cp -R labs/_modele labs/lab02_nom` (le nom ne doit pas commencer par `_`).
2. Éditer `index.qmd` (page du lab sur le site), `marimo/lab.json` (titre, liste des notebooks)
   et écrire les notebooks dans `marimo/maitres/` (un fichier par entrée de `lab.json`).
   Les données des notebooks vont dans `marimo/public/`, les autres ressources (vidéos, .bib...) dans `Resources/`.
3. Ajouter une section pour le lab dans la barre latérale de `_quarto.yml` (sous « Labs », sur le modèle du lab 1)
   et remplacer la tuile « À venir » correspondante dans `labs.qmd` par une tuile sur le modèle du Lab 1.
4. `python tools/build_marimo.py --site`, puis `quarto preview` pour vérifier et `quarto publish gh-pages`.

Voir `tools/LISEZMOI_marimo.md` pour le fonctionnement des notebooks marimo.
