import bpy

class VIEW3D_PT_ModifierToolsPanel(bpy.types.Panel):
    bl_label = "MODIFIER"
    bl_idname = "PT_ModifierToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Công cụ Modifier")

classes = (
    VIEW3D_PT_ModifierToolsPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
