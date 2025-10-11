
# Welcome!

* An website version can browsed here : [https://alexandredabyseesaram.github.io/Tracking_video/](https://alexandredabyseesaram.github.io/Tracking_video/)

To run the notebook locally you'll need to setup an environment with opencv, matplotlib and numpy. Follow these steps to create a Conda environment named `tracking-ev` with Python 3.13 and all required packages:

```bash
# Create a new conda environment with Python 3.13
conda create -n tracking-ev python=3.13 -y

# Activate the environment
conda activate tracking-ev

# Install required packages: OpenCV (with contrib modules), NumPy, and Matplotlib
conda install -c conda-forge opencv=4.8.0 matplotlib numpy -y
```