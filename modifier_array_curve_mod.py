import bpy
import bmesh

# Hàm cập nhật chiều dài Array khi thay đổi
def update_array_fit_length(self, context):
    obj = context.object
    if obj:
        mod = obj.modifiers.get("Array")
        if mod and mod.type == 'ARRAY':
            mod.fit_type = 'FIT_LENGTH'
            mod.fit_length = context.scene.array_curve_settings.fit_length

# Operator tạo Array + Curve Modifier
class OBJECT_OT_ArrayCurveSetup(bpy.types.Operator):
    bl_idname = "object.array_curve_setup"
    bl_label = "Tạo Array + Curve Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        active = context.view_layer.objects.active

        if len(selected) < 1:
            self.report({'ERROR'}, "Chọn ít nhất 1 đối tượng (không cần chọn curve, curve sẽ được tạo tự động)")
            return {'CANCELLED'}

        obj = active

        # Tạo curve
        curve_data = bpy.data.curves.new(name="StraightCurve", type='CURVE')
        curve_data.dimensions = '3D'
        curve_obj = bpy.data.objects.new("StraightCurveObj", curve_data)
        curve_obj.location = obj.location
        bpy.context.collection.objects.link(curve_obj)

        spline = curve_data.splines.new('POLY')
        spline.points.add(2)
        spline.points[0].co = (0, 0, 0, 1)
        spline.points[1].co = (0, -60, 0, 1)
        spline.points[2].co = (-context.scene.array_curve_settings.fit_length, -60, 0, 1)

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces], context='FACES_ONLY')
        bmesh.update_edit_mesh(obj.data)

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, -2, 0)})
        bpy.ops.object.mode_set(mode='OBJECT')

        settings = context.scene.array_curve_settings

        # Array Modifier
        array_mod = obj.modifiers.new(name="Array", type='ARRAY')
        array_mod.use_relative_offset = True
        array_mod.relative_offset_displace = (0, 0, 1)
        array_mod.use_merge_vertices = True
        array_mod.fit_type = 'FIT_LENGTH'
        array_mod.fit_length = settings.fit_length

        # Curve Modifier
        curve_mod = obj.modifiers.new(name="Curve", type='CURVE')
        curve_mod.object = curve_obj
        curve_mod.deform_axis = 'NEG_Y'

        # Tính lại pháp tuyến
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

# Operator Apply Array + Curve
class OBJECT_OT_ApplyArrayCurveModifier(bpy.types.Operator):
    bl_idname = "object.apply_array_curve_modifier"
    bl_label = "Apply Array + Curve Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "Không có đối tượng được chọn.")
            return {'CANCELLED'}

        for mod_name in ["Array", "Curve"]:
            mod = obj.modifiers.get(mod_name)
            if mod:
                bpy.ops.object.modifier_apply(modifier=mod.name)
        self.report({'INFO'}, "Đã Apply Array + Curve")
        return {'FINISHED'}

# Giao diện hiển thị trong UI
class VIEW3D_PT_ArrayCurvePanel(bpy.types.Panel):
    bl_label = "Tạo Array + Curve"
    bl_idname = "VIEW3D_PT_array_curve"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_ModifierToolsPanel"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.array_curve_settings
        obj = context.object

        layout.prop(settings, "fit_length", text="Độ dài")

        show_create = True
        show_apply = False

        if obj and obj.type == 'MESH':
            has_array = obj.modifiers.get("Array") is not None
            has_curve = obj.modifiers.get("Curve") is not None

            if has_array and has_curve:
                show_apply = True
                show_create = False

        if show_create:
            layout.operator("object.array_curve_setup", text="Tạo Array + Curve")
        if show_apply:
            layout.operator("object.apply_array_curve_modifier", text="Apply Array + Curve")

# Thuộc tính tùy chỉnh lưu trạng thái UI
class ArrayCurveSettings(bpy.types.PropertyGroup):
    fit_length: bpy.props.FloatProperty(
        name="Fit Length",
        default=200,
        min=0.1,
        update=update_array_fit_length
    )

# Đăng ký addon
classes = (
    OBJECT_OT_ArrayCurveSetup,
    OBJECT_OT_ApplyArrayCurveModifier,
    VIEW3D_PT_ArrayCurvePanel,
    ArrayCurveSettings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.array_curve_settings = bpy.props.PointerProperty(type=ArrayCurveSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.array_curve_settings

if __name__ == "__main__":
    register()
