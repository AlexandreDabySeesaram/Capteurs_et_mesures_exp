# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
# ]
# ///
# FICHIER MAÎTRE : contient à la fois la solution et la version étudiant.
# Les blocs "# >>> SOLUTION ... # <<< SOLUTION" sont retirés de la version étudiant,
# les blocs "# >>> ETUDIANT ... # <<< ETUDIANT" (commentés) y sont décommentés.
# Ne pas distribuer ce fichier : lancer `python tools/build_marimo.py` (depuis la racine du dépôt).

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    return mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Titre du notebook

    La première ligne `# ...` de ce notebook sert d'identifiant pour la sauvegarde dans le navigateur :
    donnez à chaque notebook un titre différent.

    ### TODO 1 : moyenne
    Calculez la moyenne `m` du tableau `x`.
    """)
    return


@app.cell
def _(np):
    x = np.arange(10)
    # >>> ETUDIANT
    # # TODO 1
    # m = None
    # <<< ETUDIANT
    # >>> SOLUTION
    m = np.mean(x)
    # <<< SOLUTION
    m
    return


if __name__ == "__main__":
    app.run()
