bl_info = {
    "name": "Box Design Addon",
    "author": "Your Name, Lai Ngua Tay",
    "version": (1, 6),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Box Design",
    "description": "An addon for box design with unit settings, volume scaling, bounding box creation, volume calculation, TH tools including circle, capsule, and flared section creation, modifier tools for array, curve, and solidify, 3D model export, and community links",
    "category": "3D View",
}

import bpy
import importlib

from . import boxdesign_tools
from . import boxdesign_scale_to_volume
from . import boxdesign_lam_phang
from . import boxdesign_bounding_box
from . import boxdesign_calculateVolume
from . import th_tools
from . import thdesign_circle_creator
from . import shared_props
from . import area_utils
from . import thdesign_capsule_from_area
from . import thdesign_capsule_from_diameter
from . import modifier_tools
from . import modifier_array_curve_mod
from . import modifier_solidify
from . import export
from . import export_3D_model
from . import export_svg_from_mesh
from . import settings
from . import community

# Reload modules for development
importlib.reload(boxdesign_tools)
importlib.reload(boxdesign_scale_to_volume)
importlib.reload(boxdesign_lam_phang)
importlib.reload(boxdesign_bounding_box)
importlib.reload(boxdesign_calculateVolume)
importlib.reload(th_tools)
importlib.reload(thdesign_circle_creator)
importlib.reload(shared_props)
importlib.reload(area_utils)
importlib.reload(thdesign_capsule_from_area)
importlib.reload(thdesign_capsule_from_diameter)
importlib.reload(modifier_tools)
importlib.reload(modifier_array_curve_mod)
importlib.reload(modifier_solidify)
importlib.reload(export)
importlib.reload(export_3D_model)
importlib.reload(export_svg_from_mesh)
importlib.reload(settings)
importlib.reload(community)

modules = (
    boxdesign_tools,
    boxdesign_scale_to_volume,
    boxdesign_lam_phang,
    boxdesign_bounding_box,
    boxdesign_calculateVolume,
    th_tools,
    thdesign_circle_creator,
    shared_props,
    area_utils,
    thdesign_capsule_from_area,
    thdesign_capsule_from_diameter,
    modifier_tools,
    modifier_array_curve_mod,
    modifier_solidify,
    export,
    export_3D_model,
    export_svg_from_mesh,
    settings,
    community,
)

def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()

def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()

if __name__ == "__main__":
    register()
