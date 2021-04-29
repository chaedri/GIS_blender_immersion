
import sys
import os
import bpy
import json
import math

################# SETTINGS from JSON ###################
config_file = 'C:\Path\To\GIS_blender_immersion\config.json'

with open(config_file, 'r') as f:
    configuration = json.load(f)
    demFile = os.path.join(configuration['watch_folder'], configuration['dem_name'])
    waterFile = os.path.join(configuration['watch_folder'], configuration['water_name'])
    buildingFile = os.path.join(configuration['watch_folder'], configuration['building_name'])
    viewFile = os.path.join(configuration['watch_folder'], configuration['view_name'])
    CRS = configuration['CRS']
    treeFile = os.path.join(configuration['watch_folder'], configuration['tree_name'])
    Flood = configuration['flood_level']

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

def create_material(name):
    # Create new material
    mat = bpy.data.materials.get(name)
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=name)
    return mat

def elevation_color_ramp(color_ramp):
    # Removing the First Element this is not necessary but done to show how to remove color stops
    color_ramp.elements.remove(color_ramp.elements[0])

    # Adding new color stop at location 0.100
    color_ramp.elements.new(0.06)

    # Setting the color for the stop that we recently created
    color_ramp.elements[0].color = (0.046,0.16,0.052,1)

    #creating the second stop the same way
    color_ramp.elements.new(0.66)
    color_ramp.elements[1].color = (0.608,0.507,0.169,1)

    # Assigning position and color to already present stop
    color_ramp.elements[2].position = (0.999)
    color_ramp.elements[2].color = (0.71,0.68,0.38,1)
    
    return color_ramp
    
def texture_terrain(terrain, z_color=False):
    # Create new material
    ter = create_material("terrain_texture")
    
    # Configure Nodes: use nodes
    ter.use_nodes = True
    nodes = ter.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    
    # Ortho photo or Z-Color option
    if z_color==True:
        #color terrain by z elevation
        coords = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.vector_type = 'TEXTURE'
        mapping.inputs['Location'].default_value = (0, 0, -1.5)
        mapping.inputs['Scale'].default_value = (10, 0, 0)
        mapping.inputs['Rotation'].default_value = (0, -math.pi/2, 0)
        grad = nodes.new("ShaderNodeTexGradient")
        ZtoRGB = nodes.new("ShaderNodeValToRGB")
        elevation_color_ramp(ZtoRGB.color_ramp)
        emission = nodes.new("ShaderNodeEmission")
        output = nodes.new("ShaderNodeOutputMaterial") 
        
        ter.node_tree.links.new(mapping.inputs['Vector'], coords.outputs['Object'])
        ter.node_tree.links.new(grad.inputs['Vector'], mapping.outputs['Vector'])
        ter.node_tree.links.new(ZtoRGB.inputs['Fac'], grad.outputs['Color'])
        ter.node_tree.links.new(emission.inputs['Color'], ZtoRGB.outputs['Color'])
        ter.node_tree.links.new(output.inputs['Surface'], emission.outputs['Emission'])
        
    elif z_color==False:
        # Create shading node
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        # Create image node
        texImage = nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load("C:\\TL_coupling\\Watch\\ortho.png")
        # Create output material node
        output=nodes.new("ShaderNodeOutputMaterial")
        
        # Link image to Shading node color
        ter.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
        # Link shading node to surface of output material
        ter.node_tree.links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])

    assign_texture(terrain.data.materials, ter)
    return terrain

def texture_water(water):
    # Create material
    wat = create_material("water_texture")

    # Configure Nodes: use nodes
    wat.use_nodes=True
    nodes = wat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    # Add wave Texture
    waves = wat.node_tree.nodes.new("ShaderNodeTexWave")
    waves.bands_direction = 'Y'
    waves.inputs[1].default_value = 30 #scale
    waves.inputs[2].default_value = 10.0 #distortion

    # Add wave coloring
    wave_color = wat.node_tree.nodes.new("ShaderNodeBsdfGlass")
    wave_color.inputs[0].default_value = (0.28, 0.86, 0.91, 1)#RGBA Color
    wave_color.inputs[1].default_value = 0.24
     
    # Output Material
    output=wat.node_tree.nodes.new("ShaderNodeOutputMaterial")

    # Links
    wat.node_tree.links.new(output.inputs['Surface'], wave_color.outputs['BSDF'])
    wat.node_tree.links.new(output.inputs['Displacement'], waves.outputs['Color'])
    
    # Assign Material to Water object
    assign_texture(water.data.materials, wat)
    return water

######################## Main ############################
# terrain
bpy.ops.importgis.georaster(filepath=demFile, importMode="DEM", subdivision="mesh", rastCRS=CRS)
terrain = bpy.context.active_object
bpy.ops.transform.translate(value=(0, 0, Flood))
terrain = texture_terrain(terrain, z_color=False)

## water
bpy.ops.importgis.georaster(filepath=waterFile, subdivision="mesh", rastCRS=CRS)
water = bpy.context.active_object
water = texture_water(water)

# buildings
bpy.ops.importgis.shapefile(filepath=buildingFile,elevSource="FIELD",fieldElevName="elevation",fieldExtrudeName="height",fieldObjName='cat',separateObjects=False,shpCRS=CRS)
 
# viewpoint
bpy.ops.importgis.shapefile(filepath=viewFile, elevSource ='OBJ', objElevName='elev', shpCRS=CRS)
view = bpy.context.active_object

# import tree file, translate and rotate/scale
loc = view.location

# import
bpy.ops.import_scene.obj(filepath=treeFile)
tree = bpy.context.selected_objects[0]
# change name
tree.name = "tree"
# move to view point
bpy.ops.transform.translate(value=loc)
# rotate to vertical
bpy.ops.transform.rotate(value=math.pi/2, orient_axis='X', orient_type='LOCAL')
# scale to normal tree heigh
dims = bpy.data.objects['tree'].dimensions
new_height = 18
scale = float(new_height)/dims[2]
bpy.ops.transform.resize(value=(scale, scale, scale))
