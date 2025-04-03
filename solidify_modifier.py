import bpy

def update_solidify_thickness(self, context):
    obj = context.object
    if obj and obj.type == 'MESH':
        solidify_mod = obj.modifiers.get("Solidify")
        if solidify_mod:
            solidify_mod.thickness = context.scene.solidify_thickness

def update_solidify_offset(self, context):
    obj = context.object
    if obj and obj.type == 'MESH':
        solidify_mod = obj.modifiers.get("Solidify")
        if solidify_mod:
            solidify_mod.offset = context.scene.solidify_offset

class OBJECT_OT_add_solidify_modifier(bpy.types.Operator):
    bl_idname = "object.add_solidify_modifier"
    bl_label = "Add Solidify Modifier"

    def execute(self, context):
        objs = bpy.context.selected_objects
        for obj in objs:
            if obj.type == 'MESH':
                solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
                solidify_mod.thickness = context.scene.solidify_thickness
                solidify_mod.offset = context.scene.solidify_offset
                solidify_mod.use_even_offset = True
        return {'FINISHED'}

class SolidifyPanel(bpy.types.Panel):
    bl_label = "Solidify"
    bl_idname = "PT_SolidifyPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "solidify_thickness", text="Thickness")
        layout.prop(context.scene, "solidify_offset", text="Offset")
        layout.operator("object.add_solidify_modifier", text="Add Solidify Modifier")

def register():
    bpy.utils.register_class(OBJECT_OT_add_solidify_modifier)
    bpy.utils.register_class(SolidifyPanel)

    bpy.types.Scene.solidify_thickness = bpy.props.FloatProperty(name="Thickness", default=6.0, update=update_solidify_thickness)
    bpy.types.Scene.solidify_offset = bpy.props.FloatProperty(name="Offset", default=1.0, update=update_solidify_offset)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_solidify_modifier)
    bpy.utils.unregister_class(SolidifyPanel)

    del bpy.types.Scene.solidify_thickness
    del bpy.types.Scene.solidify_offset

