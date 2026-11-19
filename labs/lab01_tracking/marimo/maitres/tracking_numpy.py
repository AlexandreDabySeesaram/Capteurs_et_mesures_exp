# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
#     "pillow",
#     "plotly",
# ]
# ///
# FICHIER MAÎTRE : contient à la fois la solution et la version étudiant.
# Les blocs "# >>> SOLUTION ... # <<< SOLUTION" sont retirés de la version étudiant,
# les blocs "# >>> ETUDIANT ... # <<< ETUDIANT" (commentés) y sont décommentés.
# Ne pas distribuer ce fichier : lancer `python tools/build_marimo.py` (depuis la racine du dépôt).

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    import PIL.Image  # utilisé par mo.image pour afficher des tableaux NumPy

    return go, mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Suivi d'objet 1D avec NumPy

    Dans ce notebook, nous montrons comment réaliser un suivi d'objet simple avec des opérations **NumPy** uniquement.
    Nous allons :

    1. générer une « vidéo » synthétique d'un point noir se déplaçant sinusoïdalement selon l'axe X sur un fond blanc ;
    2. suivre le point image par image en calculant le barycentre (centre de masse) des pixels noirs ;
    3. tracer la trajectoire de l'objet suivi au cours du temps avec Plotly, puis l'analyser (FFT, ajustement).

    /// admonition | Comment travailler dans ce notebook
    * Ce notebook tourne **entièrement dans votre navigateur** : rien à installer.
    * Il est organisé en **trois colonnes** (faites défiler horizontalement) : simulation et suivi, post-traitement, étude de sensibilité.
    * Les cellules marquées **TODO** sont à compléter. Cliquez sur « 💡 Indice » pour obtenir de l'aide.
    * Le notebook est *réactif* : quand vous modifiez une cellule et l'exécutez (`Ctrl/Cmd + Entrée`),
      toutes les cellules qui en dépendent sont ré-exécutées automatiquement.
    * Votre code est conservé dans le navigateur, mais pensez à **télécharger votre notebook**
      (enregistrez avec `Ctrl/Cmd + S`, puis menu ☰ en haut à droite → *Export…* → *Python* → *Export notebook source*) pour le rendre.
    ///
    """)
    return


@app.cell
def _(mo):
    # Curseurs pour paramétrer la simulation
    num_frames = mo.ui.slider(10, 200, value=100, label="Nombre d'images", show_value=True)
    width = mo.ui.slider(200, 800, value=600, label="Largeur de la vidéo (pixels)", show_value=True)
    height = mo.ui.slider(100, 400, value=200, label="Hauteur de la vidéo (pixels)", show_value=True)
    radius = mo.ui.slider(2, 20, value=8, label="Rayon du point (pixels)", show_value=True)
    frequency = mo.ui.slider(0.01, 1.0, step=0.01, value=0.02, label="Fréquence (cycles/image)", show_value=True)

    controls = mo.vstack([num_frames, width, height, radius, frequency])
    return controls, frequency, height, num_frames, radius, width


@app.cell(hide_code=True)
def _(controls, mo):
    mo.md(f"""
    ### Paramètres de la simulation
    Modifiez les paramètres ci-dessous pour régénérer dynamiquement la vidéo synthétique :

    {controls}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Génération de la vidéo synthétique

    Une image en niveaux de gris est un tableau NumPy de forme `(hauteur, largeur)` : la valeur 255 correspond au blanc,
    0 au noir. La vidéo est un tableau de forme `(n_images, hauteur, largeur)`.

    ### TODO 1 : dessiner un disque

    Complétez la fonction `masque_disque(h, w, xc, yc, r)` qui renvoie un tableau **booléen** de forme `(h, w)`
    valant `True` pour les pixels situés à une distance inférieure ou égale à `r` du centre `(xc, yc)`.
    Attention : la première coordonnée d'un tableau est la **ligne** ($y$), la seconde la **colonne** ($x$).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("`Y, X = np.ogrid[:h, :w]` crée un vecteur colonne `Y` (indices de ligne) et un vecteur ligne `X` (indices de colonne)."),
            "💡 Indice 2": mo.md("Grâce au *broadcasting*, `(X - xc)**2 + (Y - yc)**2` est directement un tableau de forme `(h, w)`. Comparez-le à `r**2`."),
        }
    )
    return


@app.cell
def _(np):
    def masque_disque(h, w, xc, yc, r):
        """Tableau booléen (h, w) : True à l'intérieur du disque de centre (xc, yc) et de rayon r."""
        # >>> ETUDIANT
        # # TODO 1
        # masque = None
        # <<< ETUDIANT
        # >>> SOLUTION
        Y, X = np.ogrid[:h, :w]
        masque = (X - xc) ** 2 + (Y - yc) ** 2 <= r**2
        # <<< SOLUTION
        return masque

    return (masque_disque,)


@app.cell(hide_code=True)
def _(masque_disque, mo, np):
    # Vérification automatique du TODO 1
    def _verifier():
        try:
            _m = masque_disque(7, 9, 4, 3, 2)
        except Exception as _e:
            return mo.callout(mo.md(f"❌ `masque_disque` a levé une erreur : `{_e!r}`"), kind="danger")
        if _m is None:
            return mo.callout(mo.md("**TODO 1** pas encore complété."), kind="warn")
        _m = np.asarray(_m, dtype=bool)
        # Disque de rayon 2 centré en (x=4, y=3) : 13 pixels, quelques pixels témoins
        _ok = (
            _m.shape == (7, 9)
            and _m.sum() == 13
            and _m[3, 6] and _m[5, 4] and not _m[3, 7] and not _m[1, 2]
        )
        if _ok:
            return mo.callout(mo.md("✅ `masque_disque` est correct."), kind="success")
        return mo.callout(mo.md(f"❌ Résultat incorrect (forme obtenue : `{np.shape(_m)}`, attendue : `(7, 9)`). Vérifiez l'ordre des axes."), kind="danger")

    _verifier()
    return


@app.cell
def _(frequency, height, masque_disque, mo, np, num_frames, radius, width):
    n_frames = num_frames.value
    _w = width.value
    _h = height.value
    _r = radius.value

    mo.stop(
        masque_disque(_h, _w, 0, 0, _r) is None,
        mo.callout(mo.md("Complétez le **TODO 1** pour générer la vidéo."), kind="warn"),
    )

    # Images blanches (valeur 255)
    frames = np.ones((n_frames, _h, _w), dtype=np.uint8) * 255
    true_x_positions = []

    for _t in range(n_frames):
        # Mouvement sinusoïdal selon X
        x_center = int(_w / 2 + (_w / 2 - _r - 20) * np.sin(2 * np.pi * frequency.value * _t))
        y_center = int(_h / 2)
        true_x_positions.append(x_center)
        frames[_t][masque_disque(_h, _w, x_center, y_center, _r)] = 0  # point noir (valeur 0)
    return (frames,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Boucle de suivi avec NumPy

    Pour chaque image, on repère les pixels qui appartiennent au point noir (valeur `< 128`), puis on calcule la
    moyenne de leurs coordonnées (le **barycentre**) pour obtenir les positions X et Y.

    ### TODO 2 : barycentre des pixels noirs

    Complétez la fonction `barycentre(frame)` qui renvoie le couple `(cx, cy)` (en **flottants**) des coordonnées moyennes
    des pixels de valeur strictement inférieure à 128, ou `(None, None)` s'il n'y en a aucun.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("`y_coords, x_coords = np.where(frame < 128)` renvoie les indices de ligne et de colonne des pixels qui vérifient la condition."),
            "💡 Indice 2": mo.md("`np.mean(x_coords)` donne la coordonnée moyenne. Pensez au cas où `x_coords` est vide (`len(x_coords) == 0`)."),
        }
    )
    return


@app.cell
def _(np):
    def barycentre(frame):
        """Renvoie (cx, cy), barycentre des pixels sombres (< 128), ou (None, None) s'il n'y en a pas."""
        # >>> ETUDIANT
        # # TODO 2
        # cx, cy = None, None
        # <<< ETUDIANT
        # >>> SOLUTION
        y_coords, x_coords = np.where(frame < 128)
        if len(x_coords) == 0:
            return None, None
        cx = float(np.mean(x_coords))
        cy = float(np.mean(y_coords))
        # <<< SOLUTION
        return cx, cy

    return (barycentre,)


@app.cell(hide_code=True)
def _(barycentre, mo, np):
    # Vérification automatique du TODO 2
    def _verifier():
        _img = np.full((5, 6), 255, dtype=np.uint8)
        _img[1, 2] = _img[3, 4] = 0
        try:
            _c = barycentre(_img)
        except Exception as _e:
            return mo.callout(mo.md(f"❌ `barycentre` a levé une erreur : `{_e!r}`"), kind="danger")
        if _c == (None, None):
            return mo.callout(mo.md("**TODO 2** pas encore complété."), kind="warn")
        if np.allclose(_c, (3.0, 2.0)):
            return mo.callout(mo.md("✅ `barycentre` est correct."), kind="success")
        return mo.callout(mo.md(f"❌ Attendu `(3.0, 2.0)`, obtenu `{_c}`. Vérifiez l'ordre (x, y)."), kind="danger")

    _verifier()
    return


@app.cell
def _(barycentre, frames, mo, np):
    mo.stop(
        barycentre(frames[0]) == (None, None),
        mo.callout(mo.md("Complétez le **TODO 2** pour lancer le suivi."), kind="warn"),
    )
    tracked_positions = []
    _h, _w = frames.shape[1], frames.shape[2]

    for _t, _frame in enumerate(frames):
        # 1. Barycentre des pixels noirs
        _cx, _cy = barycentre(_frame)
        tracked_positions.append([_t + 1, _cx, _cy])
        _cx, _cy = (_w // 2, _h // 2) if _cx is None else (int(round(_cx)), int(round(_cy)))

        # 2. Réticule rouge sur une version RGB de l'image
        _rgb = np.stack([_frame, _frame, _frame], axis=-1)
        _rgb[max(0, _cy - 1) : min(_h, _cy + 2), max(0, _cx - 10) : min(_w, _cx + 11)] = [245, 70, 58]
        _rgb[max(0, _cy - 10) : min(_h, _cy + 11), max(0, _cx - 1) : min(_w, _cx + 2)] = [245, 70, 58]

        # 3. Affichage dans la sortie de la cellule
        mo.output.replace(
            mo.vstack(
                [
                    mo.md(f"### Suivi, image {_t + 1}/{len(frames)}\n* **Barycentre** : ({_cx}, {_cy})"),
                    mo.image(_rgb, width=450),
                ]
            )
        )
    return (tracked_positions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyse physique : mesure, résolution et incertitude

    En physique, mesurer consiste à associer une valeur numérique à une grandeur physique. Lorsqu'on mesure à partir
    d'images numériques, cette association introduit des limitations, des erreurs et des incertitudes spécifiques.

    ### Résolution spatiale et erreur de quantification
    Une image numérique est discrétisée en une grille de **pixels**.
    * Le plus petit déplacement mesurable en coordonnées brutes est $1$ pixel ($\Delta x = 1$).
    * Cette discrétisation spatiale introduit une **erreur de quantification**. Pour une valeur uniformément répartie
      à l'intérieur d'un pixel, l'incertitude-type vaut :
      $$\sigma_q = \frac{\Delta x}{\sqrt{12}} \approx 0{,}289 \text{ pixel}$$

    #### Résolution sub-pixel et estimation du barycentre
    Notre suivi NumPy calcule le barycentre avec `np.mean()`.
    * En moyennant les coordonnées de tous les pixels du point, on obtient le centre avec une **précision sub-pixel**
      (une erreur inférieure à $1$ pixel !).
    * **Exercice** : réduisez le **rayon du point** à $2$ ou $3$ pixels. Qu'arrive-t-il à la régularité de la trajectoire mesurée ?
      Pourquoi un point plus gros donne-t-il une trajectoire plus lisse ? (Indice : moyenner davantage de pixels réduit
      l'incertitude statistique sur le barycentre.)

    ### Résolution temporelle et théorème d'échantillonnage de Nyquist-Shannon
    Une vidéo est une suite d'images fixes acquises à une fréquence d'échantillonnage (fréquence d'images) $f_s$ :
    * Pour reconstruire un mouvement de fréquence $f_{\text{mouvement}}$ sans **repliement de spectre** (*aliasing*),
      il faut respecter le **critère de Nyquist** :
      $$f_s > 2 \cdot f_{\text{mouvement}}$$
    * Si $f_s \le 2 \cdot f_{\text{mouvement}}$ (c'est-à-dire une fréquence > 0,5 cycle/image), le mouvement paraît plus lent,
      immobile, voire inversé (repliement temporel).
    * **Exercice (pas temporel)** : réduisez le **nombre d'images** à une faible valeur (par exemple $15$ ou $20$).
      Observez la trajectoire tracée. Est-ce toujours une belle sinusoïde ? Comment le pas temporel affecte-t-il
      notre capacité à résoudre la forme de la trajectoire ?
    * **Exercice (repliement)** : augmentez progressivement la **fréquence** de $0{,}02$ à $0{,}45$, puis dépassez la limite
      de Nyquist en la réglant à $0{,}52$ ou $0{,}55$.
      * Observez l'animation du suivi. À quoi ressemble le mouvement du point lorsque la fréquence vaut $0{,}50$ (exactement Nyquist) ?
      * Regardez la cellule **Analyse spectrale (FFT)**. Que devient la fréquence du pic détecté lorsque la vraie fréquence vaut $0{,}55$ ?
        (Indice : un avertissement s'affiche lorsque la vraie fréquence dépasse le seuil de Nyquist de 0,5 !)
    """)
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md(r"""
    ## Post-traitement de la trajectoire

    On trace la coordonnée X suivie en fonction du numéro d'image pour visualiser le mouvement sinusoïdal.
    """)
    return


@app.cell
def _(go, np, tracked_positions):
    positions_arr = np.array(tracked_positions, dtype=float)
    frames_vec = positions_arr[:, 0]
    x_vec = positions_arr[:, 1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frames_vec,
            y=x_vec,
            mode="lines+markers",
            name="Position X suivie",
            line=dict(color="rgb(58,70,245)", width=2),
            marker=dict(size=4),
        )
    )
    fig.update_layout(
        title="Position du point selon X au cours du temps",
        xaxis_title="Numéro d'image",
        yaxis_title="Coordonnée X (pixels)",
        plot_bgcolor="rgba(0,0,0,0)",
        width=850,
        height=400,
        legend=dict(x=0, y=1),
    )
    fig
    return frames_vec, x_vec


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 3 : fréquence dominante (FFT)

    1. retirez la moyenne de `x_vec` (`x_detrended`) ;
    2. calculez l'amplitude de sa transformée de Fourier discrète pour les fréquences positives (`fft_vals`) ;
    3. calculez les fréquences associées en **cycles par image** (`freqs`) ;
    4. trouvez la fréquence `peak_freq` du maximum de `fft_vals`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("`np.abs(np.fft.rfft(signal))` : amplitude de la TFD d'un signal réel (fréquences positives)."),
            "💡 Indice 2": mo.md("`np.fft.rfftfreq(n, d=1.0)` : fréquences associées pour `n` points espacés de `d` (ici une image)."),
            "💡 Indice 3": mo.md("`np.argmax(tableau)` renvoie l'indice du maximum."),
        }
    )
    return


@app.cell
def _(frequency, np, x_vec):
    # >>> ETUDIANT
    # # TODO 3
    # x_detrended = None
    # fft_vals = None
    # freqs = None
    # peak_freq = None
    # <<< ETUDIANT
    # >>> SOLUTION
    # Transformée de Fourier rapide (FFT) de la coordonnée X centrée
    x_detrended = x_vec - np.mean(x_vec)
    fft_vals = np.abs(np.fft.rfft(x_detrended))
    freqs = np.fft.rfftfreq(len(x_vec), d=1.0)  # fréquence en cycles/image
    peak_freq = freqs[np.argmax(fft_vals)]
    # <<< SOLUTION

    # Détection du repliement de spectre (fourni)
    true_f = frequency.value
    nyquist_f = 0.5
    aliasing_alert = ""
    if true_f > nyquist_f and peak_freq is not None:
        _epsilon = true_f - 0.5
        _beat_freq = 2 * _epsilon
        aliasing_alert = f"""
    /// attention | Repliement de spectre détecté !
    La vraie fréquence d'entrée (`{true_f:.2f}`) dépasse la **limite de Nyquist** de `{nyquist_f:.2f}` cycle/image.
    Le signal est sous-échantillonné (moins de 2 images par période), si bien qu'on observe une fausse fréquence plus basse,
    de `{peak_freq:.2f}` cycle/image.
    ///

    #### 🔍 Pourquoi voit-on une « enveloppe » lente (battement) ?
    Lorsqu'on échantillonne une sinusoïde de fréquence $f = 0{{,}}5 + \\epsilon$ (ici $\\epsilon = {_epsilon:.2f}$), le signal discret s'écrit :
    $$x[n] = A \\sin(2\\pi (0{{,}}5 + \\epsilon) n) = A (-1)^n \\sin(2\\pi \\epsilon n)$$
    C'est une **modulation d'amplitude à porteuse supprimée** :
    * la **porteuse** a une fréquence d'exactement $0{{,}}5$ cycle/image (le terme alterné $(-1)^n$) ;
    * l'**enveloppe lente** module l'amplitude à la fréquence $\\epsilon = {_epsilon:.2f}$ cycle/image (période de `{1 / _epsilon:.1f}` images).

    #### 📊 Pourquoi la FFT ne montre-t-elle qu'un seul pic, à `{peak_freq:.2f}` ?
    En modulation d'amplitude, l'énergie spectrale se trouve dans les bandes latérales autour de la porteuse :
    $$f_c \\pm f_m = 0{{,}}5 \\pm {_epsilon:.2f}$$
    soit `{0.5 - _epsilon:.2f}` et `{0.5 + _epsilon:.2f}` cycle/image.
    Le spectre discret étant périodique et symétrique, ces deux fréquences se replient sur **la même fréquence** de `{peak_freq:.2f}` cycle/image.

    Il n'y a **aucune** énergie à la fréquence de l'enveloppe `{_epsilon:.2f}` dans le signal brut, car la porteuse alternée $(-1)^n$
    annule toute composante lente (la moyenne est nulle). En revanche, si l'on prend la **valeur absolue** des coordonnées
    (redressement, $|x[n]|$), on supprime la porteuse $(-1)^n$, et la FFT de $|x[n]|$ présente un pic net à la fréquence de battement
    $2\\epsilon = {_beat_freq:.2f}$ cycle/image !
    """
    return aliasing_alert, fft_vals, freqs, peak_freq, true_f


@app.cell(hide_code=True)
def _(aliasing_alert, fft_vals, freqs, go, mo, peak_freq, true_f):
    mo.stop(
        peak_freq is None or fft_vals is None or freqs is None,
        mo.callout(mo.md("Complétez le **TODO 3** pour afficher le spectre."), kind="warn"),
    )
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Bar(x=freqs, y=fft_vals, name="Amplitude spectrale", marker=dict(color="rgb(23,15,48)")))
    fig_fft.update_layout(
        title="Spectre en fréquence (FFT)",
        xaxis_title="Fréquence (cycles/image)",
        yaxis_title="Amplitude spectrale",
        plot_bgcolor="rgba(0,0,0,0)",
        width=850,
        height=350,
    )
    mo.md(f"""
    ## Analyse spectrale (transformée de Fourier)
    Pour identifier la fréquence d'oscillation dominante, on calcule la transformée de Fourier discrète de la coordonnée X :

    * **Vraie fréquence d'entrée** : `{true_f:.4f}` cycle/image
    * **Fréquence du pic détecté** : `{peak_freq:.4f}` cycle/image
    * **Période d'oscillation mesurée** : `{1 / peak_freq:.2f}` images

    {aliasing_alert}

    {mo.as_html(fig_fft)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 4 : ajustement d'une sinusoïde par moindres carrés

    On modélise la trajectoire par $x(t) = A \sin(\omega t) + B \cos(\omega t) + C$. Ce modèle est **linéaire** en $(A, B, C)$ :
    $\mathbf{x} \approx M \mathbf{p}$ où les colonnes de $M$ sont $\sin(\omega t)$, $\cos(\omega t)$ et $1$.

    Complétez la fonction `ajuster_sinus(t, x, omega)` qui renvoie `(params, fit_x, rmse)` :
    les paramètres $(A, B, C)$, la courbe ajustée et l'écart quadratique moyen des résidus.
    Cette fonction est réutilisée dans l'étude de sensibilité (troisième colonne).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("`np.column_stack([np.sin(omega * t), np.cos(omega * t), np.ones_like(t)])` construit la matrice `M`."),
            "💡 Indice 2": mo.md("`params, _, _, _ = np.linalg.lstsq(M, x, rcond=None)` puis `fit_x = M @ params`."),
            "💡 Indice 3": mo.md("RMSE : `np.sqrt(np.mean((x - fit_x)**2))`."),
        }
    )
    return


@app.cell
def _(np):
    def ajuster_sinus(t, x, omega):
        """Ajuste x(t) = A sin(wt) + B cos(wt) + C. Renvoie (params, fit_x, rmse)."""
        t = np.asarray(t, dtype=float)
        x = np.asarray(x, dtype=float)
        # >>> ETUDIANT
        # # TODO 4
        # params, fit_x, rmse = None, None, None
        # <<< ETUDIANT
        # >>> SOLUTION
        M = np.column_stack([np.sin(omega * t), np.cos(omega * t), np.ones_like(t)])
        params, _, _, _ = np.linalg.lstsq(M, x, rcond=None)
        fit_x = M @ params
        rmse = np.sqrt(np.mean((x - fit_x) ** 2))
        # <<< SOLUTION
        return params, fit_x, rmse

    return (ajuster_sinus,)


@app.cell
def _(ajuster_sinus, frames_vec, go, mo, np, peak_freq, x_vec):
    mo.stop(peak_freq is None)
    params, fit_x, rmse = ajuster_sinus(frames_vec - 1, x_vec, 2 * np.pi * peak_freq)
    mo.stop(
        fit_x is None,
        mo.callout(mo.md("Complétez le **TODO 4** pour afficher l'ajustement."), kind="warn"),
    )
    amplitude_fit = np.sqrt(params[0] ** 2 + params[1] ** 2)
    offset_fit = params[2]

    fig_fit = go.Figure()
    fig_fit.add_trace(go.Scatter(x=frames_vec, y=x_vec, mode="markers", name="Positions mesurées", marker=dict(color="rgb(58,70,245)", size=6)))
    fig_fit.add_trace(go.Scatter(x=frames_vec, y=fit_x, mode="lines", name="Sinusoïde ajustée", line=dict(color="rgb(245,70,58)", width=2)))
    fig_fit.update_layout(
        title="Trajectoire et ajustement",
        xaxis_title="Numéro d'image",
        yaxis_title="Coordonnée X (pixels)",
        plot_bgcolor="rgba(0,0,0,0)",
        width=850,
        height=380,
        legend=dict(x=0, y=1),
    )
    return amplitude_fit, fig_fit, offset_fit, rmse


@app.cell(hide_code=True)
def _(amplitude_fit, fig_fit, mo, offset_fit, rmse):
    mo.md(f"""
    ## Ajustement par moindres carrés et incertitude expérimentale
    On ajuste la trajectoire par un modèle sinusoïdal $x(t) = A \\cos(\\omega t + \\phi) + C$ par moindres carrés linéaires :

    * **Amplitude ajustée** : `{amplitude_fit:.2f}` pixels
    * **Décalage ajusté (centre du mouvement)** : `{offset_fit:.2f}` pixels
    * **Écart-type des résidus (RMSE)** : `{rmse:.4f}` pixels

    Le **RMSE** représente l'incertitude de mesure expérimentale. Pour une erreur de quantification pure (résolution de 1 pixel),
    l'incertitude minimale théorique vaut $\\sigma_q \\approx 0{{,}}289$ pixel. Si votre RMSE est inférieur à cette valeur,
    vous avez atteint une **résolution sub-pixel** !

    {mo.as_html(fig_fit)}
    """)
    return


@app.cell(column=2, hide_code=True)
def _(mo):
    mo.md(r"""
    ## Étude de sensibilité : incertitude physique et résolution

    On suppose que la largeur de l'image correspond à une longueur physique de $1$ m. Pour différentes largeurs d'image
    (donc différentes résolutions spatiales), on génère la vidéo, on suit le point avec `barycentre`, on ajuste une
    sinusoïde avec `ajuster_sinus` et on convertit le RMSE en mètres.

    *(Cette cellule utilise vos fonctions des TODO 1, 2 et 4.)*

    **Question :** comment l'incertitude physique évolue-t-elle avec la résolution ? Proposez une loi d'échelle.
    """)
    return


@app.cell
def _(ajuster_sinus, barycentre, go, height, masque_disque, mo, np, num_frames, radius):
    _n_frames = num_frames.value
    _h = height.value
    _r = radius.value
    _L_physical = 1.0  # largeur physique de 1 m

    _widths = np.arange(100, 1001, 100)
    _omega = 2 * np.pi * (2 / _n_frames)
    _t_vals = np.arange(_n_frames)
    _physical_rmse_vals = []

    mo.stop(
        masque_disque(_h, 100, 0, 0, _r) is None
        or barycentre(np.zeros((2, 2), dtype=np.uint8)) == (None, None)
        or ajuster_sinus(_t_vals, _t_vals, _omega)[2] is None,
        mo.callout(mo.md("Complétez les **TODO 1, 2 et 4** pour lancer l'étude de sensibilité."), kind="warn"),
    )

    for _w in _widths:
        # Génération (centre non arrondi : position sub-pixel)
        _tracked_x = []
        for _t in range(_n_frames):
            _xc = _w / 2 + (_w / 2 - _r - 20) * np.sin(_omega * _t)
            _frame = np.full((_h, _w), 255, dtype=np.uint8)
            _frame[masque_disque(_h, _w, _xc, _h / 2, _r)] = 0
            # Suivi
            _cx, _ = barycentre(_frame)
            _tracked_x.append(_w / 2 if _cx is None else _cx)

        # Ajustement puis conversion pixels -> mètres
        _, _, _rmse = ajuster_sinus(_t_vals, _tracked_x, _omega)
        _physical_rmse_vals.append(_rmse * (_L_physical / _w))

    fig_res = go.Figure()
    fig_res.add_trace(
        go.Scatter(
            x=_widths,
            y=_physical_rmse_vals,
            mode="lines+markers",
            name="RMSE physique",
            line=dict(color="rgb(58,70,245)", width=2),
        )
    )
    fig_res.update_layout(
        title="Incertitude physique en fonction de la résolution",
        xaxis_title="Largeur de l'image (pixels)",
        yaxis_title="Incertitude (m)",
        plot_bgcolor="rgba(0,0,0,0)",
        width=500,
        height=350,
    )
    fig_res
    return


if __name__ == "__main__":
    app.run()
