import marimo

__generated_with = "0.18.4"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import marimo as mo
    import numpy as np
    import PIL.Image
    import io
    import time
    import plotly.graph_objects as go
    return PIL, go, io, mo, np, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1D Object Tracking with NumPy

    In this notebook, we demonstrate how to perform simple object tracking using **pure NumPy** operations.
    We will:
    1. Generate a synthetic "video" of a black dot moving sinusoidally along the X-axis on a white background.
    2. Track the dot frame-by-frame by finding the barycenter (center of mass) of the black pixels.
    3. Plot the trajectory of the tracked object over time using Plotly.
    """)
    return


@app.cell
def _(mo):
    # Controls to customize the simulation
    num_frames = mo.ui.slider(10, 200, value=100, label="Number of Frames")
    width = mo.ui.slider(200, 800, value=600, label="Video Width (pixels)")
    height = mo.ui.slider(100, 400, value=200, label="Video Height (pixels)")
    radius = mo.ui.slider(2, 20, value=8, label="Dot Radius (pixels)")
    frequency = mo.ui.slider(0.01, 1.0, step=0.01, value=0.02, label="Frequency (cycles/frame)")

    controls = mo.hstack([num_frames, width, height, radius, frequency], justify="space-between")
    return controls, frequency, height, num_frames, radius, width


@app.cell(hide_code=True)
def _(controls, mo):
    mo.md(f"""
    ### Simulation Parameters
    Modify the parameters below to dynamically regenerate the synthetic video:

    {controls}
    """)
    return


@app.cell
def _(frequency, height, np, num_frames, radius, width):
    n_frames = num_frames.value
    _w = width.value
    _h = height.value
    _r = radius.value

    # Generate white background frames (value 255)
    frames = np.ones((n_frames, _h, _w), dtype=np.uint8) * 255
    true_x_positions = []

    for _t in range(n_frames):
        # Sinusoidal motion along X-axis
        x_center = int(_w / 2 + (_w / 2 - _r - 20) * np.sin(2 * np.pi * frequency.value * _t))
        y_center = int(_h / 2)
        true_x_positions.append(x_center)

        # Create a circle mask using np.ogrid
        _Y, _X = np.ogrid[:_h, :_w]
        dist_from_center = (_X - x_center)**2 + (_Y - y_center)**2
        _mask = dist_from_center <= _r**2
        frames[_t][_mask] = 0  # Draw black dot (value 0)
    return (frames,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## NumPy Object Tracking Loop

    For each frame, we locate the pixels that correspond to the black dot (`value < 128`). We then compute the mean of their coordinates (the barycenter) to track the X and Y positions.
    """)
    return


@app.cell
def _(PIL, frames, io, mo, np, time):
    tracked_positions = []
    _h, _w = frames.shape[1], frames.shape[2]

    for _t, frame in enumerate(frames):
        # 1. Find indices where pixels are black
        y_coords, x_coords = np.where(frame < 128)

        if len(x_coords) > 0:
            # Compute barycenter
            cx = int(np.mean(x_coords))
            cy = int(np.mean(y_coords))
            tracked_positions.append([_t + 1, cx, cy])
        else:
            cx, cy = int(_w / 2), int(_h / 2)
            tracked_positions.append([_t + 1, None, None])

        # 2. Draw a red crosshair on the RGB version of the frame
        # Convert grayscale frame to 3-channel RGB image
        rgb_frame = np.stack([frame, frame, frame], axis=-1)

        # Color crosshair red [245, 70, 58]
        rgb_frame[max(0, cy-1):min(_h, cy+2), max(0, cx-10):min(_w, cx+11)] = [245, 70, 58]
        rgb_frame[max(0, cy-10):min(_h, cy+11), max(0, cx-1):min(_w, cx+2)] = [245, 70, 58]

        # 3. Convert array to PNG bytes and display in the cell output
        img = PIL.Image.fromarray(rgb_frame)
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        mo.output.replace(
            mo.md(
                f"""
                ### Tracking Frame {_t+1}/{len(frames)}:
                * **Barycenter Coordinates**: ({cx}, {cy})

                {mo.image(src=buf.getvalue(), width=450)}
                """
            )
        )
        time.sleep(0.015)
    return (tracked_positions,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Physics Lab Analysis: Measurement, Resolution & Uncertainty

    In physics, making a measurement means mapping a physical property to a numerical value. When measuring from digital images, this mapping introduces specific limitations, errors, and uncertainties.

    ###  Spatial Resolution & Quantization Error
    A digital image is discretized into a grid of **pixels**.
    * The smallest measurable distance change in raw coordinates is $1\text{ pixel}$ ($\Delta x = 1$).
    * This spatial discretization leads to **Quantization Error**. For a uniform distribution of values within a pixel, the standard uncertainty is:
      $$\sigma_q = \frac{\Delta x}{\sqrt{12}} \approx 0.289\text{ pixels}$$

    #### Sub-Pixel Resolution & Centroid Estimation:
    Notice that our NumPy tracker calculates the barycenter (centroid) using `np.mean()`.
    * By averaging the coordinates of all pixels that make up the dot, we can calculate the center with **sub-pixel accuracy** (less than $1\text{ pixel}$ error!).
    * **Lab Exercise**: Reduce the **Dot Radius** slider to $2$ or $3$ pixels. What happens to the smoothness of the tracked position graph? Why does a larger dot size yield a smoother trajectory? (Hint: Averaging more pixels reduces the statistical uncertainty of the centroid).

    ###  Temporal Resolution & Nyquist-Shannon Sampling
    A video is a sequence of static frames captured at a specific sampling frequency (Frame Rate) $f_s$:
    * To reconstruct a physical motion of frequency $f_{\text{motion}}$ without **aliasing**, we must satisfy the **Nyquist Criterion**:
      $$f_s > 2 \cdot f_{\text{motion}}$$
    * If $f_s \le 2 \cdot f_{\text{motion}}$ (i.e. frequency > 0.5 cycles/frame), the motion will appear slower, stationary, or even reversed in direction (temporal aliasing).
    * **Lab Exercise (Temporal Spacing)**: Drag the **Number of Frames** slider down to a low value (e.g., $15$ or $20$). Observe the resulting Plotly trajectory. Is it still a smooth sine wave? How does temporal spacing affect our ability to resolve the shape of the trajectory?
    * **Lab Exercise (Aliasing)**: Slowly increase the **Frequency** slider from $0.02$ up to $0.45$, and then exceed the Nyquist limit by setting it to $0.52$ or $0.55$.
      * Observe the live tracking frames animation. What does the dot's motion look like when frequency is $0.50$ (exactly Nyquist)?
      * Look at the **Spectral Analysis (FFT)** cell. What happens to the detected peak frequency when the true input frequency is set to $0.55$? (Hint: Notice the warning alert that displays when the true frequency crosses the 0.5 Nyquist threshold!).
    """)
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md(r"""
    ## Trajectory Post-processing

    We plot the tracked X coordinates over frame numbers to show the sinusoidal movement.
    """)
    return


@app.cell
def _(go, np, tracked_positions):
    positions_arr = np.array(tracked_positions)
    frames_vec = positions_arr[:, 0]
    x_vec = positions_arr[:, 1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frames_vec,
            y=x_vec,
            mode='lines+markers',
            name='Tracked X Position',
            line=dict(color='rgb(58,70,245)', width=2),
            marker=dict(size=4)
        )
    )

    fig.update_layout(
        title='Dot Position along X-axis over Time',
        xaxis_title='Frame number',
        yaxis_title='X Coordinate (pixels)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=850,
        height=400,
        legend=dict(x=0, y=1)
    )

    fig.show()
    return frames_vec, x_vec


@app.cell
def _(frequency, go, np, x_vec):
    # Perform Fast Fourier Transform (FFT) on the detrended X coordinates
    x_detrended = x_vec - np.mean(x_vec)
    fft_vals = np.abs(np.fft.rfft(x_detrended))
    freqs = np.fft.rfftfreq(len(x_vec), d=1.0) # frequency in cycles/frame

    peak_idx = np.argmax(fft_vals)
    peak_freq = freqs[peak_idx]

    # Plot the power spectrum
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
        title='Frequency Power Spectrum (FFT)',
        xaxis_title='Frequency (cycles/frame)',
        yaxis_title='Spectral Amplitude',
        plot_bgcolor='rgba(0,0,0,0)',
        width=850,
        height=350
    )

    # Check for aliasing
    true_f = frequency.value
    nyquist_f = 0.5
    aliasing_alert = ""
    if true_f > nyquist_f:
        _epsilon = true_f - 0.5
        _beat_freq = 2 * _epsilon
        aliasing_alert = f"""
        > [!WARNING]
        > **Aliasing Detected!** The true input frequency (`{true_f:.2f}`) exceeds the **Nyquist Limit** of `{nyquist_f:.2f}` cycles/frame. 
        > The signal is undersampled (less than 2 frames per oscillation cycle), causing the system to observe a false lower frequency of `{peak_freq:.2f}` cycles/frame.

        #### 🔍 Why do we see a slow "envelope" (beating)?
        When we sample a sine wave of frequency $f = 0.5 + \\epsilon$ (here, $\\epsilon = {_epsilon:.2f}$), the discrete-time signal behaves as:
        $$x[n] = A \\sin(2\\pi (0.5 + \\epsilon) n) = A (-1)^n \\sin(2\\pi \\epsilon n)$$
        This is a **suppressed-carrier amplitude modulation (AM)**:
        * The **inner carrier** has a frequency of exactly $0.5$ cycles/frame (represented by the alternating $(-1)^n$ term).
        * The **slow envelope** modulates the amplitude at a frequency of $\\epsilon = {_epsilon:.2f}$ cycles/frame (period of `{1/_epsilon:.1f}` frames).

        #### 📊 Why does the FFT only show a single peak at `{peak_freq:.2f}`?
        In amplitude modulation, the spectral energy lies in the sidebands around the carrier:
        $$f_c \\pm f_m = 0.5 \\pm {_epsilon:.2f}$$
        which correspond to `{0.5 - _epsilon:.2f}` and `{0.5 + _epsilon:.2f}` cycles/frame.
        Because the discrete spectrum is periodic and symmetric, both of these wrap around to the **exact same frequency** of `{peak_freq:.2f}` cycles/frame. 

        There is **no** energy at the envelope frequency of `{_epsilon:.2f}` in the raw signal because the alternating $(-1)^n$ carrier cancels out any slow offset (the mean is zero). However, if you take the **absolute value** of the coordinates (rectification, $|x[n]|$), it removes the $(-1)^n$ carrier, and the FFT of $|x[n]|$ will show a clear peak at the envelope beat frequency of $2\\epsilon = {_beat_freq:.2f}$ cycles/frame!
        """
    return aliasing_alert, fig_fft, peak_freq, true_f


@app.cell(hide_code=True)
def _(aliasing_alert, fig_fft, mo, peak_freq, true_f):
    mo.md(f"""
    ## Spectral Analysis (Fourier Transform)
    To identify the dominant frequency of oscillation in the time domain, we compute the Discrete Fourier Transform of the spatial coordinates:

    * **True Input Frequency**: `{true_f:.4f}` cycles/frame
    * **Detected Peak Frequency**: `{peak_freq:.4f}` cycles/frame
    * **Measured Oscillation Period**: `{1/peak_freq:.2f}` frames

    {aliasing_alert}

    {mo.as_html(fig_fft)}
    """)
    return


@app.cell
def _(frames_vec, go, np, peak_freq, x_vec):
    # Fit the data to a sine wave: x(t) = A*sin(omega*t) + B*cos(omega*t) + C
    omega = 2 * np.pi * peak_freq
    t_vals = frames_vec - 1  # 0-indexed time

    # Design matrix for linear least-squares
    M = np.column_stack([np.sin(omega * t_vals), np.cos(omega * t_vals), np.ones_like(t_vals)])

    # Solve least-squares
    params, _, _, _ = np.linalg.lstsq(M, x_vec, rcond=None)
    fit_x = M @ params

    # Compute amplitude and residuals
    amplitude_fit = np.sqrt(params[0]**2 + params[1]**2)
    offset_fit = params[2]
    residuals = x_vec - fit_x
    rmse = np.sqrt(np.mean(residuals**2))

    # Plot raw vs fitted trajectory
    fig_fit = go.Figure()
    fig_fit.add_trace(
        go.Scatter(
            x=frames_vec,
            y=x_vec,
            mode='markers',
            name='Measured positions',
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
        title='Trajectory Fitting & Residuals',
        xaxis_title='Frame number',
        yaxis_title='X Coordinate (pixels)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=850,
        height=380,
        legend=dict(x=0, y=1)
    )
    return amplitude_fit, fig_fit, offset_fit, rmse


@app.cell(hide_code=True)
def _(amplitude_fit, fig_fit, mo, offset_fit, rmse):
    mo.md(f"""
    ## Least-Squares Fitting & Experimental Uncertainty
    We fit the trajectory to a sinusoidal model $x(t) = A \\cos(\\omega t + \\phi) + C$ using linear least-squares:

    * **Fitted Amplitude**: `{amplitude_fit:.2f}` pixels
    * **Fitted Offset (Center of Motion)**: `{offset_fit:.2f}` pixels
    * **Residual Standard Deviation (RMSE)**: `{rmse:.4f}` pixels

    The **RMSE** represents the experimental measurement uncertainty. Under pure quantisation error (with 1-pixel resolution), the theoretical minimum uncertainty is $\\sigma_q \\approx 0.289$ pixels. If your RMSE is below this, you have achieved **sub-pixel resolution**!

    {mo.as_html(fig_fit)}
    """)
    return


@app.cell(column=2)
def _():
    return


@app.cell
def _(go, height, np, num_frames, radius):
    # Sensitivity Analysis: Sweep Video Width (Resolution) and compute Physical RMSE
    _n_frames = num_frames.value
    _h = height.value
    _r = radius.value
    _L_physical = 1.0 # 1.0 meter physical width

    _widths = np.arange(100, 1001, 100)
    _physical_rmse_vals = []

    for _w in _widths:
        # Generate frames
        _frames = np.ones((_n_frames, _h, _w), dtype=np.uint8) * 255
        for _t in range(_n_frames):
            x_center_float = _w / 2 + (_w / 2 - _r - 20) * np.sin(2 * np.pi * _t / (_n_frames / 2))
            _Y, _X = np.ogrid[:_h, :_w]
            _mask = (_X - x_center_float)**2 + (_Y - _h/2)**2 <= _r**2
            _frames[_t][_mask] = 0

        # Track
        _tracked_x = []
        for _frame in _frames:
            _, _x_coords = np.where(_frame < 128)
            if len(_x_coords) > 0:
                _tracked_x.append(np.mean(_x_coords))
            else:
                _tracked_x.append(_w / 2)

        # Fit
        _omega = 2 * np.pi * (2 / _n_frames)
        _t_vals = np.arange(_n_frames)
        _M = np.column_stack([np.sin(_omega * _t_vals), np.cos(_omega * _t_vals), np.ones_like(_t_vals)])
        _params, _, _, _ = np.linalg.lstsq(_M, _tracked_x, rcond=None)
        _fit_x = _M @ _params
        _rmse = np.sqrt(np.mean((_tracked_x - _fit_x)**2))

        # Convert pixel RMSE to physical RMSE (meters)
        _physical_rmse = _rmse * (_L_physical / _w)
        _physical_rmse_vals.append(_physical_rmse)

    # Plot 1: Physical Uncertainty vs Resolution
    fig_res = go.Figure()
    fig_res.add_trace(
        go.Scatter(
            x=_widths,
            y=_physical_rmse_vals,
            mode='lines+markers',
            name='Physical RMSE',
            line=dict(color='rgb(58,70,245)', width=2)
        )
    )
    fig_res.update_layout(
        title='Physical Uncertainty vs. Resolution',
        xaxis_title='Image Width (pixels)',
        yaxis_title='Uncertainty (meters)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=400,
        height=320
    )

    # Sensitivity Analysis: Sweep Coordinate Noise and compute Fit RMSE
    _w_fixed = 600
    # True positions
    _true_x_clean = []
    for _t in range(_n_frames):
        x_center_float = _w_fixed / 2 + (_w_fixed / 2 - _r - 20) * np.sin(2 * np.pi * _t / (_n_frames / 2))
        _true_x_clean.append(x_center_float)
    _true_x_clean = np.array(_true_x_clean)

    _noise_stds = np.linspace(0.0, 3.0, 10)
    _fit_rmse_vals = []

    for _noise_std in _noise_stds:
        # Add random coordinate noise
        _noisy_x = _true_x_clean + np.random.normal(0, _noise_std, _n_frames)

        # Fit
        _omega = 2 * np.pi * (2 / _n_frames)
        _t_vals = np.arange(_n_frames)
        _M = np.column_stack([np.sin(_omega * _t_vals), np.cos(_omega * _t_vals), np.ones_like(_t_vals)])
        _params, _, _, _ = np.linalg.lstsq(_M, _noisy_x, rcond=None)
        _fit_x = _M @ _params
        _rmse = np.sqrt(np.mean((_noisy_x - _fit_x)**2))
        _fit_rmse_vals.append(_rmse)

    # Plot 2: Fit RMSE vs Coordinate Noise
    fig_noise = go.Figure()
    fig_noise.add_trace(
        go.Scatter(
            x=_noise_stds,
            y=_fit_rmse_vals,
            mode='lines+markers',
            name='Measured RMSE',
            line=dict(color='rgb(245,70,58)', width=2)
        )
    )
    # Add a theoretical x=y line
    fig_noise.add_trace(
        go.Scatter(
            x=_noise_stds,
            y=_noise_stds,
            mode='lines',
            name='Theoretical Limit',
            line=dict(color='gray', dash='dash')
        )
    )
    fig_noise.update_layout(
        title='Fit Uncertainty vs. Tracking Noise',
        xaxis_title='Added Noise Std Dev (pixels)',
        yaxis_title='Experimental Fit RMSE (pixels)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=400,
        height=320,
        legend=dict(x=0, y=1)
    )
    return fig_noise, fig_res


@app.cell(hide_code=True)
def _(fig_noise, fig_res, mo):
    mo.md(f"""
    ## Sensitivity Analysis Dashboard

    To understand the physics of measurement errors and camera calibration, we run two automated parameter sweeps:

    1. **Resolution Sensitivity (Left)**: Assuming the image width corresponds to a fixed physical size of $1.0 m$, we sweep the resolution. As resolution increases, the physical size of each pixel shrinks, and the physical tracking uncertainty decays as $1/Width$.
    2. **Noise Sensitivity (Right)**: We artificially inject random Gaussian noise into our tracked coordinates. The resulting least-squares fit **RMSE** closely matches the injected noise level (dashed line), proving that fit residuals act as a direct estimator of experimental noise.

    {mo.hstack([fig_res, fig_noise], justify="space-around")}
    """)
    return


if __name__ == "__main__":
    app.run()
