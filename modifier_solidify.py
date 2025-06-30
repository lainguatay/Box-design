import bpy
from bpy.props import FloatProperty, BoolProperty

# Biến toàn cục để tránh vòng lặp cập nhật
is_updating = False

# Cập nhật modifier Solidify khi panel thay đổi, áp dụng cho tất cả đối tượng đang chọn
def update_solidify_modifier(self, context):
    global is_updating
    if is_updating:
        return

    selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
    if not selected_objects:
        return

    is_updating = True
    settings = context.scene.solidify_settings
    for obj in selected_objects:
        solidify_mod = obj.modifiers.get("Solidify")
        if solidify_mod and solidify_mod.type == 'SOLIDIFY':
            solidify_mod.thickness = settings.solidify_thickness
            solidify_mod.offset = settings.solidify_offset
            solidify_mod.use_even_offset = True
            solidify_mod.use_rim = settings.solidify_fill_rim
    is_updating = False

# Cập nhật panel khi modifier thay đổi
def update_ui_on_modifier_change(scene):
    global is_updating
    if is_updating:
        return

    obj = bpy.context.object
    if not obj or obj.type != 'MESH':
        return

    solidify_mod = obj.modifiers.get("Solidify")
    settings = scene.solidify_settings
    if solidify_mod and solidify_mod.type == 'SOLIDIFY':
        if (abs(settings.solidify_thickness - solidify_mod.thickness) > 0.0001 or
            abs(settings.solidify_offset - solidify_mod.offset) > 0.0001 or
            settings.solidify_fill_rim != solidify_mod.use_rim):
            is_updating = True
            settings.solidify_thickness = solidify_mod.thickness
            settings.solidify_offset = solidify_mod.offset
            settings.solidify_fill_rim = solidify_mod.use_rim
            is_updating = False

# Cập nhật panel khi chọn đối tượng mới
def update_ui_on_selection_change(scene):
    global is_updating
    if is_updating:
        return

    obj = bpy.context.object
    if not obj or obj.type != 'MESH':
        return

    solidify_mod = obj.modifiers.get("Solidify")
    settings = scene.solidify_settings
    if solidify_mod and solidify_mod.type == 'SOLIDIFY':
        if (abs(settings.solidify_thickness - solidify_mod.thickness) > 0.0001 or
            abs(settings.solidify_offset - solidify_mod.offset) > 0.0001 or
            settings.solidify_fill_rim != solidify_mod.use_rim):
            is_updating = True
            settings.solidify_thickness = solidify_mod.thickness
            settings.solidify_offset = solidify_mod.offset
            settings.solidify_fill_rim = solidify_mod.use_rim
            is_updating = False

class OBJECT_OT_AddSolidifyModifier(bpy.types.Operator):
    bl_idname = "object.add_solidify_modifier"
    bl_label = "Thêm Solidify Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Vui lòng chọn ít nhất một đối tượng Mesh.")
            return {'CANCELLED'}

        settings = context.scene.solidify_settings
        success_count = 0
        
        try:
            for obj in selected_objects:
                context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
                solidify_mod = obj.modifiers.get("Solidify")
                if not solidify_mod:
                    solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')

                solidify_mod.thickness = settings.solidify_thickness
                solidify_mod.offset = settings.solidify_offset
                solidify_mod.use_even_offset = True
                solidify_mod.use_rim = settings.solidify_fill_rim
                success_count += 1

            self.report({'INFO'}, f"Đã thêm Solidify modifier cho {success_count} đối tượng thành công.")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi thêm Solidify: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_ApplySolidifyModifier(bpy.types.Operator):
    bl_idname = "object.apply_solidify_modifier"
    bl_label = "Apply Solidify Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Vui lòng chọn ít nhất một đối tượng Mesh.")
            return {'CANCELLED'}

        success_count = 0
        try:
            for obj in selected_objects:
                context.view_layer.objects.active = obj
                mod = obj.modifiers.get("Solidify")
                if mod:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    success_count += 1
            if success_count > 0:
                self.report({'INFO'}, f"Đã Apply Solidify Modifier cho {success_count} đối tượng.")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Không tìm thấy Solidify Modifier trên bất kỳ đối tượng nào.")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi Apply Solidify: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_RemoveSolidifyModifier(bpy.types.Operator):
    bl_idname = "object.remove_solidify_modifier"
    bl_label = "Xóa Solidify Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "Vui lòng chọn ít nhất một đối tượng Mesh.")
            return {'CANCELLED'}

        success_count = 0
        try:
            for obj in selected_objects:
                mod = obj.modifiers.get("Solidify")
                if mod:
                    obj.modifiers.remove(mod)
                    success_count += 1
            if success_count > 0:
                self.report({'INFO'}, f"Đã xóa Solidify Modifier khỏi {success_count} đối tượng.")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Không tìm thấy Solidify Modifier trên bất kỳ đối tượng nào.")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Lỗi khi xóa Solidify: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_SolidifyPanel(bpy.types.Panel):
    bl_label = "Solidify - Tạo độ dày"
    bl_idname = "VIEW3D_PT_solidify"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'
    bl_parent_id = "PT_ModifierToolsPanel"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.solidify_settings
        obj = context.object

        layout.prop(settings, "solidify_thickness", text="Độ dày")
        layout.prop(settings, "solidify_offset", text="Offset")
        layout.prop(settings, "solidify_fill_rim", text="Fill Rim")
        
        show_add = True
        show_apply_remove = False
        if obj and obj.type == 'MESH':
            solidify_mod = obj.modifiers.get("Solidify")
            if solidify_mod and solidify_mod.type == 'SOLIDIFY':
                show_apply_remove = True
                show_add = False
        if show_add:
              layout.operator("object.add_solidify_modifier", text="Thêm Solidify")
        if show_apply_remove:
            layout.operator("object.apply_solidify_modifier", text="Apply Solidify")
            layout.operator("object.remove_solidify_modifier", text="Xóa Solidify")

class SolidifySettings(bpy.types.PropertyGroup):
    solidify_thickness: FloatProperty(
        name="Solidify Thickness",
        default=6.0,
        min=0.0,
        update=update_solidify_modifier
    )
    solidify_offset: FloatProperty(
        name="Solidify Offset",
        default=1.0,
        min=-1.0,
        max=1.0,
        update=update_solidify_modifier
    )
    solidify_fill_rim: BoolProperty(
        name="Fill Rim",
        default=True,
        update=update_solidify_modifier
    )

classes = (
    OBJECT_OT_AddSolidifyModifier,
    OBJECT_OT_ApplySolidifyModifier,
    OBJECT_OT_RemoveSolidifyModifier,
    VIEW3D_PT_SolidifyPanel,
    SolidifySettings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.solidify_settings = bpy.props.PointerProperty(type=SolidifySettings)
    bpy.app.handlers.depsgraph_update_post.append(update_ui_on_selection_change)
    bpy.app.handlers.depsgraph_update_post.append(update_ui_on_modifier_change)

def unregister():
    if update_ui_on_selection_change in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_ui_on_selection_change)
    if update_ui_on_modifier_change in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_ui_on_modifier_change)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.solidify_settings

if __name__ == "__main__":
    register()