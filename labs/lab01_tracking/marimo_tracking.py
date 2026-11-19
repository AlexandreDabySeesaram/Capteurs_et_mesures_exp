import marimo

__generated_with = "0.18.4"
app = marimo.App(width="columns")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    bibliography: Resources/tracking.bib
    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Small tracking notebook

    In this jupyter notebook we will see how to use OpenCV to track an object in a video. We'll first select the object (Region Of Interest) then track it through the frame and finally we' ll plot the evolution of the barycenter of the object with regard to the frame number.

    ## Import the used libraries

    We'll need

    * OpenCV (cv2)
    * tracking_tools to read the ROI
    * matplotlib to do our plots
    * IPython.display for the inline display of the tracked video in the notebook
    """)
    return


@app.cell
def _():
    import cv2
    from IPython.display import display, clear_output
    import numpy as np
    import tracking_tools as tt
    import matplotlib.pyplot as plt
    import PIL.Image
    import io
    return PIL, cv2, io, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Choose the video file and select the ROI (Region Of Interest)
    To select the object you want to track, adjust the sliders below to center the red bounding box on the pendulum bob. This runs entirely in your browser without requiring server-side window popups!
    """)
    return


@app.cell
def _(cv2):
    video_path = "Resources/Pendulum/pend.mp4"

    # Read the first frame to get dimensions and initialize slider ranges
    _cap = cv2.VideoCapture(video_path)
    _flag, first_frame = _cap.read()
    _cap.release()

    if _flag:
        frame_h, frame_w = first_frame.shape[:2]
        # print("flag")
    else:
        # print("non flag")
        first_frame = None
        frame_h, frame_w = 480, 640
    return first_frame, frame_h, frame_w, video_path


@app.cell
def _(frame_h, frame_w, mo):
    # Interactive sliders for bbox selection
    # Set default values close to the center of the frame
    bbox_x = mo.ui.slider(0, frame_w, value=frame_w // 2, label="Box Center X")
    bbox_y = mo.ui.slider(0, frame_h, value=frame_h // 2, label="Box Center Y")
    bbox_w = mo.ui.slider(10, frame_w // 2, value=min(60, frame_w // 2), label="Box Width")
    bbox_h = mo.ui.slider(10, frame_h // 2, value=min(60, frame_h // 2), label="Box Height")
    run_button = mo.ui.run_button(label="Start Tracking")

    roi_controls = mo.hstack([bbox_x, bbox_y, bbox_w, bbox_h], justify="space-between")
    return bbox_h, bbox_w, bbox_x, bbox_y, roi_controls, run_button


@app.cell
def _(
    PIL,
    bbox_h,
    bbox_w,
    bbox_x,
    bbox_y,
    cv2,
    first_frame,
    io,
    mo,
    roi_controls,
    run_button,
):
    if first_frame is not None:
        _h, _w = first_frame.shape[:2]
        # Copy frame to draw on it
        _draw_frame = first_frame.copy()

        # Calculate bbox coordinates (top-left x, y, width, height)
        _cx = bbox_x.value
        _cy = bbox_y.value
        _bw = bbox_w.value
        _bh = bbox_h.value

        _x1 = max(0, _cx - _bw // 2)
        _y1 = max(0, _cy - _bh // 2)

        # Draw red bounding box
        cv2.rectangle(_draw_frame, (_x1, _y1), (_x1 + _bw, _y1 + _bh), (0, 0, 255), 2)

        # Convert BGR to RGB for PIL/Marimo
        _rgb_frame = cv2.cvtColor(_draw_frame, cv2.COLOR_BGR2RGB)

        _img = PIL.Image.fromarray(_rgb_frame)
        _buf = io.BytesIO()
        _img.save(_buf, format="PNG")

        _img_output = mo.image(src=_buf.getvalue(), width=450)

        # Bounding box in OpenCV format: (x_min, y_min, w, h)
        bbox = (_x1, _y1, _bw, _bh)
    else:
        _img_output = mo.md("Video not loaded yet.")
        bbox = (0, 0, 0, 0)

    roi_panel = mo.vstack([
        mo.md("Adjust the target area:"),
        roi_controls,
        run_button,
        _img_output
    ])
    roi_panel
    return (bbox,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Initialise the tracker

    The tracker is the **CSRT** tracker from OpenCV based on [@lukezicDiscriminativeCorrelationFilter2017] that we initialised based of the **bounding box** surrounding delimiting the ROI.
    """)
    return


@app.cell
def _():
    # Tracker initialization is now combined with the tracking loop to avoid state conflicts
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Actual tracking
    We now loop over the frame to perform the actual tracking and store the positino of the barycenter of the ROI for each frame.
    """)
    return


@app.cell
def _(bbox, cv2, mo, run_button, video_path):
    import time

    if not run_button.value:
        mo.output.replace(
            mo.md(
                "Adjust the sliders above to position the red box on the pendulum, then click **'Start Tracking'** to execute the OpenCV tracker."
            )
        )
        positions = []
    elif bbox is None or bbox == (0, 0, 0, 0):
        mo.output.replace(mo.md("Please select a valid Region of Interest (ROI) first."))
        positions = []
    else:
        cap = cv2.VideoCapture(video_path)
        flag, frame = cap.read()

        if not flag:
            mo.output.replace(mo.md("Error: Could not read the video file."))
            positions = []
        else:
            if hasattr(cv2, 'legacy'):
                tracker = cv2.legacy.TrackerCSRT_create()
            else:
                tracker = cv2.TrackerCSRT_create()

            tracker.init(frame, bbox)

            x, y, w, h = [int(v) for v in bbox]
            center_x = x + w // 2
            center_y = y + h // 2
            positions = [[1, center_x, center_y]]

            frame_num = 1
            while True:
                frame_num += 1
                flag_read, frame = cap.read()
                if not flag_read:
                    break

                flag_track, bbox_1 = tracker.update(frame)
                if flag_track:
                    x, y, w, h = [int(v) for v in bbox_1]
                    center_x = x + w // 2
                    center_y = y + h // 2
                    positions.append([frame_num, center_x, center_y])
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (245, 70, 58), 2)
                    cv2.circle(frame, (center_x, center_y), int(0.1 * min(h, w)), (245, 70, 58), -1)
                    cv2.putText(frame, f'({center_x},{center_y})', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 70, 58), 2)
                else:
                    cv2.putText(frame, 'Lost', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (247, 59, 218), 2)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mo.output.replace(mo.image(rgb))
                time.sleep(0.01)

            cap.release()
    return (positions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Post-processing
    """)
    return


@app.cell
def _(np, positions):
    #| code-fold: true
    import plotly.graph_objects as go
    import plotly.io as pio
    pio.renderers.default = 'notebook_connected'
    if len(positions) == 0:
        positions_1 = None
    else:
        positions_1 = np.array(positions)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 1], mode='lines', name='X', line=dict(color='rgb(58,70,245)')))
        fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 2], mode='lines', name='Y', line=dict(color='rgb(23,15,48)')))
        fig.update_layout(title='Position over time', plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Frame number', yaxis_title='Position (pixels)', legend=dict(x=0, y=1), width=900, height=500)
        fig.show()  # Remove background color
    return go, positions_1


@app.cell
def _(go, mo, np, positions_1):
    mo.stop(positions_1 is None)

    # Extract frame numbers and X coordinates
    frames_vec = positions_1[:, 0]
    x_vec = positions_1[:, 1]

    # Detrend data (remove mean)
    x_detrended = x_vec - np.mean(x_vec)

    # Compute FFT
    fft_vals = np.abs(np.fft.rfft(x_detrended))
    freqs = np.fft.rfftfreq(len(x_vec), d=1.0) # cycles/frame

    peak_idx = np.argmax(fft_vals)
    peak_freq = freqs[peak_idx]

    # Plot power spectrum
    fig_fft = go.Figure()
    fig_fft.add_trace(
        go.Bar(
            x=freqs,
            y=fft_vals,
            name='Spectral Power',
            marker=dict(color='rgb(23,15,48)')
        )
    )
    fig_fft.update_layout(
        title='Pendulum Frequency Power Spectrum (FFT)',
        xaxis_title='Frequency (cycles/frame)',
        yaxis_title='Spectral Amplitude',
        plot_bgcolor='rgba(0,0,0,0)',
        width=900,
        height=350
    )
    return fig_fft, frames_vec, peak_freq, x_vec


@app.cell(hide_code=True)
def _(fig_fft, mo, peak_freq):
    mo.stop(fig_fft is None)
    mo.md(
        f"""
        ## Spectral Analysis (Fourier Transform)
        By computing the Discrete Fourier Transform of the pendulum's X coordinate, we isolate the dominant frequency of its swing:

        * **Detected Peak Frequency**: `{peak_freq:.4f}` cycles/frame
        * **Oscillation Period**: `{1/peak_freq:.2f}` frames

        Assuming a camera frame rate of $60\text{{ fps}}$, this corresponds to an oscillation frequency of `{peak_freq * 60:.2f}\text{{ Hz}}` (Period of `{1/(peak_freq * 60):.3f}\text{{ seconds}}`).

        {mo.as_html(fig_fft)}
        """
    )
    return


@app.cell
def _(frames_vec, go, mo, np, peak_freq, x_vec):
    mo.stop(frames_vec is None or x_vec is None or peak_freq is None)

    # Fit physical pendulum X position to a sine wave: x(t) = A*sin(omega*t) + B*cos(omega*t) + C
    omega = 2 * np.pi * peak_freq
    t_vals = frames_vec - 1  # 0-indexed time

    # Design matrix
    M = np.column_stack([np.sin(omega * t_vals), np.cos(omega * t_vals), np.ones_like(t_vals)])

    # Solve least-squares
    params, _, _, _ = np.linalg.lstsq(M, x_vec, rcond=None)
    fit_x = M @ params

    # Calculate parameters
    amplitude_fit = np.sqrt(params[0]**2 + params[1]**2)
    offset_fit = params[2]
    residuals = x_vec - fit_x
    rmse = np.sqrt(np.mean(residuals**2))

    # Plot tracking results vs sine fit
    fig_fit = go.Figure()
    fig_fit.add_trace(
        go.Scatter(
            x=frames_vec,
            y=x_vec,
            mode='markers',
            name='OpenCV Measured X',
            marker=dict(color='rgb(58,70,245)', size=6)
        )
    )
    fig_fit.add_trace(
        go.Scatter(
            x=frames_vec,
            y=fit_x,
            mode='lines',
            name='Least-Squares Sine Fit',
            line=dict(color='rgb(245,70,58)', width=2)
        )
    )
    fig_fit.update_layout(
        title='OpenCV Trajectory Fitting & Residuals',
        xaxis_title='Frame number',
        yaxis_title='X Coordinate (pixels)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=900,
        height=380,
        legend=dict(x=0, y=1)
    )
    return amplitude_fit, fig_fit, offset_fit, rmse


@app.cell(hide_code=True)
def _(amplitude_fit, fig_fit, mo, offset_fit, rmse):
    mo.stop(fig_fit is None)
    mo.md(
        f"""
        ## Least-Squares Fitting & Tracking Noise
        Fitting the tracked position of the physical pendulum to a sinusoidal model gives:

        * **Fitted Swing Amplitude**: `{amplitude_fit:.2f}` pixels
        * **Fitted Center of Swing**: `{offset_fit:.2f}` pixels
        * **Residual Standard Deviation (RMSE)**: `{rmse:.4f}` pixels

        The **RMSE** shows the average deviation of the OpenCV tracker from a perfect sinusoidal model. This encapsulates camera noise, algorithm tracking drift, and physical perturbations in the lab.

        {mo.as_html(fig_fit)}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Physics Lab Analysis: Real Video Tracking & Uncertainty

    When tracking a real physical object (like the pendulum in `pend.mp4`), additional real-world factors influence the quality of our measurements compared to a clean digital simulation.

    ###  Spatial Calibration (Pixels to Physical Units)
    Our tracking algorithm measures positions in **pixels** ($x_{\text{pixel}}$). To convert this to physical coordinates ($x_{\text{meters}}$), we need a calibration factor $C$ (in meters/pixel):
    $$x_{\text{meters}} = C \cdot x_{\text{pixel}}$$

    * **Calibration Uncertainty**: How do we measure $C$? Typically, by placing a reference object of known length $L$ (like a ruler) in the same plane as the motion, measuring its pixel length $N_{\text{pixel}}$, so $C = L / N_{\text{pixel}}$.
    * The uncertainty in identifying the ruler's endpoints in the image propagates directly to our calibration factor $C$ and thus to all calculated physical positions.

    ###  Systematic vs. Random Errors
    * **Systematic Errors**:
      * **Parallax Error**: If the camera optical axis is not perfectly perpendicular to the plane of the pendulum's motion, distances closer to the camera will appear larger than distances further away.
      * **Lens Distortion**: Camera lenses (especially wide-angle ones) distort the image (barrel/pincushion distortion), shifting pixel coordinates away from their true physical projection.
      * **Tracking Algorithm Bias**: The CSRT tracker bounding box might drift slightly during the swing, introducing a systematic phase or position shift.
    * **Random Errors**:
      * **Camera Sensor Noise**: Random thermal/shot noise in the camera sensor changes pixel values slightly from frame to frame, which can introduce small fluctuations in the tracker bounding box.
      * **Lighting/Reflections**: Shadows and glare can shift the center of color of the object, adding high-frequency noise to the measured barycenter.

    ###  Sampling & Signal Analysis
    * Real video files have fixed frame rates (e.g., $30\text{ fps}$ or $60\text{ fps}$).
    * If you want to measure the acceleration of gravity $g$ from the pendulum's period $T = 2\pi\sqrt{L/g}$, the uncertainty of your time measurement $\delta t$ depends directly on the frame interval $\Delta t = 1/f_s$. For a $60\text{ fps}$ video, the time step is $\approx 16.7\text{ ms}$.
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
