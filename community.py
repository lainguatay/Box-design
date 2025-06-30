import bpy
from bpy.types import Panel, Operator

class OBJECT_OT_OpenCommunityLink(Operator):
    bl_idname = "object.open_community_link"
    bl_label = "Open Community Link"
    
    url: bpy.props.StringProperty(name="URL", default="")

    def execute(self, context):
        if self.url:
            try:
                bpy.ops.wm.url_open(url=self.url)
                self.report({'INFO'}, f"Đã mở liên kết: {self.url}")
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Lỗi khi mở liên kết: {str(e)}")
                return {'CANCELLED'}
        self.report({'ERROR'}, "Không có URL được cung cấp.")
        return {'CANCELLED'}

class VIEW3D_PT_CommunityPanel(Panel):
    bl_label = "COMMUNITY"
    bl_idname = "VIEW3D_PT_community_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Box Design'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Tham gia cộng đồng Lại Ngứa Tay:")
        
        # Facebox button
        op = layout.operator(
            "object.open_community_link",
            text="Facebox",
            icon='FUND'
        )
        op.url = "https://www.facebook.com/groups/lainguatay"
        
        # YouTube button
        op = layout.operator(
            "object.open_community_link",
            text="YouTube",
            icon='FILE_MOVIE'
        )
        op.url = "https://www.youtube.com/@lainguatay"

classes = (
    OBJECT_OT_OpenCommunityLink,
    VIEW3D_PT_CommunityPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
