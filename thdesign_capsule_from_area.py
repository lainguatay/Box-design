import bpy
import math
from .shared_props import SharedCapsuleSettings
from .area_utils import calculate_area_of_selected_object

def update_capsule_from_area(self, context):
    try:
        bpy.ops.object.create_capsule_from_area()
    except:
        pass  # Tránh lỗi nếu chưa có object được chọn

def calculate_radius_from_area(area, height):
    """Tính bán kính từ diện tích mặt cắt 2D và chiều cao của viên nang."""
    if area <= 0 or height <= 0:
        return None
    
    # Công thức diện tích mặt cắt 2D: A = 2rh + πr²
    # Chuyển thành phương trình bậc hai: πr² + 2hr - A = 0
    a = math.pi
    b = 2 * height
    c = -area
    
    # Tính nghiệm phương trình bậc hai
    disc = b**2 - 4 * a * c
    if disc < 0:
        return None
    
    # Lấy nghiệm dương
    r = (-b + math.sqrt(disc)) / (2 * a)
    if r <= 0:
        return None
    return r

def get_previous_selected_object():
    for obj in bpy.context.selected_objects:
        if obj.name.startswith("Capsule2D"):
            continue
        if obj.type in {'MESH', 'CURVE'}:
            return obj
    return None

def create_capsule_polygon(radius, height, seg=32, horizontal=False):
    selected_obj = get_previous_selected_object()

    # Tên gốc của capsule
    if selected_obj:
        base_name = f"Capsule2D_{selected_obj.name}"
    else:
        base_name = "Capsule2D"

    # Xóa capsule cũ nếu đang chọn cùng đối tượng
    for obj in list(bpy.data.objects):
        if obj.name == base_name or obj.name.startswith(base_name + "_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Tìm tên chưa trùng
    name = base_name
    index = 1
    while name in bpy.data.objects:
        name = f"{base_name}_{index}"
        index += 1

    # Tạo mesh viên nang
    verts = []
    for i in range(seg + 1):
        angle = math.pi * i / seg
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius + height / 2
        verts.append((x, y, 0))
    for i in range(seg + 1):
        angle = math.pi * i / seg
        x = math.cos(math.pi - angle) * radius
        y = -math.sin(angle) * radius - height / 2
        verts.append((x, y, 0))

    faces = [list(range(len(verts)))]
    mesh_data = bpy.data.meshes.new(name + "_Mesh")
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()

    obj = bpy.data.objects.new(name, mesh_data)

    # Đặt vị trí capsule tại object gốc
    if selected_obj:
        obj.location = selected_obj.location
    else:
        obj.location = bpy.context.scene.cursor.location

    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Xoay nếu nằm ngang
    if horizontal:
        obj.rotation_euler = (math.radians(90), math.radians(-90), 0)
    else:
        obj.rotation_euler = (math.radians(90), 0, 0)

class OBJECT_OT_SetHeightValue(bpy.types.Operator):
    bl_idname = "object.set_height_value"
    bl_label = "Set Height"

    value: bpy.props.FloatProperty()

    def execute(self, context):
        context.scene.shared_capsule_settings.height = self.value
        return {'FINISHED'}

class OBJECT_OT_CreateCapsuleFromArea(bpy.types.Operator):
    bl_idname = "object.create_capsule_from_area"
    bl_label = "Tạo viên nang"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.shared_capsule_settings
        height = props.height
        horizontal = props.horizontal

        if height <= 0:
            self.report({'ERROR'}, "Chiều cao phải lớn hơn 0.")
            return {'CANCELLED'}

        area = calculate_area_of_selected_object()
        if area is None or area <= 0:
            self.report({'ERROR'}, "Vui lòng chọn một đối tượng Mesh hoặc Curve hợp lệ.")
            return {'CANCELLED'}

        r = calculate_radius_from_area(area, height)
        if r is None or r <= 0:
            self.report({'ERROR'}, "Không thể tính bán kính từ diện tích và chiều cao.")
            return {'CANCELLED'}

        try:
            create_capsule_polygon(r, height, horizontal=horizontal)
            self.report({'INFO'}, "Đã tạo viên nang thành công.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi tạo viên nang: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_CapsuleAreaPanel(bpy.types.Panel):
    bl_label = "Tạo TH hình viên nang"
    bl_idname = "VIEW3D_PT_capsule_area"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_THToolsPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.shared_capsule_settings
        layout.prop(props, "height")
        
        # Thêm hàng nút đặt nhanh
        row = layout.row()
        for v in [10, 20, 30, 40, 50]:
            row.operator("object.set_height_value", text=str(v)).value = v

        layout.prop(props, "horizontal")
#        layout.operator("object.create_capsule_from_area")

classes = (
    OBJECT_OT_CreateCapsuleFromArea,
    OBJECT_OT_SetHeightValue,
    VIEW3D_PT_CapsuleAreaPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
