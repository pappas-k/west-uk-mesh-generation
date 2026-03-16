# West UK Ambient Mesh

Unstructured mesh generation for the West UK / Severn Estuary region, intended for tidal hydrodynamic simulations. Built with [qmesh](https://qmesh.org) and [gmsh](https://gmsh.info).

## Overview

The mesh covers the Irish Sea and Severn Estuary (lon: −14° to −2°, lat: 47° to 60°, EPSG:32630). Resolution is spatially graded — coarse offshore and progressively finer near coastlines, estuaries, islands, and instrument locations. The same framework supports extended configurations including tidal range structures (lagoons).

## Repository Structure

```
mesh_generation.py       # Main mesh generation script
how_to_lagoon_mesh.docx  # Guide for adding a tidal lagoon to the domain
shapefiles/
  whole_domain_ambient.shp   # Domain outline with open boundary PhysIDs
  gradation/                 # Resolution shapefiles
    grad_irish_sea.shp       # Irish Sea — coarse background
    grad_estuaries.shp       # Estuary regions — medium resolution
    grad_gauges.shp          # Tide gauge locations — fine resolution
    grad_detectors_TRS.shp   # Tidal range scheme detector locations
    grad_isl.shp             # Islands — fine resolution
    grad_isl_2.shp           # Secondary island features
    grad_med.shp             # Severn / North Wales coast — medium resolution
    grad_large.shp           # Remaining UK coastline — coarse resolution
    grad_extra.shp           # Narrow channels and estuaries — extra fine
```

## Mesh Resolution

All gradations scale from a base value of `h_l = 15000 m`:

| Shapefile             | Min resolution      | Region                          |
|-----------------------|---------------------|---------------------------------|
| `grad_irish_sea`      | ~750 m              | Open Irish Sea                  |
| `grad_estuaries`      | ~375 m              | Estuary entrances               |
| `grad_gauges`         | ~150 m              | Tide gauge sites                |
| `grad_detectors_TRS`  | ~150 m              | Tidal range scheme detectors    |
| `grad_isl`            | ~1200 m             | Islands                         |
| `grad_isl_2`          | ~150 m              | Detailed island features        |
| `grad_med`            | ~4500 m             | Severn / North Wales coast      |
| `grad_large`          | ~7500 m             | Background UK coastline         |
| `grad_extra`          | ~600 m              | Narrow channels                 |

## Running

The recommended way to run the script is via `qmeshcontainer`, which provides a pre-configured environment with all dependencies (QGIS, gmsh, qmesh).

**1. Install qmeshcontainers:**
```bash
sudo pip install qmeshcontainers
```

**2. In the project directory  launch the container:**
```bash
qmeshcontainer -mwd
```

**3. Inside the container, run the script:**
```bash
cd mesh
python mesh_generation.py
```

This produces:
- `west_uk_mesh.geo` — gmsh geometry file
- `west_uk_mesh.fld` — mesh metric field
- `west_uk_mesh.msh` — the mesh
- `west_uk_mesh.shp` — shapefile for visualisation in QGIS
- `meshMetric-whole.nc` — combined resolution raster (NetCDF4)

## Lagoon Configuration

To extend the domain with a tidal lagoon (tidal range structure), follow the workflow in `how_to_lagoon_mesh.docx`. In brief:

1. Add the lagoon outline to the domain shapefile and assign PhysIDs to turbine and sluice gate boundaries (inner/outer faces).
2. Add a high-resolution gradation shapefile for the lagoon wall (`grad_internal_lagoon.shp`).
3. Update `resolution_shapefiles` and `gradation_params` in the script accordingly.

## Dependencies

| Package          | Purpose                        |
|------------------|--------------------------------|
| qmesh / qmesh3   | Mesh generation framework      |
| gmsh             | Unstructured mesh generation   |
| QGIS / PyQGIS    | Geospatial vector/raster I/O   |
| netCDF4          | Resolution raster export       |
