import bpy
import bmesh
from mathutils import Vector
from bpy.app.handlers import persistent

updating_dimensions = False

def calculate_volume(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Kiểm tra xem mesh có kín không
    if not bm.is_valid or any(e.is_boundary for e in bm.edges):
        bm.free()
        return 0.0
    volume = bm.calc_volume()
    bm.free()
    return volume

def get_base_dimensions(obj):
    orig_scale = obj.scale.copy()
    obj.scale = Vector((1, 1, 1))
    bpy.context.view_layer.update()
    base_dim = obj.dimensions.copy()
    obj.scale = orig_scale
    bpy.context.view_layer.update()
    return base_dim

def scale_object_to_dims(obj, width, height, target_volume_liters):
    target_volume = target_volume_liters * 1_000_000  # Chuyển từ lít sang mm³
    base_volume = calculate_volume(obj)  # Sử dụng thể tích thực
    base_dim = get_base_dimensions(obj)
    base_width, base_depth, base_height = base_dim.x, base_dim.y, base_dim.z

    if base_volume == 0 or base_width == 0 or base_height == 0:
        return False

    scale_x = width / base_width
    scale_z = height / base_height
    # Tính scale_y dựa trên thể tích thực
    scale_y = (target_volume / base_volume) / (scale_x * scale_z)
    if scale_y <= 0:
        return False

    obj.scale = Vector((scale_x, scale_y, scale_z))
    bpy.context.view_layer.update()
    # Áp dụng tỷ lệ sau khi thay đổi
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return True

def scale_object_to_volume_only(obj, target_volume_liters):
    target_volume = target_volume_liters * 1_000_000  # Chuyển từ lít sang mm³
    base_volume = calculate_volume(obj)  # Sử dụng thể tích thực
    base_dim = get_base_dimensions(obj)
    base_width, base_depth, base_height = base_dim.x, base_dim.y, base_dim.z
    if base_volume == 0 or base_width == 0 or base_height == 0:
        return False

    scale_x = obj.scale.x
    scale_z = obj.scale.z

    scale_y = (target_volume / base_volume) / (scale_x * scale_z)
    if scale_y <= 0:
        return False

    obj.scale.y = scale_y
    bpy.context.view_layer.update()
    # Áp dụng tỷ lệ sau khi thay đổi
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return True

def update_scene_dimensions_from_object(scene):
    global updating_dimensions
    if updating_dimensions:
        return
    objs = [obj for obj in scene.objects if obj.select_get() and obj.type == 'MESH']
    if not objs:
        return
    obj = objs[0]
    dim = obj.dimensions

    updating_dimensions = True
    if abs(scene.width - dim.x) > 1e-4:
        scene.width = dim.x
    if abs(scene.height - dim.z) > 1e-4:
        scene.height = dim.z
    updating_dimensions = False

@persistent
def depsgraph_update_handler(scene, depsgraph):
    update_scene_dimensions_from_object(scene)

def on_dimension_prop_update(self, context):
    global updating_dimensions
    if updating_dimensions:
        return

    scene = context.scene
    objs = [obj for obj in scene.objects if obj.select_get() and obj.type == 'MESH']
    if not objs:
        return
    obj = objs[0]

    updating_dimensions = True
    success = scale_object_to_dims(obj, scene.width, scene.height, scene.target_volume)
    if not success:
        print("Failed to scale object in on_dimension_prop_update due to invalid volume or dimensions.")
    updating_dimensions = False

def on_volume_prop_update(self, context):
    global updating_dimensions
    if updating_dimensions:
        return

    scene = context.scene
    objs = [obj for obj in scene.objects if obj.select_get() and obj.type == 'MESH']
    if not objs:
        return
    obj = objs[0]

    updating_dimensions = True
    success = scale_object_to_volume_only(obj, scene.target_volume)
    if not success:
        print("Failed to scale object in on_volume_prop_update due to invalid volume.")
    updating_dimensions = False

class OBJECT_OT_UpdateScale(bpy.types.Operator):
    bl_idname = "object.update_scale"
    bl_label = "Cập nhật"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        # Kiểm tra xem có đối tượng mesh được chọn không
        objs = [obj for obj in scene.objects if obj.select_get() and obj.type == 'MESH']
        if not objs:
            self.report({'ERROR'}, "Không có đối tượng mesh nào được chọn.")
            return {'CANCELLED'}
        obj = objs[0]

        # Kiểm tra giá trị target_volume
        if scene.target_volume <= 0:
            self.report({'ERROR'}, "Dung tích phải lớn hơn 0.")
            return {'CANCELLED'}

        # Kiểm tra mesh có kín không
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if any(e.is_boundary for e in bm.edges):
            bm.free()
            self.report({'ERROR'}, "Đối tượng mesh phải là hình khối kín để tính thể tích.")
            return {'CANCELLED'}
        bm.free()

        global updating_dimensions
        updating_dimensions = True
        success = scale_object_to_volume_only(obj, scene.target_volume)
        updating_dimensions = False

        if not success:
            self.report({'ERROR'}, "Không thể thay đổi tỷ lệ do thể tích không hợp lệ hoặc mesh không hợp lệ.")
            return {'CANCELLED'}

        # Cập nhật lại chiều rộng và chiều cao trong UI
        update_scene_dimensions_from_object(scene)
        self.report({'INFO'}, "Đã cập nhật chiều sâu thành công.")
        return {'FINISHED'}
        
# Tạo operator cho nút Tach Face
class SeparateFacesOperator(bpy.types.Operator):
    bl_idname = "mesh.separate_faces_button"
    bl_label = "Tách Face"

    def execute(self, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            # Lưu tên object ban đầu
            original_name = obj.name
            
            # Chuyển sang Edit Mode
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Tạo BMesh để xử lý mesh
            bm = bmesh.from_edit_mesh(obj.data)
            
            # Lưu danh sách các mặt
            faces = [face for face in bm.faces]
            
            # Tách từng mặt thành object riêng
            for i, face in enumerate(faces):
                bm.faces.ensure_lookup_table()
                # Chọn mặt hiện tại
                for f in bm.faces:
                    f.select = False
                face.select = True
                
                # Tách mặt được chọn
                bpy.ops.mesh.separate(type='SELECTED')
            
            # Cập nhật mesh
            bmesh.update_edit_mesh(obj.data)
            
            # Chuyển về Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Xóa object ban đầu nếu nó còn tồn tại và không có mặt
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            if not bm.faces:
                bpy.ops.object.delete()
            
            # Giải phóng BMesh
            bm.free()
        else:
            self.report({'WARNING'}, "Vui lòng chọn một object Mesh")
        
        return {'FINISHED'}

class ScaleVolumePanel(bpy.types.Panel):
    bl_label = "Scale Volume"
    bl_idname = "PT_ScaleVolumePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"
    bl_parent_id = "PT_BoxToolsPanel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "width", text="Chiều rộng (mm)")
        layout.prop(scene, "height", text="Chiều cao (mm)")
        layout.prop(scene, "target_volume", text="Dung tích (L)")
        layout.operator("object.update_scale", text="Cập nhật")
        obj = context.active_object
        row = layout.row()
        if obj and obj.type == 'MESH':
            row.operator("mesh.separate_faces_button", text="Tách Face")
        else:
            row.label(text="Chọn một object Mesh")

def register():
    bpy.types.Scene.width = bpy.props.FloatProperty(
        name="Width",
        default=150,
        min=0.01,
        update=on_dimension_prop_update
    )
    bpy.types.Scene.height = bpy.props.FloatProperty(
        name="Height",
        default=120,
        min=0.01,
        update=on_dimension_prop_update
    )
    bpy.types.Scene.target_volume = bpy.props.FloatProperty(
        name="Target Volume (L)",
        default=2.5,
        min=0.001,
        update=on_volume_prop_update
    )

    bpy.utils.register_class(ScaleVolumePanel)
    bpy.utils.register_class(OBJECT_OT_UpdateScale)

    if depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_handler)
        
    bpy.utils.register_class(SeparateFacesOperator)

def unregister():
    bpy.utils.unregister_class(ScaleVolumePanel)
    bpy.utils.unregister_class(OBJECT_OT_UpdateScale)
    del bpy.types.Scene.width
    del bpy.types.Scene.height
    del bpy.types.Scene.target_volume
    bpy.utils.unregister_class(SeparateFacesOperator)

    if depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_handler)
