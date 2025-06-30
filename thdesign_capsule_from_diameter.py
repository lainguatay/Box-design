import bpy
import math
from bpy.props import FloatProperty
from . import shared_props

def update_capsule(self, context):
    bpy.ops.object.create_capsule_from_diameter()
    bpy.ops.object.create_capsule_rim()

def update_rim(self, context):
    bpy.ops.object.create_capsule_rim()


def create_capsule_polygon(radius, height, seg=32, horizontal=False, name="Mieng_ong"):
    # Remove old object if it exists
    old_obj = bpy.data.objects.get(name)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)

    # Create capsule mesh
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
    mesh_data = bpy.data.meshes.new("CapsuleMesh")
    mesh_data.from_pydata(verts, [], faces)
    mesh_data.update()

    obj = bpy.data.objects.new(name, mesh_data)
    obj.location = bpy.context.scene.cursor.location
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Rotate capsule based on orientation
    if horizontal:
        obj.rotation_euler.y = math.radians(-90)
        obj.rotation_euler.x = math.radians(90)
    else:
        obj.rotation_euler.x = math.radians(90)

class CapsuleFromDiameterProps(bpy.types.PropertyGroup):
    diameter: FloatProperty(
        name="Đường kính",
        default=65,
        min=0.01,
        description="Diameter of the capsule",
        update=update_capsule 
    )

    diameter_offset: FloatProperty(
        name="Độ tăng đường kính vành",
        default=20,
        min=0,
        description="Offset to add to diameter for rim",
        update=update_rim
    )

class OBJECT_OT_CreateCapsuleFromDiameter(bpy.types.Operator):
    bl_idname = "object.create_capsule_from_diameter"
    bl_label = "Tạo miệng ống"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.capsule_diam_props
        shared = context.scene.shared_capsule_settings
        r = props.diameter / 2
        h = shared.height
        horizontal = shared.horizontal

        if r <= 0 or h <= 0:
            self.report({'ERROR'}, "Đường kính và khoảng cách tâm phải lớn hơn 0.")
            return {'CANCELLED'}

        try:
            create_capsule_polygon(r, h, horizontal=horizontal, name="Mieng_ong")
            self.report({'INFO'}, "Đã tạo phần loe thành công.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi tạo phần loe: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_CreateCapsuleRim(bpy.types.Operator):
    bl_idname = "object.create_capsule_rim"
    bl_label = "Tạo vành"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.capsule_diam_props
        shared = context.scene.shared_capsule_settings
        r = (props.diameter + props.diameter_offset) / 2
        h = shared.height
        horizontal = shared.horizontal

        if r <= 0 or h <= 0:
            self.report({'ERROR'}, "Đường kính và khoảng cách tâm phải lớn hơn 0.")
            return {'CANCELLED'}

        try:
            create_capsule_polygon(r, h, horizontal=horizontal, name="Mieng_ong_vanh")
            self.report({'INFO'}, "Đã tạo vành thành công.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi tạo vành: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_SetDiameter(bpy.types.Operator):
    bl_idname = "object.set_diameter_value"
    bl_label = "Set Diameter"
    
    value: FloatProperty()

    def execute(self, context):
        context.scene.capsule_diam_props.diameter = self.value
        return {'FINISHED'}

class VIEW3D_PT_CapsuleDiameterPanel(bpy.types.Panel):
    bl_label = "Tạo miệng ống"
    bl_idname = "VIEW3D_PT_capsule_diameter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_THToolsPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.capsule_diam_props
        layout.prop(props, "diameter")
        

        # Add quick-select buttons
        values = [16, 18, 20, 21, 22, 24, 25, 27, 30, 32, 34, 35, 40, 42, 45, 50, 55, 60, 65]
        for i in range(0, len(values), 5):  # 5 buttons per row
            row = layout.row()
            for v in values[i:i+5]:
                row.operator("object.set_diameter_value", text=str(v)).value = v

  #      layout.operator("object.create_capsule_from_diameter")
        layout.prop(props, "diameter_offset")
 #       layout.operator("object.create_capsule_rim")

classes = (
    CapsuleFromDiameterProps,
    OBJECT_OT_CreateCapsuleFromDiameter,
    OBJECT_OT_CreateCapsuleRim,
    OBJECT_OT_SetDiameter,
    VIEW3D_PT_CapsuleDiameterPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.capsule_diam_props = bpy.props.PointerProperty(type=CapsuleFromDiameterProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.capsule_diam_props