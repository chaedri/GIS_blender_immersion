# GIS_blender_immersion
A add-on for blender that allows real-time 3D immersion in landscapes produced by GRASS GIS and Tangible Landscape.

## Installation
Install [Blender]() 2.8 or later and the [BlenderGIS addon]() .

Download and unzip this repository.

Create a folder in the base directory of your computer called `TL_coupling`. Move the `Watch` folder from the downloaded repository to the `TL_coupling` folder. The path to the `Watch` folder should now be `C:\TL_coupling\Watch\`**. This is the shared folder that GRASS GIS will write it's output to and Blender will watch for data to render. 

**If the watch folder path does not match `C:\TL_coupling\Watch\`, change the path in the config.json file to the correct.

Open a blank template in Blender 2.8 or later and delete the default cube. Switch to the Scripting layout. Open main.py in the scripting window. 

In the upper right hand corner of the rendering window, toggle the viewport shading to `Material Preview`.

At the beginning of main.py, change the config_file variable to the path to repository. Press the `play` button. A scene from NC Bald Head Island will render. 

