import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import PIL.Image
    import io
    import time
    import plotly.graph_objects as go
    return mo, np, PIL, io, time, go


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
    
    controls = mo.hstack([num_frames, width, height, radius], justify="space-between")
    
    mo.md(
        f"""
        ### Simulation Parameters
        Modify the parameters below to dynamically regenerate the synthetic video:
        
        {controls}
        """
    )
    return height, num_frames, radius, width


@app.cell
def _(height, num_frames, np, radius, width):
    n_frames = num_frames.value
    _w = width.value
    _h = height.value
    _r = radius.value
    
    # Generate white background frames (value 255)
    frames = np.ones((n_frames, _h, _w), dtype=np.uint8) * 255
    true_x_positions = []
    
    for _t in range(n_frames):
        # Sinusoidal motion along X-axis
        x_center = int(_w / 2 + (_w / 2 - _r - 20) * np.sin(2 * np.pi * _t / (n_frames / 2)))
        y_center = int(_h / 2)
        true_x_positions.append(x_center)
        
        # Create a circle mask using np.ogrid
        _Y, _X = np.ogrid[:_h, :_w]
        dist_from_center = (_X - x_center)**2 + (_Y - y_center)**2
        mask = dist_from_center <= _r**2
        frames[_t][mask] = 0  # Draw black dot (value 0)
        
    return frames, n_frames, true_x_positions


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## NumPy Object Tracking Loop
    
    For each frame, we locate the pixels that correspond to the black dot (`value < 128`). We then compute the mean of their coordinates (the barycenter) to track the X and Y positions.
    """)
    return


@app.cell
def _(frames, io, mo, np, PIL, time):
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
    return fig, positions_arr, x_vec, frames_vec


if __name__ == "__main__":
    app.run()
