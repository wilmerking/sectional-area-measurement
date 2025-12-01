# Sectional Area Calculator

A Python tool to calculate and visualize the cross-sectional area distribution of STL models along the X, Y, and Z axes.

## Features

- **Auto-detection**: Automatically finds STL files in the current directory.
- **Multi-Axis Analysis**: Calculates cross-sectional areas along X, Y, and Z axes.
- **Interactive Visualization**: View graphs for each axis using a tabbed interface.
- **Robust Slicing**: Handles complex geometries using `trimesh` and `shapely`/`networkx`.

## Installation

1.  **Clone the repository** (or download the files).
2.  **Set up a virtual environment** (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install trimesh numpy matplotlib networkx rtree scipy
    ```
    *Note: `rtree` is required for accurate polygon calculations.*

## Usage

### Command Line Interface (CLI)
1.  Place your STL file in the same directory as the script.
2.  Run the script:
    ```bash
    python3 area_calculator.py
    ```
3.  If multiple STL files are found, you will be prompted to select one.

### Web Interface (Streamlit)
1.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
2.  Upload your STL file in the browser window.
3.  Adjust the number of slices and click "Calculate Area Distribution".

## Requirements

- Python 3.x
- `trimesh`
- `numpy`
- `matplotlib`
- `networkx`
- `rtree`
