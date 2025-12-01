# Sectional Area Calculator

A web-based tool to calculate and visualize the cross-sectional area distribution of STL models along the X, Y, and Z axes.

## Features

- **Web Interface**: Easy-to-use Streamlit web application
- **File Upload**: Simply drag and drop or browse for your STL file
- **Unit Selection**: Choose from inches, feet, yards, millimeters, centimeters, or meters
- **Multi-Axis Analysis**: Calculates cross-sectional areas along X, Y, and Z axes
- **Interactive Tabs**: View graphs for each axis in separate tabs
- **Customizable Slicing**: Adjust the number of slices for precision vs. speed
- **Interactive Visualizations**: Zoom, pan, and hover to explore data with Plotly charts

## Installation

1.  **Clone the repository** (or download the files).
2.  **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```
2.  **Open your browser** to the URL shown (typically http://localhost:8501)
3.  **Upload your STL file** using the file uploader
4.  **Select the original model units** (e.g., inches, millimeters)
5.  **Adjust the number of slices** (more slices = smoother graph but slower)
6.  **Click "Calculate Area Distribution"** to generate the graphs
7.  **Switch between X, Y, and Z axis tabs** to view different orientations

## Requirements

- Python 3.x
- `streamlit`
- `trimesh`
- `numpy`
- `plotly` (for interactive visualizations)
- `networkx`
- `rtree`
- `scipy`
