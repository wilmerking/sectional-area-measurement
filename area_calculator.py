import trimesh
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
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
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    plt.subplots_adjust(bottom=0.2) # Make room for buttons

    # Initial Plot (X Axis)
    current_axis = 'X'
    line, = ax.plot(data['X'][0], data['X'][1], linestyle='-', color='#1f77b4')
    fill = ax.fill_between(data['X'][0], data['X'][1], alpha=0.3, color='#1f77b4')
    
    # Remove .stl extension for display
    display_name = filename.removesuffix('.stl')
    
    ax.set_title(f'Cross-Sectional Area Distribution - {display_name} ({current_axis} Axis)')
    ax.set_xlabel(f'Position along {current_axis} Axis ({unit_name})')
    ax.set_ylabel(f'Area ({unit_name}²)')
    ax.grid(True, alpha=0.3)
    
    # Remove all spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Callback function to update plot
    def update_plot(axis_name):
        nonlocal fill
        # Update data
        x, y = data[axis_name]
        line.set_data(x, y)
        
        # Remove old fill and create new one
        fill.remove()
        fill = ax.fill_between(x, y, alpha=0.3, color='#1f77b4')
        
        # Rescale axes
        ax.relim()
        ax.autoscale_view()
        
        # Update labels
        ax.set_title(f'Cross-Sectional Area Distribution - {display_name} ({axis_name} Axis)')
        ax.set_xlabel(f'Position along {axis_name} Axis ({unit_name})')
        fig.canvas.draw_idle()

    # Create Buttons
    # Define button positions [left, bottom, width, height]
    ax_x = plt.axes([0.3, 0.05, 0.1, 0.075])
    ax_y = plt.axes([0.45, 0.05, 0.1, 0.075])
    ax_z = plt.axes([0.6, 0.05, 0.1, 0.075])

    btn_x = Button(ax_x, 'X Axis')
    btn_y = Button(ax_y, 'Y Axis')
    btn_z = Button(ax_z, 'Z Axis')

    # Connect buttons to callback
    btn_x.on_clicked(lambda event: update_plot('X'))
    btn_y.on_clicked(lambda event: update_plot('Y'))
    btn_z.on_clicked(lambda event: update_plot('Z'))

    plt.show()

if __name__ == "__main__":
    main()