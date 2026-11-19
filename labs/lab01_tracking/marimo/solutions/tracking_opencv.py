# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
#     "opencv-python",
#     "pillow",
#     "plotly",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import io
    import zipfile
    import cv2
    import numpy as np
    import plotly.graph_objects as go
    import PIL.Image  # utilisé par mo.image pour afficher des tableaux NumPy

    return cv2, go, io, mo, np, zipfile


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Suivi d'objet dans une vidéo avec OpenCV

    Dans ce notebook, nous allons utiliser **OpenCV** pour suivre un objet (le disque d'un pendule) dans une vidéo.
    Nous allons d'abord sélectionner l'objet (la **région d'intérêt**, ou ROI), puis le suivre image par image,
    et enfin tracer l'évolution de la position de son barycentre en fonction du numéro d'image, avant d'en
    extraire la fréquence d'oscillation.

    /// admonition | Comment travailler dans ce notebook
    * Ce notebook tourne **entièrement dans votre navigateur** : rien à installer.
    * Les cellules marquées **TODO** sont à compléter. Cliquez sur « 💡 Indice » pour obtenir de l'aide.
    * Le notebook est *réactif* : quand vous modifiez une cellule et l'exécutez (`Ctrl/Cmd + Entrée`),
      toutes les cellules qui en dépendent sont ré-exécutées automatiquement.
    * Votre code est conservé dans le navigateur, mais pensez à **télécharger votre notebook**
      (enregistrez avec `Ctrl/Cmd + S`, puis menu ☰ en haut à droite → *Export…* → *Python* → *Export notebook source*) pour le rendre.
    ///

    ## Bibliothèques utilisées

    * OpenCV (`cv2`) pour le traitement d'images ;
    * NumPy pour le calcul numérique ;
    * Plotly pour les graphiques interactifs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Chargement de la vidéo

    La vidéo du pendule (`pend.mp4`, filmée à 60 images par seconde) a été découpée à l'avance en une suite
    d'images JPEG regroupées dans une archive `pendule_frames.zip`. En effet, la version d'OpenCV qui tourne
    dans le navigateur ne sait pas décoder les fichiers MP4. Chaque image est un tableau NumPy de forme
    `(hauteur, largeur, 3)` dont les canaux sont dans l'ordre **BGR** (bleu, vert, rouge), qui est la convention d'OpenCV.

    *(Cette cellule est fournie, il n'y a rien à modifier.)*
    """)
    return


@app.cell
async def _(cv2, io, mo, np, zipfile):
    async def lire_octets(chemin):
        """Lit un fichier, localement ou par le réseau (navigateur)."""
        try:
            from pyodide.http import pyfetch  # disponible uniquement dans le navigateur
        except ImportError:
            with open(chemin, "rb") as _f:
                return _f.read()
        _reponse = await pyfetch(str(chemin))
        return await _reponse.bytes()

    _archive = zipfile.ZipFile(
        io.BytesIO(await lire_octets(mo.notebook_location() / "public" / "pendule_frames.zip"))
    )
    frames = [
        cv2.imdecode(np.frombuffer(_archive.read(_nom), np.uint8), cv2.IMREAD_COLOR)
        for _nom in sorted(_archive.namelist())
    ]
    fps = 60.0  # fréquence d'acquisition de la caméra (images par seconde)
    first_frame = frames[0]
    frame_h, frame_w = first_frame.shape[:2]

    mo.md(
        f"**{len(frames)} images** chargées, de taille {frame_w} × {frame_h} pixels, "
        f"filmées à {fps:.0f} images/s (durée : {len(frames) / fps:.2f} s)."
    )
    return first_frame, fps, frame_h, frame_w, frames


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Sélection de la région d'intérêt (ROI)

    Pour choisir l'objet à suivre, déplacez les curseurs ci-dessous pour centrer le **rectangle rouge**
    sur le disque jaune du pendule. Le rectangle doit contenir tout le disque, sans trop de fond autour.

    Dans OpenCV, un rectangle (*bounding box*) est décrit par le quadruplet `(x, y, w, h)` où `(x, y)` sont
    les coordonnées du **coin supérieur gauche** (l'axe $y$ est orienté **vers le bas**) et `(w, h)` la largeur et la hauteur.
    """)
    return


@app.cell
def _(frame_h, frame_w, mo):
    # Curseurs interactifs pour choisir le rectangle (valeurs par défaut au centre de l'image)
    bbox_x = mo.ui.slider(0, frame_w, value=frame_w // 2, label="Centre X du rectangle", show_value=True)
    bbox_y = mo.ui.slider(0, frame_h, value=frame_h // 2, label="Centre Y du rectangle", show_value=True)
    bbox_w = mo.ui.slider(10, frame_w // 2, value=min(60, frame_w // 2), label="Largeur", show_value=True)
    bbox_h = mo.ui.slider(10, frame_h // 2, value=min(60, frame_h // 2), label="Hauteur", show_value=True)
    run_button = mo.ui.run_button(label="Lancer le suivi")

    roi_controls = mo.hstack([bbox_x, bbox_y, bbox_w, bbox_h], justify="space-between", wrap=True)
    return bbox_h, bbox_w, bbox_x, bbox_y, roi_controls, run_button


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 1 : du centre au coin supérieur gauche

    Les curseurs donnent le **centre** $(c_x, c_y)$, la largeur $w$ et la hauteur $h$ du rectangle.
    Calculez les coordonnées `(x1, y1)` du **coin supérieur gauche** (en pixels entiers, et jamais négatives),
    puis le rectangle au format OpenCV `bbox = (x1, y1, w, h)`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice": mo.md(
                r"""
                Le coin supérieur gauche est à une demi-largeur à gauche et une demi-hauteur au-dessus du centre :
                $x_1 = c_x - w/2$. Utilisez la division entière `//` pour obtenir un entier,
                et `max(0, ...)` pour ne pas sortir de l'image.
                """
            )
        }
    )
    return


@app.cell
def _(bbox_h, bbox_w, bbox_x, bbox_y):
    _cx = bbox_x.value
    _cy = bbox_y.value
    _bw = bbox_w.value
    _bh = bbox_h.value

    x1 = max(0, _cx - _bw // 2)
    y1 = max(0, _cy - _bh // 2)

    bbox = None if (x1 is None or y1 is None) else (int(x1), int(y1), _bw, _bh)
    return (bbox,)


@app.cell
def _(bbox, cv2, first_frame, mo, roi_controls, run_button):
    if bbox is None:
        _img_output = mo.callout(mo.md("Complétez le **TODO 1** pour afficher le rectangle."), kind="warn")
    else:
        # On dessine sur une copie de la première image
        _draw_frame = first_frame.copy()
        _x1, _y1, _bw, _bh = bbox
        cv2.rectangle(_draw_frame, (_x1, _y1), (_x1 + _bw, _y1 + _bh), (0, 0, 255), 2)
        # Conversion BGR -> RGB pour l'affichage
        _img_output = mo.image(cv2.cvtColor(_draw_frame, cv2.COLOR_BGR2RGB), width=450)

    mo.vstack(
        [
            mo.md("Ajustez la zone à suivre :"),
            roi_controls,
            mo.md(f"Rectangle courant `(x, y, w, h)` = `{bbox}`"),
            run_button,
            _img_output,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Principe du suivi : la corrélation de motif (*template matching*)

    Le notebook d'origine utilise le *tracker* **CSRT** d'OpenCV (Lukežič *et al.*,
    [*Discriminative Correlation Filter with Channel and Spatial Reliability*](https://openaccess.thecvf.com/content_cvpr_2017/html/Lukezic_Discriminative_Correlation_Filter_CVPR_2017_paper.html), CVPR 2017).
    Ce *tracker* n'est malheureusement pas disponible dans la version d'OpenCV qui tourne dans le navigateur.
    Nous utilisons donc une méthode plus simple, qui repose sur la même idée de **corrélation** :

    1. on découpe dans la première image le **motif** $T$ (le contenu du rectangle choisi) ;
    2. pour chaque nouvelle image $I$, on fait glisser le motif sur toute l'image et on calcule en chaque
       position $(x, y)$ un **coefficient de corrélation normalisé** $R(x, y)$ (formule ci-dessous) ;
    3. la position du motif dans la nouvelle image est celle où $R$ est **maximal** ($R = 1$ pour une correspondance parfaite).

    $$R(x,y) = \frac{\sum_{x',y'} T'(x',y')\, I'(x+x', y+y')}{\sqrt{\sum_{x',y'} T'(x',y')^2 \sum_{x',y'} I'(x+x',y+y')^2}}$$

    où $T'$ et $I'$ sont le motif et la portion d'image auxquels on a retranché leur moyenne.

    OpenCV fournit ce calcul avec `cv2.matchTemplate(image, motif, cv2.TM_CCOEFF_NORMED)`,
    qui renvoie la carte $R$, et `cv2.minMaxLoc(R)`, qui renvoie `(min_val, max_val, min_loc, max_loc)`.
    Les positions `min_loc` et `max_loc` sont des couples `(x, y)`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### TODO 2 : localiser le motif dans une image

    Complétez la fonction `localiser(frame, motif)` qui renvoie le triplet `(x, y, score)` :
    `(x, y)` est le **coin supérieur gauche** de la meilleure correspondance du motif dans l'image,
    et `score` la valeur maximale de corrélation correspondante.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md(
                "Calculez d'abord la carte de corrélation `R = cv2.matchTemplate(frame, motif, cv2.TM_CCOEFF_NORMED)`."
            ),
            "💡 Indice 2": mo.md(
                "`_, score, _, (x, y) = cv2.minMaxLoc(R)` récupère directement la valeur et la position du maximum."
            ),
        }
    )
    return


@app.cell
def _(cv2):
    def localiser(frame, motif):
        """Renvoie (x, y, score) : coin supérieur gauche de la meilleure correspondance et son score."""
        R = cv2.matchTemplate(frame, motif, cv2.TM_CCOEFF_NORMED)
        _, score, _, (x, y) = cv2.minMaxLoc(R)
        return x, y, score

    return (localiser,)


@app.cell(hide_code=True)
def _(bbox, first_frame, localiser, mo):
    # Vérification automatique du TODO 2 : dans la première image, le motif doit être retrouvé à sa place exacte.
    def _verifier():
        if bbox is None:
            return mo.callout(mo.md("Complétez d'abord le **TODO 1**."), kind="warn")
        _x1, _y1, _bw, _bh = bbox
        _motif = first_frame[_y1 : _y1 + _bh, _x1 : _x1 + _bw]
        try:
            _x, _y, _s = localiser(first_frame, _motif)
        except Exception as _e:
            return mo.callout(mo.md(f"❌ `localiser` a levé une erreur : `{_e!r}`"), kind="danger")
        if _x is None:
            return mo.callout(mo.md("**TODO 2** pas encore complété."), kind="warn")
        if (_x, _y) == (_x1, _y1) and _s > 0.99:
            return mo.callout(mo.md(f"✅ `localiser` retrouve le motif en ({_x}, {_y}) avec un score de {_s:.3f}."), kind="success")
        return mo.callout(
            mo.md(f"❌ Attendu ({_x1}, {_y1}) avec un score ≈ 1, obtenu ({_x}, {_y}) avec un score {_s}."),
            kind="danger",
        )

    _verifier()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Suivi image par image

    On parcourt maintenant toutes les images : pour chacune, on localise le motif et on enregistre la position
    du **centre** du rectangle. On obtient une liste `positions` dont chaque élément est `[numéro d'image, x_centre, y_centre]`.

    ### TODO 3 : position du centre

    Dans la boucle ci-dessous, à partir du coin supérieur gauche `(x, y)` renvoyé par `localiser` et de la taille
    `(w, h)` du motif, calculez les coordonnées `center_x`, `center_y` du centre du rectangle (en pixels entiers).

    Cliquez ensuite sur **« Lancer le suivi »** (plus haut) pour démarrer.
    """)
    return


@app.cell
def _(bbox, cv2, frames, localiser, mo, run_button):
    positions = []
    if bbox is None:
        mo.output.replace(mo.callout(mo.md("Complétez d'abord le **TODO 1**."), kind="warn"))
    elif not run_button.value:
        mo.output.replace(
            mo.md(
                "Placez le rectangle rouge sur le disque du pendule, puis cliquez sur **« Lancer le suivi »**."
            )
        )
    else:
        x, y, w, h = bbox
        motif = frames[0][y : y + h, x : x + w].copy()

        for frame_num, frame in enumerate(frames, start=1):
            x, y, score = localiser(frame, motif)
            if x is None:
                mo.output.replace(mo.callout(mo.md("Complétez d'abord le **TODO 2**."), kind="warn"))
                positions = []
                break

            center_x = x + w // 2
            center_y = y + h // 2
            if center_x is None or center_y is None:
                mo.output.replace(mo.callout(mo.md("Complétez le **TODO 3**."), kind="warn"))
                positions = []
                break

            positions.append([frame_num, center_x, center_y])

            # Affichage (une image sur deux pour aller plus vite dans le navigateur)
            if frame_num % 2 == 1 or frame_num == len(frames):
                _vis = frame.copy()
                cv2.rectangle(_vis, (x, y), (x + w, y + h), (58, 70, 245), 2)
                cv2.circle(_vis, (int(center_x), int(center_y)), max(2, int(0.1 * min(h, w))), (58, 70, 245), -1)
                cv2.putText(_vis, f"image {frame_num}  ({center_x},{center_y})  score {score:.2f}",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (58, 70, 245), 2)
                _small = cv2.resize(_vis, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                mo.output.replace(mo.image(cv2.cvtColor(_small, cv2.COLOR_BGR2RGB), width=450))
    return (positions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Post-traitement

    On trace les coordonnées $x$ et $y$ du centre en fonction du numéro d'image.
    """)
    return


@app.cell
def _(go, mo, np, positions):
    mo.stop(
        len(positions) == 0,
        mo.callout(mo.md("Lancez le suivi pour afficher la trajectoire."), kind="info"),
    )
    positions_1 = np.array(positions, dtype=float)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 1], mode="lines", name="X", line=dict(color="rgb(58,70,245)")))
    fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 2], mode="lines", name="Y", line=dict(color="rgb(23,15,48)")))
    fig.update_layout(
        title="Position en fonction du temps",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Numéro d'image",
        yaxis_title="Position (pixels)",
        legend=dict(x=0, y=1),
        width=900,
        height=500,
    )
    fig
    return (positions_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyse spectrale (transformée de Fourier)

    ### TODO 4 : fréquence dominante

    On cherche la fréquence d'oscillation du pendule à partir de la coordonnée $x$ :

    1. retirez la moyenne du signal (`x_detrended`), sinon le pic à fréquence nulle domine le spectre ;
    2. calculez l'amplitude de sa transformée de Fourier discrète pour les fréquences positives (`fft_vals`) ;
    3. calculez les fréquences associées (`freqs`), en **cycles par image** ;
    4. trouvez la fréquence `peak_freq` pour laquelle l'amplitude est maximale.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("Pour un signal réel, `np.fft.rfft(signal)` calcule la TFD pour les fréquences positives ; prenez-en la valeur absolue avec `np.abs`."),
            "💡 Indice 2": mo.md("`np.fft.rfftfreq(n, d=1.0)` donne les fréquences (en cycles par unité de `d`) pour un signal de `n` points espacés de `d`."),
            "💡 Indice 3": mo.md("`np.argmax(tableau)` renvoie l'indice du maximum."),
        }
    )
    return


@app.cell
def _(np, positions_1):
    # Numéros d'image et coordonnée X
    frames_vec = positions_1[:, 0]
    x_vec = positions_1[:, 1]

    # Signal centré (on retire la moyenne)
    x_detrended = x_vec - np.mean(x_vec)

    # Amplitude de la TFD et fréquences associées (cycles/image)
    fft_vals = np.abs(np.fft.rfft(x_detrended))
    freqs = np.fft.rfftfreq(len(x_vec), d=1.0)

    peak_freq = freqs[np.argmax(fft_vals)]
    return fft_vals, frames_vec, freqs, peak_freq, x_vec


@app.cell(hide_code=True)
def _(fft_vals, fps, freqs, go, mo, peak_freq):
    mo.stop(
        peak_freq is None or fft_vals is None or freqs is None,
        mo.callout(mo.md("Complétez le **TODO 4** pour afficher le spectre."), kind="warn"),
    )
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Bar(x=freqs, y=fft_vals, name="Amplitude spectrale", marker=dict(color="rgb(23,15,48)")))
    fig_fft.update_layout(
        title="Spectre du mouvement du pendule (FFT)",
        xaxis_title="Fréquence (cycles/image)",
        yaxis_title="Amplitude spectrale",
        plot_bgcolor="rgba(0,0,0,0)",
        width=900,
        height=350,
    )
    mo.md(
        f"""
        En calculant la transformée de Fourier discrète de la coordonnée $x$ du pendule, on isole la fréquence dominante de son oscillation :

        * **Fréquence du pic détecté** : `{peak_freq:.4f}` cycles/image
        * **Période d'oscillation** : `{1 / peak_freq:.2f}` images

        La caméra filmant à ${fps:.0f}$ images/s, cela correspond à une fréquence d'oscillation de `{peak_freq * fps:.2f} Hz`
        (période de `{1 / (peak_freq * fps):.3f} s`).

        **Question :** quelle est la résolution en fréquence $\\Delta f$ de ce spectre (écart entre deux fréquences successives) ?
        Qu'en déduisez-vous sur l'incertitude de la période mesurée ?

        {mo.as_html(fig_fft)}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ajustement par moindres carrés

    ### TODO 5 : ajustement d'une sinusoïde

    On modélise la position par $x(t) = A \sin(\omega t) + B \cos(\omega t) + C$, avec $\omega = 2\pi f_{\text{pic}}$
    et $t$ le numéro d'image compté à partir de 0. Ce modèle est **linéaire** en $(A, B, C)$ : on peut l'écrire
    $\mathbf{x} \approx M \mathbf{p}$ avec $\mathbf{p} = (A, B, C)$ et la matrice $M$ dont les colonnes sont
    $\sin(\omega t)$, $\cos(\omega t)$ et $1$.

    1. construisez la matrice `M` ;
    2. résolvez le problème aux moindres carrés pour obtenir `params` ;
    3. calculez la courbe ajustée `fit_x`, l'amplitude `amplitude_fit` $=\sqrt{A^2+B^2}$, le centre `offset_fit` $= C$
       et l'écart quadratique moyen des résidus `rmse`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Indice 1": mo.md("`np.column_stack([a, b, c])` assemble des vecteurs colonne en une matrice ; `np.ones_like(t)` crée un vecteur de 1."),
            "💡 Indice 2": mo.md("`params, _, _, _ = np.linalg.lstsq(M, x_vec, rcond=None)` résout le problème aux moindres carrés ; `M @ params` donne la courbe ajustée."),
            "💡 Indice 3": mo.md("RMSE $= \\sqrt{\\frac{1}{N}\\sum_i (x_i - \\hat x_i)^2}$ : `np.sqrt(np.mean(residus**2))`."),
        }
    )
    return


@app.cell
def _(frames_vec, mo, np, peak_freq, x_vec):
    mo.stop(peak_freq is None)
    omega = 2 * np.pi * peak_freq
    t_vals = frames_vec - 1  # temps en images, à partir de 0

    # Matrice du modèle linéaire
    M = np.column_stack([np.sin(omega * t_vals), np.cos(omega * t_vals), np.ones_like(t_vals)])

    # Résolution aux moindres carrés
    params, _, _, _ = np.linalg.lstsq(M, x_vec, rcond=None)
    fit_x = M @ params

    # Paramètres physiques et résidus
    amplitude_fit = np.sqrt(params[0] ** 2 + params[1] ** 2)
    offset_fit = params[2]
    residuals = x_vec - fit_x
    rmse = np.sqrt(np.mean(residuals**2))
    return amplitude_fit, fit_x, offset_fit, rmse


@app.cell(hide_code=True)
def _(amplitude_fit, fit_x, frames_vec, go, mo, offset_fit, rmse, x_vec):
    mo.stop(
        fit_x is None or rmse is None,
        mo.callout(mo.md("Complétez le **TODO 5** pour afficher l'ajustement."), kind="warn"),
    )
    fig_fit = go.Figure()
    fig_fit.add_trace(go.Scatter(x=frames_vec, y=x_vec, mode="markers", name="X mesuré (OpenCV)", marker=dict(color="rgb(58,70,245)", size=6)))
    fig_fit.add_trace(go.Scatter(x=frames_vec, y=fit_x, mode="lines", name="Sinusoïde ajustée", line=dict(color="rgb(245,70,58)", width=2)))
    fig_fit.update_layout(
        title="Trajectoire mesurée et ajustement",
        xaxis_title="Numéro d'image",
        yaxis_title="Coordonnée X (pixels)",
        plot_bgcolor="rgba(0,0,0,0)",
        width=900,
        height=380,
        legend=dict(x=0, y=1),
    )
    mo.md(
        f"""
        ## Ajustement par moindres carrés et bruit de suivi

        L'ajustement de la position mesurée du pendule par un modèle sinusoïdal donne :

        * **Amplitude d'oscillation ajustée** : `{amplitude_fit:.2f}` pixels
        * **Centre d'oscillation ajusté** : `{offset_fit:.2f}` pixels
        * **Écart-type des résidus (RMSE)** : `{rmse:.4f}` pixels

        Le **RMSE** mesure l'écart moyen entre la position suivie et un modèle sinusoïdal parfait. Il englobe le bruit
        de la caméra, la dérive de l'algorithme de suivi et les perturbations physiques réelles
        (par exemple l'amortissement, ou le fait que les grandes oscillations d'un pendule ne sont pas exactement sinusoïdales).

        {mo.as_html(fig_fit)}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyse physique : suivi vidéo réel et incertitudes

    Lorsqu'on suit un objet physique réel (comme le pendule de `pend.mp4`), des facteurs supplémentaires
    influencent la qualité des mesures par rapport à une simulation numérique idéale.

    ### Étalonnage spatial (des pixels aux unités physiques)
    L'algorithme de suivi mesure des positions en **pixels** ($x_{\text{pixel}}$). Pour les convertir en coordonnées
    physiques ($x_{\text{mètres}}$), il faut un facteur d'étalonnage $C$ (en mètres/pixel) :
    $$x_{\text{mètres}} = C \cdot x_{\text{pixel}}$$

    * **Incertitude d'étalonnage** : comment mesurer $C$ ? En général, en plaçant un objet de longueur connue $L$
      (une règle par exemple) dans le même plan que le mouvement et en mesurant sa longueur en pixels $N_{\text{pixel}}$ : $C = L / N_{\text{pixel}}$.
    * L'incertitude sur le repérage des extrémités de la règle dans l'image se propage directement au facteur $C$,
      et donc à toutes les positions physiques calculées.

    ### Erreurs systématiques et erreurs aléatoires
    * **Erreurs systématiques** :
      * **Parallaxe** : si l'axe optique de la caméra n'est pas parfaitement perpendiculaire au plan du mouvement,
        les distances plus proches de la caméra paraissent plus grandes que les distances plus éloignées.
      * **Distorsion de l'objectif** : les objectifs (surtout grand-angle) déforment l'image (distorsion en barillet ou en coussinet),
        ce qui décale les coordonnées en pixels par rapport à la projection physique réelle.
      * **Biais de l'algorithme de suivi** : le rectangle suivi peut dériver légèrement pendant l'oscillation,
        ce qui introduit un décalage systématique de phase ou de position.
    * **Erreurs aléatoires** :
      * **Bruit du capteur** : le bruit thermique et le bruit de photons du capteur modifient légèrement les valeurs des pixels
        d'une image à l'autre, ce qui peut faire fluctuer le rectangle suivi.
      * **Éclairage et reflets** : ombres et reflets peuvent déplacer le « centre » apparent de l'objet,
        ajoutant un bruit haute fréquence au barycentre mesuré.

    ### Échantillonnage et analyse du signal
    * Les vidéos réelles ont une fréquence d'images fixe (par exemple $30$ ou $60$ images/s).
    * Si l'on veut mesurer l'accélération de la pesanteur $g$ à partir de la période du pendule $T = 2\pi\sqrt{L/g}$,
      l'incertitude sur la mesure du temps $\delta t$ dépend directement de l'intervalle entre deux images $\Delta t = 1/f_s$.
      Pour une vidéo à $60$ images/s, ce pas de temps vaut $\approx 16{,}7$ ms.

    ### Questions
    1. Recommencez le suivi avec un rectangle beaucoup plus grand que le disque, puis beaucoup plus petit. Que constatez-vous ?
    2. Le score de corrélation affiché pendant le suivi diminue-t-il au cours du temps ? Pourquoi ?
    3. Estimez l'incertitude sur la période $T$ obtenue par la FFT, puis par l'ajustement. Laquelle est la plus précise ?
    """)
    return


if __name__ == "__main__":
    app.run()
