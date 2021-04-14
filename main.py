
import sys
import os
import bpy

################# SETTINGS (for JSON config file) ###################
watchFolder = 'C:\\TL_coupling\\Watch\\'
demFile = os.path.join(watchFolder, 'elev.tif')
waterFile = os.path.join(watchFolder, 'water.tif')
buildingFile = os.path.join(watchFolder, 'buildings.shp')
CRS = 'EPSG:32119'


################## Functions ###################


def assign_texture(objMaterials, texture):
        # Assign it to object
    if objMaterials:
        # assign to 1st material slot
        objMaterials[0] = texture
    else:
        # no slots
        objMaterials.append(texture)
    return objMaterials


def texture_terrain(terrain, z_color=FALSE):
    # Create new material
    ter = bpy.data.materials.get("terrain_texture")
    if ter is None:
        # create material
        ter = bpy.data.materials.new(name="terrain_texture")
    
    # Configure Nodes: use nodes
    ter.use_nodes = True
    
    # Ortho photo or Z-Color option
    if z_color=TRUE:
        #color terrain by z elevation
    else:
        # Create shading node
        bsdf = ter.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        # Create image node
        texImage = ter.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load("C:\\TL_coupling\\Watch\\ortho.png")
        # Create output material node
        output=ter.node_tree.nodes.new("ShaderNodeOutputMaterial")
        
        # Link image to Shading node color
        ter.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
        # Link shading node to surface of output material
        ter.node_tree.links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])

    assign_texture(terrain.data.materials, ter)
    return terrain

def texture_water(water):
    # Create material
    mat = bpy.data.materials.get("Water_texture")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Water_texture")
    
    # Configure Nodes: use nodes
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
    
    # Assign Material to Water object
    assign_texture(water.data.materials, mat)
    return water

######################## Main ############################
# terrain
bpy.ops.importgis.georaster(filepath=demFile, importMode="DEM", subdivision="mesh", rastCRS=CRS)
terrain = bpy.context.active_object
terrain = texture_terrain(terrain, z_col=FALSE)

## water
bpy.ops.importgis.georaster(filepath=waterFile, subdivision="mesh", rastCRS=CRS)
water = bpy.context.active_object
water = texture_water(water)

# buildings
bpy.ops.importgis.shapefile(filepath=buildingFile,fieldElevName="elevation",fieldExtrudeName="height",fieldObjName='cat',separateObjects=True,shpCRS=CRS)



#    
## viewpoint
#viewFile = os.path.join(watchFolder, 'view.shp')
#view = bpy.ops.importgis.shapefile(filepath=viewFile, elevSource ='terrain', shpCRS=CRS)
