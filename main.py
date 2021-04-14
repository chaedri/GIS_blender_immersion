
import sys
import os
import bpy

# watch folder
# hard coded for now
watchFolder = 'C:\\TL_coupling\\Watch\\'

# surface
demFile = os.path.join(watchFolder, 'elev.tif')
CRS = 'EPSG:32119'

bpy.ops.importgis.georaster(filepath=demFile, importMode="DEM", subdivision="mesh", rastCRS=CRS)

terrain = bpy.context.active_object

# Get material
ter = bpy.data.materials.get("terrain_texture")
if ter is None:
    # create material
    ter = bpy.data.materials.new(name="terrain_texture")

ter.use_nodes = True

bsdf = ter.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
texImage = ter.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load("C:\\TL_coupling\\Watch\\ortho.png")
ter.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
output=ter.node_tree.nodes.new("ShaderNodeOutputMaterial")
ter.node_tree.links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])

# Assign it to object
if terrain.data.materials:
    # assign to 1st material slot
    terrain.data.materials[0] = ter
else:
    # no slots
    terrain.data.materials.append(ter)

#    
## viewpoint
#viewFile = os.path.join(watchFolder, 'view.shp')
#view = bpy.ops.importgis.shapefile(filepath=viewFile, elevSource ='terrain', shpCRS=CRS)

## water
waterFile = os.path.join(watchFolder, 'water.tif')
bpy.ops.importgis.georaster(filepath=waterFile, subdivision="mesh", rastCRS=CRS)
water = bpy.context.active_object

# Get material
mat = bpy.data.materials.get("Water_texture")
if mat is None:
    # create material
    mat = bpy.data.materials.new(name="Water_texture")

mat.use_nodes=True

# Add wave Texture
waves = mat.node_tree.nodes.new("ShaderNodeTexWave")
waves.bands_direction = 'Y'
waves.inputs[1].default_value = 30 #scale
waves.inputs[2].default_value = 10.0 #distortion

# Add wave coloring
wave_color = mat.node_tree.nodes.new("ShaderNodeBsdfGlass")
wave_color.inputs[0].default_value = (0.28, 0.86, 0.91, 1)#RGBA Color
wave_color.inputs[1].default_value = 0.24
 
# Output Material
output=mat.node_tree.nodes.new("ShaderNodeOutputMaterial")

# Links
mat.node_tree.links.new(output.inputs['Surface'], wave_color.outputs['BSDF'])
mat.node_tree.links.new(output.inputs['Displacement'], waves.outputs['Color'])

# Assign it to object
if water.data.materials:
    # assign to 1st material slot
    water.data.materials[0] = mat
else:
    # no slots
    water.data.materials.append(mat)

# buildings
buildingFile = os.path.join(watchFolder, 'buildings.shp')
bpy.ops.importgis.shapefile(filepath=buildingFile,fieldElevName="elevation",fieldExtrudeName="height",fieldObjName='cat',separateObjects=True,shpCRS=CRS)