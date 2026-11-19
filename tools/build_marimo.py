"""Génère, pour chaque lab, les notebooks étudiant / solution et le site statique marimo (WASM).

Usage (depuis la racine du dépôt) :
    python tools/build_marimo.py                     # tous les labs : notebooks/ et solutions/
    python tools/build_marimo.py --site              # idem + site étudiant (marimo/site/)
    python tools/build_marimo.py --site --site-solutions   # + site des corrigés (marimo/site_solutions/)
    python tools/build_marimo.py labs/lab01_tracking --site # un seul lab
    python tools/build_marimo.py --site --force      # recompiler même si rien n'a changé

Un lab n'est recompilé que si ses maîtres, lab.json, public/ ou les fichiers de tools/ ont changé
(empreinte enregistrée dans site/.empreinte) : on peut donc lancer ce script avant chaque rendu Quarto.

Organisation d'un lab (voir labs/_modele/) :
    labs/labXX_nom/marimo/
        lab.json         titre du lab et liste des notebooks (ordre, titres, descriptions)
        maitres/*.py     notebooks maîtres (solution + consignes étudiant) : les seuls à éditer
        public/          données nécessaires aux notebooks
        notebooks/*.py   versions étudiant (TODO), générées
        solutions/*.py   versions corrigées, générées
        site/            site statique étudiant, généré (publié par Quarto)
        site_solutions/  site des corrigés, généré (non publié)

Dans un notebook maître :
    # >>> ETUDIANT
    # code commenté, décommenté (un niveau de "# ") dans la version étudiant
    # <<< ETUDIANT
    # >>> SOLUTION
    code gardé dans la solution, supprimé de la version étudiant
    # <<< SOLUTION
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MODELE_ACCUEIL = Path(__file__).resolve().parent / "accueil_modele.html"
NOINDEX = '<meta name="robots" content="noindex, nofollow">\n'  # corrigés : non référencés par les moteurs de recherche
STYLE_ENSTA = (Path(__file__).resolve().parent / "marimo_ensta.css").read_text(encoding="utf-8")

EN_TETE_MAITRE = re.compile(r"^# FICHIER MAÎTRE.*?\n(?:#.*\n)*?(?=\n|import)", re.M)
BLOC = re.compile(r"^([ \t]*)# >>> (ETUDIANT|SOLUTION)\n(.*?)^[ \t]*# <<< \2\n", re.M | re.S)

# Script injecté dans chaque page exportée : sauvegarde du travail dans le navigateur.
# Dans un export html-wasm, marimo recharge toujours le code d'origine à l'ouverture de la page.
# Quand l'étudiant enregistre (Ctrl/Cmd + S), marimo écrit le code dans localStorage["marimo:file"]
# (clé commune à tout le site). Ce script recopie ce code dans une clé propre au notebook
# et le réinjecte à la place du code d'origine au chargement suivant.
# L'adresse ?reinitialiser efface la sauvegarde et repart de l'énoncé.
SCRIPT_SAUVEGARDE = """
<script>
(function () {
  var CLE = "tp-sauvegarde:" + location.pathname;
  var SIGNATURE = __SIGNATURE__;
  try {
    if (new URLSearchParams(location.search).has("reinitialiser")) localStorage.removeItem(CLE);
    var el = document.querySelector("marimo-code");
    var sauve = localStorage.getItem(CLE);
    if (el && sauve) {
      var original = decodeURIComponent(el.textContent || "");
      var app = original.match(/app = marimo\\.App\\([^)]*\\)/);
      if (app) sauve = sauve.replace(/app = marimo\\.App\\([^)]*\\)/, app[0]);
      el.textContent = encodeURIComponent(sauve);
    }
    var dernier = localStorage.getItem("marimo:file");
    setInterval(function () {
      var v = localStorage.getItem("marimo:file");
      if (v === dernier) return;
      dernier = v;
      if (!document.hasFocus()) return;
      var code;
      try { code = JSON.parse(v); } catch (e) { return; }
      if (typeof code === "string" && code.indexOf(SIGNATURE) !== -1) localStorage.setItem(CLE, code);
    }, 1000);
  } catch (e) { console.warn("sauvegarde locale indisponible", e); }
})();
</script>
"""


def version(source: str, cible: str) -> str:
    """Produit la version 'etudiant' ou 'solution' d'un notebook maître."""

    def remplacer(m):
        _, genre, corps = m.groups()
        if genre == "SOLUTION":
            return corps if cible == "solution" else ""
        if cible == "solution":
            return ""
        return "".join(re.sub(r"^([ \t]*)# ?", r"\1", ligne, count=1) for ligne in corps.splitlines(keepends=True))

    texte = EN_TETE_MAITRE.sub("", BLOC.sub(remplacer, source))
    if "# >>>" in texte or "# <<<" in texte:
        raise ValueError("marqueur non apparié")
    return texte


class Lab:
    def __init__(self, dossier_lab: Path):
        self.marimo = dossier_lab / "marimo"
        self.config = json.loads((self.marimo / "lab.json").read_text(encoding="utf-8"))
        self.notebooks = self.config["notebooks"]

    def generer(self):
        public = self.marimo / "public"
        for cible, dossier in (("etudiant", "notebooks"), ("solution", "solutions")):
            sortie = self.marimo / dossier
            sortie.mkdir(exist_ok=True)
            if (sortie / "public").exists():
                shutil.rmtree(sortie / "public")
            if public.exists():
                shutil.copytree(public, sortie / "public")
            for nb in self.notebooks:
                source = (self.marimo / "maitres" / f"{nb['nom']}.py").read_text(encoding="utf-8")
                (sortie / f"{nb['nom']}.py").write_text(version(source, cible), encoding="utf-8")
        print(f"[{self.config['titre']}] notebooks/ et solutions/ générés")

    def exporter_site(self, source_dir: str, site_dir: str):
        source, final = self.marimo / source_dir, self.marimo / site_dir
        # On construit dans un dossier temporaire : si l'export échoue, l'ancien site reste intact.
        site = self.marimo / f".{site_dir}_en_cours"
        if site.exists():
            shutil.rmtree(site)
        site.mkdir()
        # Configuration marimo vierge : on n'embarque pas la configuration personnelle
        # de l'enseignant (~/.config/marimo/marimo.toml) dans le site.
        env = {**os.environ, "XDG_CONFIG_HOME": tempfile.mkdtemp()}
        cartes = []
        for nb in self.notebooks:
            nom = nb["nom"]
            subprocess.run(
                [*commande_marimo(), "export", "html-wasm", str(source / f"{nom}.py"),
                 "-o", str(site / nom), "--mode", "edit", "-f"],
                check=True, env=env,
            )
            page = site / nom / "index.html"
            texte = page.read_text(encoding="utf-8")
            # Exécuter toutes les cellules à l'ouverture (sinon il faut cliquer sur « Run all »)
            if '"auto_instantiate": false' not in texte:
                print(f"attention : réglage auto_instantiate introuvable dans {page}")
            texte = texte.replace('"auto_instantiate": false', '"auto_instantiate": true')
            # Sauvegarde locale propre à chaque notebook ; la signature est le titre (1re ligne "    # ...")
            signature = re.search(r"^    # (.+)$", (source / f"{nom}.py").read_text(encoding="utf-8"), re.M).group(1)
            assert texte.count("</marimo-code>") == 1
            texte = texte.replace(
                "</marimo-code>",
                "</marimo-code>" + SCRIPT_SAUVEGARDE.replace("__SIGNATURE__", json.dumps("# " + signature)),
            )
            # Couleurs ENSTA (titres, liens, encadrés)
            assert texte.count("</head>") == 1
            texte = texte.replace("</head>", f"<style>\n{STYLE_ENSTA}</style>\n</head>")
            if site_dir == "site_solutions":
                texte = texte.replace("</head>", NOINDEX + "</head>", 1)
            page.write_text(texte, encoding="utf-8")
            (site / nom / "CLAUDE.md").unlink(missing_ok=True)  # fichier d'aide IA ajouté par marimo, inutile ici
            cartes.append(
                f'<a class="carte" href="{nom}/"><h2>{html.escape(nb["titre"])}</h2>'
                f"<p>{html.escape(nb.get('description', ''))}</p></a>"
            )
        accueil = MODELE_ACCUEIL.read_text(encoding="utf-8")
        accueil = accueil.replace("<!--TITRE-->", html.escape(self.config["titre"]))
        accueil = accueil.replace("<!--SOUS_TITRE-->", html.escape(self.config.get("sous_titre", "")))
        accueil = accueil.replace("<!--CARTES-->", "\n".join(cartes))
        # Lien de retour vers l'accueil du site Quarto (chemin relatif depuis ce site)
        accueil = accueil.replace("<!--RACINE-->", os.path.relpath(RACINE, site).replace(os.sep, "/"))
        if site_dir == "site_solutions":
            accueil = accueil.replace("</head>", NOINDEX + "</head>", 1)
            accueil = accueil.replace("<h1>", "<h1>Corrigés · ", 1)
        (site / "index.html").write_text(accueil, encoding="utf-8")
        (site / ".nojekyll").touch()
        if final.exists():
            shutil.rmtree(final)
        site.rename(final)
        site = final
        print(f"[{self.config['titre']}] site exporté dans {os.path.relpath(site, RACINE)}")


def commande_marimo():
    """marimo du Python courant si possible, sinon la commande `marimo` du PATH
    (Quarto peut lancer le pre-render avec un autre Python que celui de votre environnement)."""
    import importlib.util
    if importlib.util.find_spec("marimo"):
        return [sys.executable, "-m", "marimo"]
    if shutil.which("marimo"):
        return [shutil.which("marimo")]
    sys.exit("marimo introuvable : installez-le (pip install marimo==0.25.2) dans l'environnement actif.")


def labs_demandes(args):
    chemins = [Path(a).resolve() for a in args if not a.startswith("--")]
    if not chemins:
        chemins = sorted(p.parent.parent for p in (RACINE / "labs").glob("*/marimo/lab.json"))
    return [Lab(p) for p in chemins if not p.name.startswith("_")]


def empreinte(lab: "Lab") -> str:
    """Empreinte de tout ce dont dépend le site d'un lab : si elle ne change pas, inutile de recompiler."""
    import hashlib

    h = hashlib.sha256()
    outils = Path(__file__).resolve().parent
    fichiers = [lab.marimo / "lab.json", Path(__file__).resolve(),
                outils / "accueil_modele.html", outils / "marimo_ensta.css"]
    fichiers += sorted((lab.marimo / "maitres").glob("*.py"))
    fichiers += sorted(f for f in (lab.marimo / "public").rglob("*") if f.is_file())
    for f in fichiers:
        h.update(str(f.relative_to(RACINE)).encode())
        h.update(f.read_bytes())
    # Version de marimo réellement utilisée pour l'export
    h.update(subprocess.run([*commande_marimo(), "--version"], capture_output=True, text=True).stdout.strip().encode())
    return h.hexdigest()


if __name__ == "__main__":
    # --force : tout recompiler même si rien n'a changé
    force = "--force" in sys.argv
    for lab in labs_demandes(sys.argv[1:]):
        cibles = [("--site", "notebooks", "site"), ("--site-solutions", "solutions", "site_solutions")]
        cibles = [(src, dst) for opt, src, dst in cibles if opt in sys.argv]
        signature = empreinte(lab)
        a_faire = [
            (src, dst) for src, dst in cibles
            if force or not (lab.marimo / dst / ".empreinte").exists()
            or (lab.marimo / dst / ".empreinte").read_text() != signature
        ]
        if cibles and not a_faire:
            print(f"[{lab.config['titre']}] inchangé, rien à recompiler")
            continue
        lab.generer()
        for src, dst in a_faire:
            lab.exporter_site(src, dst)
            (lab.marimo / dst / ".empreinte").write_text(signature)
