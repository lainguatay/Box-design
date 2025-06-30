bl_info = {
    "name": "Bounding box",
    "author": "Lai Ngua Tay",
    "version": (1, 3),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Box Design",
    "description": "Create axis-aligned bounding boxes from selected objects",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator, Panel, Object
from mathutils import Vector, Euler
from typing import Tuple, List

# ---------- UTILITY FUNCTIONS ----------

def set_object_origin_location(origin_location: Vector) -> None:
    old_cursor_location = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = origin_location
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.context.scene.cursor.location = old_cursor_location

def set_bounding_box_origin_to_corner(bounding_box: Object) -> None:
    new_origin = bounding_box.matrix_world @ bounding_box.data.vertices[0].co
    set_object_origin_location(new_origin)

def get_selected_objects_vertices(selected_objects: List[Object], active_object: Object = None, is_align_active_object: bool = False) -> List[Vector]:
    vertices = []
    for obj in selected_objects:
        vertices.extend([obj.matrix_world @ v.co for v in obj.data.vertices])
    if is_align_active_object and active_object:
        inv = active_object.matrix_world.inverted()
        vertices = [inv @ v for v in vertices]
    return vertices

def get_bounding_box_range(vertices: List[Vector]) -> Tuple[tuple]:
    return tuple((min(c), max(c)) for c in zip(*[(v.x, v.y, v.z) for v in vertices]))

def get_bounding_box_dimensions(bbox_range: Tuple[tuple]) -> Vector:
    return Vector(axis[1] - axis[0] for axis in bbox_range)

def get_bounding_box_corner_location(bbox_range: Tuple[tuple], active_object: Object = None, is_align_active_object: bool = False) -> Vector:
    corner = Vector(axis[0] for axis in bbox_range)
    if is_align_active_object and active_object:
        return active_object.matrix_world @ corner
    return corner

def create_basic_bounding_box(corner: Vector, size: Vector, rotation: Euler) -> Object:
    bpy.ops.mesh.primitive_cube_add()
    box = bpy.context.active_object
    set_bounding_box_origin_to_corner(box)
    box.dimensions = size
    box.location = corner
    box.rotation_euler = rotation
    return box

def get_selected_and_active(is_separate: bool = False) -> Tuple[List[Object], Object]:
    selected = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    active = bpy.context.active_object
    if is_separate and active in selected:
        selected.remove(active)
    return selected, active

def create_bounding_box(selected, active, align_to_active) -> Object:
    # Apply scale cho các đối tượng được chọn
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Tính toán bounding box
    verts = get_selected_objects_vertices(selected, active, align_to_active)
    bbox_range = get_bounding_box_range(verts)
    corner = get_bounding_box_corner_location(bbox_range, active, align_to_active)
    size = get_bounding_box_dimensions(bbox_range)
    rotation = active.rotation_euler if align_to_active and active else Euler()

    # Đặt tên cho bounding box
    bbox_name = f"{active.name}_bounding" if active else "Bounding_Box"

    # Xoá bounding box cũ nếu đã tồn tại
    old_bbox = bpy.data.objects.get(bbox_name)
    if old_bbox:
        bpy.data.objects.remove(old_bbox, do_unlink=True)

    # Tạo bounding box mới
    bbox = create_basic_bounding_box(corner, size, rotation)
    bbox.name = bbox_name

    # Đặt origin về tâm bounding box
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    # Hiển thị dưới dạng wireframe
    bbox.display_type = 'WIRE'
    
    return bbox

# ---------- OPERATOR ----------

class MESH_OT_bounding_box(Operator):
    bl_idname = "mesh.bounding_box"
    bl_label = "Tạo hình bao"
    bl_description = "Create a bounding box from selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    coordinate_system: bpy.props.EnumProperty(
        items=[
            ("active_object", "Active Object", "Use active object's coordinate system"),
            ("world", "World", "Use world coordinate system"),
        ],
        name="Coordinate System",
        default="active_object",
    )

    is_separate_active_object: bpy.props.BoolProperty(
        name="Separate Active Object",
        default=False,
        description="Exclude active object from bounding box calculation",
    )

    is_wireframe: bpy.props.BoolProperty(
        name="Display as Wireframe",
        default=False,
        description="Show bounding box in wireframe mode",
    )

    is_render: bpy.props.BoolProperty(
        name="Show in Renders",
        default=True,
        description="Render the bounding box",
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and any(
            o for o in context.selected_objects if o.type == "MESH"
        )

    def execute(self, context):
        selected, active = get_selected_and_active(self.is_separate_active_object)
        if not selected or not active:
            self.report({'WARNING'}, "Need at least one selected object and an active object")
            return {'CANCELLED'}

        align = self.coordinate_system == "active_object"
        bbox = create_bounding_box(selected, active, align)

        if self.is_wireframe:
            bbox.display_type = 'WIRE'
        bbox.hide_render = not self.is_render

        return {'FINISHED'}

# ---------- SIDEBAR PANEL ----------

class VIEW3D_PT_bounding_box_panel(Panel):
    bl_label = "Bounding Box"
    bl_idname = "VIEW3D_PT_bounding_box_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_BoxToolsPanel"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Bounding Box")
        layout.operator("mesh.bounding_box")

# ---------- REGISTER ----------

bl_classes = (
    MESH_OT_bounding_box,
    VIEW3D_PT_bounding_box_panel,
)

def register():
    for cls in bl_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(bl_classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
