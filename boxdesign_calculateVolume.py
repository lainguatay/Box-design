import bpy
import bmesh
from bpy.props import FloatProperty


def compute_volume(obj, depsgraph):
    if obj.type != 'MESH':
        return 0.0

    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    if not mesh:
        return 0.0

    bm = bmesh.new()
    bm.from_mesh(mesh)

    try:
        volume_local = bm.calc_volume(signed=False)
    except Exception as e:
        print("Lỗi khi tính thể tích:", e)
        volume_local = 0.0

    bm.free()
    eval_obj.to_mesh_clear()

    scale = obj.matrix_world.to_scale()
    volume_world = volume_local * scale.x * scale.y * scale.z

    # Đơn vị chiều dài đang là mm, nên thể tích tính ra là mm³
    # 1 lít = 1,000,000 mm³ → nhân 1e-6 để ra lít
    volume_liters = volume_world * 1e-6

    return volume_liters


class OBJECT_OT_CalculateVolume(bpy.types.Operator):
    bl_idname = "object.calculate_volume_liters"
    bl_label = "Tính thể tích"
    bl_description = "Tính thể tích của mesh hiện tại (lít)"

    def execute(self, context):
        obj = context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Chỉ áp dụng cho đối tượng mesh.")
            return {'CANCELLED'}

        depsgraph = context.evaluated_depsgraph_get()
        volume_l = compute_volume(obj, depsgraph)
        obj.volume_liters = volume_l

        self.report({'INFO'}, f"Thể tích: {volume_l:.6f} L")
        return {'FINISHED'}


class OBJECT_PT_VolumePanel(bpy.types.Panel):
    bl_label = "Thể tích đối tượng"
    bl_idname = "OBJECT_PT_volume_liters"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_BoxToolsPanel"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        layout.operator("object.calculate_volume_liters")
        layout.label(text=f"Thể tích: {obj.volume_liters:.6f} L")


def register():
    bpy.utils.register_class(OBJECT_OT_CalculateVolume)
    bpy.utils.register_class(OBJECT_PT_VolumePanel)
    bpy.types.Object.volume_liters = FloatProperty(
        name="Volume (liters)",
        description="Thể tích đã tính",
        default=0.0
    )


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CalculateVolume)
    bpy.utils.unregister_class(OBJECT_PT_VolumePanel)
    del bpy.types.Object.volume_liters
