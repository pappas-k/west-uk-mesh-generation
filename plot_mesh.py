"""
Plot the West UK unstructured mesh.

Reads west_uk_mesh.shp from the shapefiles/ directory and produces a figure
where each mesh edge is coloured by its length (m), revealing the resolution
gradation across the domain.

Outputs
-------
mesh_plot.png  — saved in the current working directory
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — works without a display
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
from matplotlib.collections import LineCollection

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_SHP   = os.path.join(SCRIPT_DIR, "shapefiles", "west_uk_mesh.shp")
OUT_FILE   = os.path.join(SCRIPT_DIR, "mesh_plot.png")

# ---------------------------------------------------------------------------
# Load mesh
# ---------------------------------------------------------------------------
print("Loading mesh shapefile …")
gdf = gpd.read_file(MESH_SHP).to_crs("EPSG:4326")  # reproject to lon/lat

# ---------------------------------------------------------------------------
# Build line segments and compute edge lengths (in metres, using UTM original)
# ---------------------------------------------------------------------------
gdf_utm = gpd.read_file(MESH_SHP)                   # keep UTM for length calc
gdf["length_m"] = gdf_utm.geometry.length

segments = []
lengths  = []
for geom, length in zip(gdf.geometry, gdf["length_m"]):
    coords = np.array(geom.coords)
    segments.append(coords)
    lengths.append(length)

lengths = np.array(lengths)

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
print(f"Plotting {len(segments):,} mesh edges …")

fig, ax = plt.subplots(figsize=(10, 12))

norm  = mcolors.LogNorm(vmin=lengths.min(), vmax=lengths.max())
cmap  = plt.cm.viridis_r

lc = LineCollection(segments, linewidths=0.15, cmap=cmap, norm=norm)
lc.set_array(lengths)
ax.add_collection(lc)

# Axis limits from data extent
xmin, ymin, xmax, ymax = gdf.total_bounds
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# Colorbar
cbar = fig.colorbar(lc, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Edge length (m)", fontsize=11)
cbar.ax.tick_params(labelsize=9)

# Labels
ax.set_xlabel("Longitude (°)", fontsize=11)
ax.set_ylabel("Latitude (°)", fontsize=11)
ax.set_title("West UK Ambient Mesh\n(colour = edge length)", fontsize=13)
ax.tick_params(labelsize=9)

# Stats annotation
textstr = (
    f"Edges : {len(segments):,}\n"
    f"Min   : {lengths.min():.0f} m\n"
    f"Median: {np.median(lengths):.0f} m\n"
    f"Max   : {lengths.max():.0f} m"
)
ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=8,
        verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.7))

plt.tight_layout()
plt.savefig(OUT_FILE, dpi=200, bbox_inches="tight")
print(f"Saved → {OUT_FILE}")
