"""
Mesh generation example for the severn estuary;

To be adapted for other examples

the folder shapefiles containes all the necessary files from qGIS to describe the geometry we wish to model
the function generate_mesh calls qmesh; we feed into the necessary inputs based on the mesh characteristics
as described below

"""

import qmesh
import os


def generate_mesh(name,
                  outline,
                  resolution_shapefiles,
                  gradation_params,
                  raster_boundaries=(-5.2, 1.73, 48.4, 51.2),
                  raster_resolution=(300,300),
                  raster_file=None,
                  coordinate_system='EPSG:32630',):
    """
    Mesh generation

    :param outline: Shapefile for outline file destination.
    :param resolution_arrays: Shapefiles that specify resolution characteristics
    :param raster_boundaries: Boundaries for raster generated that is used to specify resolution - this is based on the
                              input file projection
    :param raster_resolution: Resolution of raster, the larger the value, the greater the computational time
                              units are pixels
    :param raster_file: Specify a raster_file rather than generate from scratch
    :return:
    """

    # Initialising qgis API
    qmesh.initialise()

    # Reading outline, and converting to polylines and polygon shapes to communicate with qGIS
    boundaries = qmesh.vector.Shapes()
    boundaries.fromFile(outline)
    loopShapes = qmesh.vector.identifyLoops(boundaries,isGlobal=False, defaultPhysID=1000, fixOpenLoops=True)
    polygonShapes = qmesh.vector.identifyPolygons(loopShapes, smallestNotMeshedArea=300, meshedAreaPhysID=1)



    # Create raster for mesh gradation for increased resolution around regions of interest highlighted by shapefiles
    # Iteratively create these rasters and store the associated qmesh objects in a list
    gradation = []
    if raster_file is None:
        for i in range(len(resolution_shapefiles)):
            print(raster_boundaries[i],raster_resolution,gradation_params[i])
            boundary_shapefiles = qmesh.vector.Shapes()
            boundary_shapefiles.fromFile(resolution_shapefiles[i])
            gradation.append(qmesh.raster.meshMetricTools.gradationToShapes())
            gradation[-1].setShapes(boundary_shapefiles)
            gradation[-1].setRasterBounds(*raster_boundaries[i])
            gradation[-1].setRasterResolution(*raster_resolution)
            gradation[-1].setGradationParameters(*gradation_params[i])
            gradation[-1].calculateLinearGradation()
            # gradation[-1].writeNetCDF('grad_'+str(i)+'.nc') # Output netCDF4 format raster

        if len(gradation) == 1:
            # If we only have one shapefile that defines the resolution, then use only that one to define our raster
            meshMetricRaster = gradation[0]
        else:
            # Mix all the information from multiple shapefiles to create a single raster that encompasses all
            # information
            meshMetricRaster = qmesh.raster.meshMetricTools.minimumRaster(gradation) #grad_0

        # Export raster that defines the resolution; this can be used directly later instead of being regenerated
        meshMetricRaster.writeNetCDF('../outputs/meshMetric-whole.nc')

    else:
        # Read in existing mesh gradation raster
        meshMetricRaster =qmesh.raster.meshMetricTools.gradationToShapes()
        meshMetricRaster.fromFile(raster_file)

    # Create domain object and write gmsh files.
    domain = qmesh.mesh.Domain()

    # Set geometry polylines and polygons
    domain.setGeometry(loopShapes, polygonShapes)

    # Specify gradation metric gor gmsh
    domain.setMeshMetricField(meshMetricRaster)

    # Spefify coordinate system
    domain.setTargetCoordRefSystem(coordinate_system, fldFillValue=1000.0)

    # Call gmsh
    domain.gmsh(geoFilename= name + '.geo', \
                fldFilename= name + '.fld', \
                mshFilename= name + '.msh', \
                )


def convertMesh(name):
    """
    Generates a shapefile based on the mesh. Useful for visualisation in QGIS
    :param name: Name of mesh file that needs to be converted to *.shp
    :return:
    """
    mesh = qmesh.mesh.Mesh()
    mesh.readGmsh( name + '.msh', 'EPSG:32630')
    mesh.writeShapefile(name)


if __name__ == '__main__':
    """
    In this example we have put together the files for the Severn Estuary, and we call on these to the function
    """

    print(os.getcwd())
    # Change working directory to folder that contains
    os.chdir("shapefiles/")
    

    # Name of mesh files (output path included)
    name = "../outputs/west_uk_mesh"

    # Specify model outline
    outline = "whole_domain_ambient.shp"

    # Shapefiles that indicate resolution
    resolution_shapefiles = ['gradation/grad_irish_sea.shp',
                             'gradation/grad_estuaries.shp',
                             'gradation/grad_gauges.shp',
                             'gradation/grad_detectors_TRS.shp',
                             'gradation/grad_isl.shp',
                             'gradation/grad_isl_2.shp',
                             'gradation/grad_med.shp',
                             'gradation/grad_large.shp',
                             'gradation/grad_extra.shp']

    h_l =15000
    #f=2
    # Specifying the mesh resolution parameters we seek for each of the above shapefiles
     
     #THIS WAS FOR THE FINER
     #gradation_params = [(0.04  * h_l, h_l, 3.0, 0.005),  # for grad_irish_sea 
     #                   (0.02  * h_l, h_l, 3.0, 0.001),   # for grad_estuaries
     #                   (0.01  * h_l, h_l, 0.3, 0.002),   # for grad_gauges
     #                   (0.01  * h_l, h_l, 0.3, 0.002),   # for grad_detectors_TRS
     #                   (0.02  * h_l, h_l, 0.2, 0.0005),  # for grad_isl
     #                   (0.01  * h_l, h_l, 0.3, 0.0005),  # for grad_isl_2
     #                   (0.15  * h_l, h_l, 0.5),          # for grad_med
     #                   (0.25  * h_l, h_l, 0.5),          # for grad_large
     #                   (0.04  * h_l, h_l, 0.5, 0.001)]   # for grad_extra
     
         
    gradation_params = [(0.05  * h_l, h_l, 1.5,  2*0.002),   # for grad_irish_sea 
                        (0.025  * h_l, h_l, 1.5, 2*0.002),   # for grad_estuaries
                        (0.01  * h_l, h_l, 0.6, 0.002),       # for grad_gauges
                        (0.01  * h_l, h_l, 0.3, 0.002),       # for grad_detectors_TRS
                        (2*0.04  * h_l, h_l, 0.7),              # for grad_isl
                        (0.01  * h_l, h_l, 0.3, 0.0005),      # for grad_isl_2
                        (2*0.15* h_l, h_l, 0.5),              # for grad_med
                        (2*0.25* h_l, h_l, 0.5),              # for grad_large
                        (0.04  * h_l, h_l, 0.5, 0.001)]       # for grad_extra

    # Raster boundary coordinates - can be consistent for all rasters, maximum will be used when these need to
    # be collated for a single mesh metric
    raster_boundaries = [(-14.0, -2.0, 47.0, 60.0), # for grad_irish_sea
                         (-14.0, -2.0, 47.0, 60.0), # for grad_estuaries
                         (-14.0, -2.0, 47.0, 60.0), # for grad_gauges
                         (-14.0, -2.0, 47.0, 60.0), # for grad_detectors_TRS
                         (-14.0, -2.0, 47.0, 60.0), # for grad_isl
                         (-14.0, -2.0, 47.0, 60.0), # for grad_isl_2
                         (-14.0, -2.0, 47.0, 60.0), # for grad_med
                         (-14.0, -2.0, 47.0, 60.0), # for grad_large
                         (-14.0, -2.0, 47.0, 60.0)] # for grad_extra


    
    # Call mesh generation function.
    generate_mesh(name,
                  outline,
                  resolution_shapefiles,
                  gradation_params,
                  raster_boundaries,
                  raster_resolution=(1500, 1500),
                  coordinate_system='EPSG:32630')

    # Convert the gmsh *.msh file to a *.shp file for visualisation in qGIS
    convertMesh(name)
