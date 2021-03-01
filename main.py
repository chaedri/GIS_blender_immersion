
import sys
import os
import bpy

# watch folder
# hard coded for now
watchFolder = 'C:\\TL_coupling\\Watch\\'

# surface
demFile = os.path.join(watchFolder, 'elev.tif')
CRS = 'EPSG:32119'
terrain = bpy.ops.importgis.georaster(filepath=demFile, importMode="DEM", subdivision="mesh", rastCRS=CRS)

# viewpoint
viewFile = os.path.join(watchFolder, 'view.shp')
view = bpy.ops.importgis.shapefile(filepath=viewFile, elevSource ='terrain', shpCRS=CRS)

# shrink other raster to surface

# texture

# water
waterFile = os.path.join(watchFolder, 'water.tif')
water = bpy.ops.importgis.georaster(filepath=waterFile, rastCRS=CRS)

bpy.data.materials['rastMat']

# buildings
