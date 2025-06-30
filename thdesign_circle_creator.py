import bpy
from bpy.props import FloatProperty

def update_circle(self, context):
    # Xoá hình tròn cũ nếu có
    obj = bpy.data.objects.get("FilledCircle")
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Tạo lại hình tròn
    bpy.ops.object.create_filled_circle()


class CircleProperties(bpy.types.PropertyGroup):
    circle_diameter: FloatProperty(
        name="Đường kính",
        description="Diameter of the filled circle",
        default=60,
        min=0.01,
        precision=4,
        update=update_circle
    )


class OBJECT_OT_CreateFilledCircle(bpy.types.Operator):
    bl_idname = "object.create_filled_circle"
    bl_label = "Create Filled Circle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.circle_props
        radius = props.circle_diameter / 2.0

        # Lấy vị trí con trỏ 3D
        cursor_location = context.scene.cursor.location
        bpy.ops.mesh.primitive_circle_add(
            radius=radius,
            fill_type='NGON',
            vertices=64,
            enter_editmode=False,
            location=cursor_location,
            rotation=(1.5707964, 0, 0)
        )

        obj = bpy.context.active_object
        obj.name = "FilledCircle"


        return {'FINISHED'}


class VIEW3D_PT_CirclePanel(bpy.types.Panel):
    bl_label = "Đường kính TH"
    bl_idname = "VIEW3D_PT_circle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_THToolsPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.circle_props
        layout.prop(props, "circle_diameter")
        row = layout.row()
        for v in [10, 20, 30, 40, 50]:
            row.operator("object.set_circle_diameter", text=str(v)).value = v
 #       layout.operator("object.create_filled_circle", text="Tạo hình tròn")

class OBJECT_OT_SetCircleDiameter(bpy.types.Operator):
    bl_idname = "object.set_circle_diameter"
    bl_label = "Set Circle Diameter"

    value: FloatProperty()

    def execute(self, context):
        context.scene.circle_props.circle_diameter = self.value
        return {'FINISHED'}


classes = (
    CircleProperties,
    OBJECT_OT_CreateFilledCircle,
    OBJECT_OT_SetCircleDiameter,
    VIEW3D_PT_CirclePanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.circle_props = bpy.props.PointerProperty(type=CircleProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.circle_props


if __name__ == "__main__":
    register()

