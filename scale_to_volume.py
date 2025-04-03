import bpy
import bmesh

class OBJECT_OT_scale_to_volume(bpy.types.Operator):
    bl_idname = "object.scale_to_volume"
    bl_label = "Scale to Volume"

    def execute(self, context):
        width = context.scene.width
        height = context.scene.height
        target_volume_liters = context.scene.target_volume
        target_volume = target_volume_liters * 1_000_000  # Chuyển lít sang mm³
        
        objs = bpy.context.selected_objects
        
        for obj in objs:
            if obj.type == 'MESH':
                iterations = 0
                while iterations < 100:
                    initial_volume = self.calculate_volume(obj)
                    scale_x = width / obj.dimensions.x
                    scale_z = height / obj.dimensions.z
                    obj.scale.x *= scale_x
                    obj.scale.z *= scale_z

                    current_volume = self.calculate_volume(obj)
                    
                    if current_volume > 0:
                        scale_y = (target_volume / current_volume) ** (1/3)
                        obj.scale.y *= scale_y
                        bpy.ops.object.transform_apply(scale=True)
                        updated_volume = self.calculate_volume(obj)

                        if abs(updated_volume - target_volume) <= 0.00001:
                            break
                        iterations += 1
                    else:
                        break

                bpy.context.view_layer.update()
        
        return {'FINISHED'}
    
    def calculate_volume(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        volume = bm.calc_volume()
        bm.free()
        return volume

class ScaleVolumePanel(bpy.types.Panel):
    bl_label = "Scale Volume"
    bl_idname = "PT_ScaleVolumePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "width", text="Width (mm)")
        layout.prop(context.scene, "height", text="Height (mm)")
        layout.prop(context.scene, "target_volume", text="Target Volume (L)")
        layout.operator("object.scale_to_volume", text="Scale to Volume")

def register():
    bpy.utils.register_class(OBJECT_OT_scale_to_volume)
    bpy.utils.register_class(ScaleVolumePanel)

    bpy.types.Scene.width = bpy.props.FloatProperty(name="Width", default=150)
    bpy.types.Scene.height = bpy.props.FloatProperty(name="Height", default=120)
    bpy.types.Scene.target_volume = bpy.props.FloatProperty(name="Target Volume", default=2.5)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_scale_to_volume)
    bpy.utils.unregister_class(ScaleVolumePanel)

    del bpy.types.Scene.width
    del bpy.types.Scene.height
    del bpy.types.Scene.target_volume

