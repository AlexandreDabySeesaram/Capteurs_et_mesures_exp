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
    return cv2, np, tt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Choose the video file and select the ROI
    """)
    return


@app.cell
def _(tt):
    video_path  = "Resources/Pendulum/pend.mp4"  
    bbox        = tt.select_ROI(video_path)
    return bbox, video_path


@app.cell
def _():
    # video_player = mo.video(src=open(video_path, "rb"), width=450, loop=True)
    # video_player
    return


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
def _(bbox, cv2, mo, video_path):
    import time

    if bbox is None or bbox == (0, 0, 0, 0):
        mo.output.replace(mo.md("⚠️ Please select a Region of Interest (ROI) first."))
        positions = []
    else:
        cap = cv2.VideoCapture(video_path)
        flag, frame = cap.read()

        if not flag:
            mo.output.replace(mo.md("❌ Error: Could not read the video file."))
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
    positions_1 = np.array(positions)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 1], mode='lines', name='X', line=dict(color='rgb(58,70,245)')))
    fig.add_trace(go.Scatter(x=positions_1[:, 0], y=positions_1[:, 2], mode='lines', name='Y', line=dict(color='rgb(23,15,48)')))
    fig.update_layout(title='Position over time', plot_bgcolor='rgba(0,0,0,0)', xaxis_title='Frame number', yaxis_title='Position (pixels)', legend=dict(x=0, y=1), width=900, height=500)
    fig.show()  # Remove background color
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
