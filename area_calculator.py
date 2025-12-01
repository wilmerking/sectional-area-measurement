import trimesh
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import glob

# --- CONFIGURATION SECTION ---
# 1. Put the name of your STL file here
# FILENAME = 'Flanged Finger Weldment FEA.stl' # Now auto-detected 

# 2. How many slices do you want? (More slices = smoother graph but slower)
NUM_SLICES = 100 
# -----------------------------

# Unit name mapping
UNIT_NAMES = {
    "in": "inches",
    "ft": "feet",
    "yd": "yards",
    "mm": "millimeters",
    "cm": "centimeters",
    "m": "meters"
}

def get_area_distribution(mesh, axis_direction, num_slices):
    """
    Calculates the cross-sectional area distribution along a specific axis.
    """
    axis_name = "Unknown"
    if np.array_equal(axis_direction, [1, 0, 0]): axis_name = "X"
    elif np.array_equal(axis_direction, [0, 1, 0]): axis_name = "Y"
    elif np.array_equal(axis_direction, [0, 0, 1]): axis_name = "Z"
    
    print(f"Analyzing geometry along {axis_name} axis...")
    
    # Get the bounding box of the mesh
    bounds = mesh.bounds
    
    # Determine start and end points along the chosen axis
    min_val = np.dot(bounds[0], axis_direction)
    max_val = np.dot(bounds[1], axis_direction)
    
    # Create the locations where we will slice
    slice_locations = np.linspace(min_val, max_val, num_slices)
    areas = []
    
    print(f"Slicing model into {num_slices} sections along {axis_name}...")

    for i, loc in enumerate(slice_locations):
        # Calculate the origin point for this specific slice
        origin = np.array(axis_direction) * loc
        
        # Slice the mesh
        slice_2d = mesh.section(plane_origin=origin, plane_normal=axis_direction)
        
        if slice_2d:
            # slice_2d is a Path3D, we need to convert it to a planar Path2D first
            # We use to_2D() instead of to_planar() to avoid deprecation warnings
            slice_planar, to_3D = slice_2d.to_2D()
            areas.append(slice_planar.area)
        else:
            areas.append(0.0)
            
    # Shift locations to start at 0 for plotting
    plot_locations = slice_locations - slice_locations[0]
            
    return plot_locations, areas

def get_stl_filename():
    # 1. Check command line arguments
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # 2. Search for STL files in the current directory
    stl_files = glob.glob("*.stl")
    
    if not stl_files:
        print("No STL files found in the current directory!")
        return None
        
    if len(stl_files) == 1:
        print(f"Found 1 STL file: {stl_files[0]}")
        return stl_files[0]
        
    # 3. If multiple files, ask user to choose
    print("Multiple STL files found:")
    for i, f in enumerate(stl_files):
        print(f"{i+1}: {f}")
    
    while True:
        try:
            selection = int(input("Enter the number of the file to use: "))
            if 1 <= selection <= len(stl_files):
                return stl_files[selection-1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

def get_unit():
    """Prompt user to select the unit of measurement."""
    units = ["in", "ft", "yd", "mm", "cm", "m"]
    
    print("\nSelect the unit of measurement:")
    for i, unit in enumerate(units):
        print(f"{i+1}: {UNIT_NAMES[unit]} ({unit})")
    
    while True:
        try:
            selection = int(input("Enter the number (1-6): "))
            if 1 <= selection <= len(units):
                selected_unit = units[selection-1]
                print(f"Selected: {UNIT_NAMES[selected_unit]}\n")
                return selected_unit
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

def main():
    filename = get_stl_filename()
    if not filename:
        return
    
    unit = get_unit()
    unit_name = UNIT_NAMES[unit]

    print(f"Loading {filename}...")
    try:
        mesh = trimesh.load(filename)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # If the file contains multiple objects, combine them into one mesh
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(mesh.dump())

    # Calculate distributions for all 3 axes
    data = {}
    axes_config = {
        'X': [1, 0, 0],
        'Y': [0, 1, 0],
        'Z': [0, 0, 1]
    }

    for axis_name, direction in axes_config.items():
        locs, areas = get_area_distribution(mesh, direction, NUM_SLICES)
        data[axis_name] = (locs, areas)

    # Plotting Setup
    print("Generating interactive graph...")
    
    # Remove .stl extension for display
    display_name = filename.removesuffix('.stl')
    
    # Create figure with buttons
    fig = go.Figure()
    
    # Add traces for all three axes (only one visible at a time)
    for axis_name, (locs, areas) in data.items():
        fig.add_trace(go.Scatter(
            x=locs,
            y=areas,
            mode='lines',
            name=f'{axis_name} Axis',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.3)',
            visible=(axis_name == 'X'),  # Only X visible initially
            hovertemplate=f'Position: %{{x:.2f}} {unit_name}<br>Area: %{{y:.2f}} {unit_name}²<extra></extra>'
        ))
    
    # Create buttons for axis selection
    buttons = []
    for i, axis_name in enumerate(['X', 'Y', 'Z']):
        visible = [False, False, False]
        visible[i] = True
        buttons.append(dict(
            label=f'{axis_name} Axis',
            method='update',
            args=[
                {'visible': visible},
                {
                    'title': f'Cross-Sectional Area Distribution - {display_name} ({axis_name} Axis)',
                    'xaxis.title': f'Position along {axis_name} Axis ({unit_name})'
                }
            ]
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Cross-Sectional Area Distribution - {display_name} (X Axis)',
            font=dict(size=18)
        ),
        xaxis=dict(
            title=f'Position along X Axis ({unit_name})',
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=False,
            zeroline=True
        ),
        yaxis=dict(
            title=f'Area ({unit_name}²)',
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=False,
            zeroline=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.5,
                xanchor="center",
                y=-0.15,
                yanchor="top"
            )
        ],
        margin=dict(l=60, r=40, t=80, b=100)
    )
    
    fig.show()

if __name__ == "__main__":
    main()