import bpy

class OBJECT_OT_change_units(bpy.types.Operator):
    bl_idname = "scene.change_units"
    bl_label = "Change Units"

    def execute(self, context):
        scene = context.scene
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 0.001
        scene.unit_settings.length_unit = 'MILLIMETERS'
        bpy.context.space_data.overlay.grid_scale = 0.001
        bpy.context.space_data.clip_start = 1
        bpy.context.space_data.clip_end = 100000
        return {'FINISHED'}

class SettingsPanel(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "PT_SettingsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.change_units", text="Units")

def register():
    bpy.utils.register_class(OBJECT_OT_change_units)
    bpy.utils.register_class(SettingsPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_change_units)
    bpy.utils.unregister_class(SettingsPanel)

