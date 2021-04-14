import bpy

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
        geometry = nodes.new("ShaderNodeNewGeometry")
        sepxyz = nodes.new("ShaderNodeSeparateXYZ")
        ZtoRGB = nodes.new("ShaderNodeValToRGB")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial") 
        
        ter.node_tree.links.new(sepxyz.inputs['Vector'], geometry.outputs['Position'])
        ter.node_tree.links.new(ZtoRGB.inputs['Fac'], sepxyz.outputs['Z'])
        ter.node_tree.links.new(bsdf.inputs['Base Color'], ZtoRGB.outputs['Color'])
        ter.node_tree.links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])
        
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