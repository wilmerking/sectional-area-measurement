import streamlit as st
import trimesh
import numpy as np
import plotly.graph_objects as go
import tempfile
import os
from area_calculator import get_area_distribution

# Unit name mapping
UNIT_NAMES = {
    "in": "inches",
    "ft": "feet",
    "yd": "yards",
    "mm": "millimeters",
    "cm": "centimeters",
    "m": "meters"
}

st.set_page_config(page_title="Sectional Area Calculator", layout="wide")

st.title("Sectional Area Calculator")
st.markdown("""
Upload an STL file to calculate and visualize its cross-sectional area distribution along the X, Y, and Z axes.
""")

uploaded_file = st.file_uploader("Choose an STL file", type=['stl'])

if uploaded_file is not None:
    # Save uploaded file to a temporary file because trimesh needs a file path or file object
    # For robust loading with trimesh (which sometimes needs a path for file type detection), 
    # we'll save it to a temp file.
    suffix = '.stl'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        with st.spinner(f"Loading {uploaded_file.name}..."):
            mesh = trimesh.load(tmp_file_path)
        
        # If the file contains multiple objects, combine them into one mesh
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump())

        st.success(f"Successfully loaded {uploaded_file.name}")
        
        # Configuration
        st.subheader("Configuration")

        col1, col2 = st.columns([1, 3])
        
        with col1:
            source_unit = st.selectbox(
                "Select original model units:",
                ("in", "ft", "yd", "mm", "cm", "m"),
                index=0, # Defaults to 'in' as it's most common for 3D files
                help="3D files (like STLs) are unitless. Please select the unit used when this file was originally exported."
            )

            unit_name = UNIT_NAMES[source_unit]
            st.write(f"Processing model in **{unit_name}**...")
        
        # Slicing Configuration
        col3, col4 = st.columns([1, 3])
        
        with col3:
            num_slices = st.slider("Number of Slices", min_value=10, max_value=500, value=100, step=10,
                                   help="More slices = smoother graph but slower processing")
        
        if st.button("Calculate Area Distribution"):
            
            # Create tabs for X, Y, Z
            tab_x, tab_y, tab_z = st.tabs(["X Axis", "Y Axis", "Z Axis"])
            
            axes_config = {
                'X': ([1, 0, 0], tab_x),
                'Y': ([0, 1, 0], tab_y),
                'Z': ([0, 0, 1], tab_z)
            }
            
            progress_bar = st.progress(0)
            
            for i, (axis_name, (direction, tab)) in enumerate(axes_config.items()):
                with st.spinner(f"Analyzing {axis_name} axis..."):
                    locs, areas = get_area_distribution(mesh, direction, num_slices)
                    
                    with tab:
                        # Remove .stl extension for display
                        display_name = uploaded_file.name.removesuffix('.stl')
                        
                        # Create plotly figure
                        fig = go.Figure()
                        
                        # Add filled area trace
                        fig.add_trace(go.Scatter(
                            x=locs,
                            y=areas,
                            mode='lines+markers',
                            name='Area',
                            line=dict(color='#1f77b4', width=2),
                            marker=dict(
                                size=6,
                                color='#1f77b4',
                                opacity=0  # Hidden by default, will show on hover
                            ),
                            fill='tozeroy',
                            fillcolor='rgba(31, 119, 180, 0.3)',
                            hovertemplate='Position: %{x:.2f} ' + unit_name + '<br>Area: %{y:.2f} ' + unit_name + '²<extra></extra>'
                        ))
                        
                        # Update layout for dark theme with no box
                        fig.update_layout(
                            title=dict(
                                text=f'Cross-Sectional Area Distribution - {display_name} ({axis_name} Axis)',
                                font=dict(size=16)
                            ),
                            xaxis=dict(
                                title=f'Position along {axis_name} Axis ({unit_name})',
                                showgrid=True,
                                gridcolor='rgba(128, 128, 128, 0.2)',
                                showline=False,
                                zeroline=True,
                                showspikes=True,
                                spikemode='across',
                                spikesnap='cursor',
                                spikecolor='rgba(128, 128, 128, 0.5)',
                                spikethickness=1,
                                spikedash='solid'
                            ),
                            yaxis=dict(
                                title=f'Area ({unit_name}²)',
                                showgrid=True,
                                gridcolor='rgba(128, 128, 128, 0.2)',
                                showline=False,
                                zeroline=True
                            ),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            hovermode='closest',
                            margin=dict(l=60, r=40, t=60, b=60)
                        )
                        
                        # Display the interactive plot
                        st.plotly_chart(fig, use_container_width=True)
                
                progress_bar.progress((i + 1) / 3)
                
    except Exception as e:
        st.error(f"Error processing file: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
