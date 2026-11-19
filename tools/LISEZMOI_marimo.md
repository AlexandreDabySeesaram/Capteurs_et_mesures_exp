# Notebooks marimo à compléter (navigateur, sans installation)

## Organisation (exemple du lab 1)

| Chemin | Rôle |
|---|---|
| `labs/lab01_tracking/marimo/lab.json` | Titre du lab et liste des notebooks (ordre, titres, descriptions de la page d'accueil). |
| `labs/lab01_tracking/marimo/maitres/` | **Les seuls notebooks à éditer** : solution + consignes étudiant entre marqueurs `# >>> ETUDIANT` / `# >>> SOLUTION`. |
| `labs/lab01_tracking/marimo/public/` | Données lues par les notebooks (ici `pendule_frames.zip`, les 131 images de `pend.mp4`). |
| `labs/lab01_tracking/marimo/notebooks/`, `solutions/` | Versions étudiant et corrigés, générées. |
| `labs/lab01_tracking/marimo/site/` | Site étudiant généré, publié par Quarto. |
| `labs/lab01_tracking/marimo/site_solutions/` | Site des corrigés, généré, **jamais publié** par Quarto. |
| `tools/build_marimo.py` | Génère tout ce qui précède, pour un lab ou pour tous. |
| `tools/accueil_modele.html` | Modèle de la page d'accueil d'un lab (consignes de travail et de rendu pour les étudiants). |

Les originaux du lab 1 (`marimo_tracking.py`, `numpy_tracking.py`, `jup_tracking.ipynb`) sont dans `labs/lab01_tracking/` et ne sont pas modifiés
(lancez-les depuis ce dossier pour que les chemins `Resources/...` fonctionnent).

## Regénérer et publier

```bash
pip install marimo   # une fois
python tools/build_marimo.py --site --site-solutions     # tous les labs
python tools/build_marimo.py labs/lab01_tracking --site  # un seul lab
quarto preview                                           # vérification locale
quarto publish gh-pages
```

Pour tester un site seul : `python -m http.server --directory labs/lab01_tracking/marimo/site 8000`.
Le site doit être servi en HTTP (pas ouvert en `file://`). Seuls `labs/*/marimo/site/` sont copiés dans le site Quarto :
maîtres, solutions et `site_solutions/` ne sont ni rendus ni publiés.

Nouveau lab : voir `labs/_modele/LISEZMOI.md`.

## Adaptations par rapport aux notebooks d'origine

- Traduction en français.
- **TP 2 (OpenCV)** : le tracker CSRT n'existe pas dans OpenCV pour Pyodide (4.11, sans modules contrib ; KCF non plus, MIL perd le pendule).
  Le suivi utilise donc la corrélation de motif (`cv2.matchTemplate`, `TM_CCOEFF_NORMED`), qui donne les mêmes positions que CSRT à 4 px près sur cette vidéo.
  La vidéo est lue depuis `public/pendule_frames.zip`.
- **TP 1 (NumPy)** : le disque, le barycentre et l'ajustement sont devenus des fonctions (`masque_disque`, `barycentre`, `ajuster_sinus`) que l'étude de sensibilité (3e colonne) réutilise, pour ne pas donner la solution dans cette cellule. Le graphique de sensibilité, qui n'était pas affiché, l'est maintenant.
- TODO avec indices dépliables, et cellules de vérification automatique (✅ / ❌) quand c'est possible.

## Ce que build.py corrige dans l'export marimo (version 0.25.2)

- `auto_instantiate` forcé à `true` : sinon les cellules ne s'exécutent pas à l'ouverture.
- Export avec une configuration marimo vierge : votre `~/.config/marimo/marimo.toml` n'est pas embarqué dans le site.
- **Sauvegarde** : par défaut, un notebook html-wasm recharge toujours l'énoncé d'origine (les modifications sont perdues au rechargement).
  Un petit script ajouté à chaque page recopie le code enregistré par l'étudiant (`Ctrl/Cmd + S`) dans le `localStorage` du navigateur, propre à chaque TP,
  et le recharge à l'ouverture suivante. `?reinitialiser` à la fin de l'adresse efface cette sauvegarde.
  Elle reste locale au navigateur : les étudiants doivent télécharger leur `.py` (menu ☰ → Export… → Python) pour le rendre.

À revérifier si vous changez de version de marimo (le script de sauvegarde dépend de son comportement interne).

## Couleurs ENSTA

Palette commune : marine `#170F39`, bleu `#3A46F5` (bleu éclairci `#8C94FF` en mode sombre).
Elle est définie dans `assets/style_site.scss` / `style_site_dark.scss` (site Quarto), `tools/accueil_modele.html`
(page d'accueil de chaque lab) et `tools/marimo_ensta.css` (injecté dans chaque notebook par `build_marimo.py`).
