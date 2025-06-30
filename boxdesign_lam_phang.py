bl_info = {
    "name": "Làm phẳng & Xếp mặt",
    "blender": (4, 0, 0),
    "category": "Object",
}

import bpy
import math
import numpy as np
from mathutils import Vector, Matrix

# --- PCA ALIGNMENT ---
def align_object_points_to_xy(obj):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    coords = np.array([[v.x, v.y, v.z] for v in verts])

    centroid = np.mean(coords, axis=0)
    centered = coords - centroid

    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    normal = vh[2]

    if normal[2] < 0:
        normal = -normal

    z_axis = Vector((0, 0, 1))
    normal_vec = Vector(normal)
    axis = normal_vec.cross(z_axis)
    angle = normal_vec.angle(z_axis)

    if axis.length > 1e-6 and angle > 1e-6:
        R = Matrix.Rotation(angle, 4, axis.normalized())
        obj.matrix_world = R @ obj.matrix_world
        bpy.context.view_layer.update()

def flatten_object_to_ground(obj):
    mesh = obj.data
    min_z = float('inf')
    for v in mesh.vertices:
        world_v = obj.matrix_world @ v.co
        if world_v.z < min_z:
            min_z = world_v.z
    obj.location.z -= min_z

def get_bbox_2d(obj):
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    return min_x, max_x, min_y, max_y

def flatten_and_arrange(objs, cols, spacing):
    # Làm phẳng & thu thập dữ liệu bounding box
    bbox_data = []
    for obj in objs:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        align_object_points_to_xy(obj)
        flatten_object_to_ground(obj)
        bpy.context.view_layer.update()

        min_x, max_x, min_y, max_y = get_bbox_2d(obj)
        width = max_x - min_x
        height = max_y - min_y
        bbox_data.append({
            'obj': obj,
            'width': width,
            'height': height,
            'min_x': min_x,
            'min_y': min_y,
        })

    # Tự tính số hàng
    rows = math.ceil(len(objs) / cols)

    # Bắt đầu sắp xếp
    x_offset = 0
    y_offset = 0
    col = 0
    row_max_height = 0

    for i, data in enumerate(bbox_data):
        obj = data['obj']
        width = data['width']
        height = data['height']
        min_x = data['min_x']
        min_y = data['min_y']

        # Vị trí mới: giữ nguyên kích thước, dịch sang đúng vị trí
        dx = x_offset - min_x
        dy = -y_offset - min_y
        obj.location.x += dx
        obj.location.y += dy

        # Cập nhật offset cho object kế tiếp
        x_offset += width + spacing
        row_max_height = max(row_max_height, height)
        col += 1

        # Nếu hết cột, chuyển hàng
        if col >= cols:
            col = 0
            x_offset = 0
            y_offset += row_max_height + spacing
            row_max_height = 0

# --- Properties ---
class FlattenProps(bpy.types.PropertyGroup):
    def update_trigger(self, context):
        selected_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if selected_objs:
            flatten_and_arrange(selected_objs, self.cols, self.spacing)

    cols: bpy.props.IntProperty(
        name="Số cột", default=3, min=1,
        update=update_trigger
    )
    spacing: bpy.props.FloatProperty(
        name="Khoảng cách", default=10, min=0,
        update=update_trigger
    )


# --- Operator ---
class OBJECT_OT_flatten_arrange(bpy.types.Operator):
    bl_idname = "object.flatten_arrange"
    bl_label = "Làm phẳng và xếp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.flatten_props
        selected_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if selected_objs:
            flatten_and_arrange(selected_objs, props.cols, props.spacing)
            self.report({'INFO'}, "✅ Đã làm phẳng và xếp.")
        else:
            self.report({'WARNING'}, "⚠️ Chưa chọn object nào.")
        return {'FINISHED'}

# --- UI Panel ---
class OBJECT_PT_flatten_panel(bpy.types.Panel):
    bl_label = "Làm phẳng"
    bl_idname = "OBJECT_PT_flatten_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Box Design"
    bl_parent_id = "PT_BoxToolsPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.flatten_props

        layout.prop(props, "cols")
        layout.prop(props, "spacing")
        layout.operator("object.flatten_arrange")


# --- Đăng ký ---
classes = (
    FlattenProps,
    OBJECT_OT_flatten_arrange,
    OBJECT_PT_flatten_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.flatten_props = bpy.props.PointerProperty(type=FlattenProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.flatten_props

if __name__ == "__main__":
    register()

