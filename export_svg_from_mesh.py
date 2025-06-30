bl_info = {
    "name": "SVG Export",
    "author": "Lai Ngua Tay",
    "version": (2, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > SVG Export",
    "description": "Export selected mesh/curve objects to SVG with proper fill and holes",
    "category": "Import-Export",
}

import bpy
import bmesh
import os
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector

class EXPORT_OT_svg_from_selection(bpy.types.Operator, ExportHelper):
    bl_idname = "export_object.svg_selection"
    bl_label = "Export Selection to SVG"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".svg"
    filter_glob: StringProperty(default="*.svg", options={'HIDDEN'})
    auto_name: BoolProperty(
        name="Auto Name File",
        description="Automatically name the SVG file as BlendFile_ObjectName",
        default=True,
    )

    def invoke(self, context, event):
        if self.auto_name and context.selected_objects:
            # Get the blend file name if saved, otherwise use default behavior
            blend_file = bpy.data.filepath
            if blend_file:
                blend_name = os.path.splitext(os.path.basename(blend_file))[0]
                first_obj_name = context.selected_objects[0].name.replace(" ", "_")
                auto_filename = f"{blend_name}_{first_obj_name}{self.filename_ext}"
                self.filepath = os.path.join(os.path.dirname(blend_file), auto_filename)
            else:
                # If blend file is not saved, let user choose location
                self.filepath = os.path.join(os.path.expanduser("~"), f"untitled_{context.selected_objects[0].name.replace(' ', '_')}{self.filename_ext}")
        return super().invoke(context, event)

    def get_view_projection(self, context):
        rv3d = context.region_data
        if not rv3d or rv3d.view_perspective != 'ORTHO':
            self.report({'ERROR'}, "Only Orthographic views are supported")
            return None

        forward = rv3d.view_rotation @ Vector((0, 0, -1))
        abs_f = [abs(x) for x in forward]
        max_axis = max(abs_f)
        axis_index = abs_f.index(max_axis)

        if axis_index == 2:  # Z-axis
            if forward.z < 0:
                return lambda co: (co.x, -co.y)  # Top view
            else:
                return lambda co: (co.x, co.y)  # Bottom view
        elif axis_index == 1:  # Y-axis
            if forward.y < 0:
                return lambda co: (-co.x, -co.z)  # Back view
            else:
                return lambda co: (co.x, -co.z)  # Front view
        elif axis_index == 0:  # X-axis
            if forward.x < 0:
                return lambda co: (co.y, -co.z)  # Right view
            else:
                return lambda co: (-co.y, -co.z)  # Left view
        else:
            self.report({'WARNING'}, "View not clearly recognized, defaulting to XY")
            return lambda co: (co.x, co.y)  # Default to Top view

    def execute(self, context):
        objects = [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]
        if not objects:
            self.report({'ERROR'}, "No mesh or curve objects selected")
            return {'CANCELLED'}

        project = self.get_view_projection(context)
        if not project:
            return {'CANCELLED'}

        # Apply auto_name logic again if blend file is saved
        if self.auto_name and objects and bpy.data.filepath:
            blend_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
            first_obj_name = objects[0].name.replace(" ", "_")
            auto_filename = f"{blend_name}_{first_obj_name}{self.filename_ext}"
            self.filepath = os.path.join(os.path.dirname(bpy.data.filepath), auto_filename)

        svg_lines = []
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        def update_bounds(p):
            nonlocal min_x, max_x, min_y, max_y
            x, y = p
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        depsgraph = context.evaluated_depsgraph_get()

        for obj in objects:
            svg_lines.append(f'<!-- Object: {obj.name} -->')
            mat_world = obj.matrix_world

            if obj.type == 'MESH':
                eval_obj = obj.evaluated_get(depsgraph)
                mesh = eval_obj.to_mesh()
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bmesh.ops.triangulate(bm, faces=bm.faces)

                # Group faces into connected islands
                islands = []
                visited = set()

                def walk_faces(start_face, collected):
                    stack = [start_face]
                    while stack:
                        face = stack.pop()
                        if face.index in visited:
                            continue
                        visited.add(face.index)
                        collected.append(face)
                        for edge in face.edges:
                            for linked_face in edge.link_faces:
                                if linked_face.index not in visited:
                                    stack.append(linked_face)

                for face in bm.faces:
                    if face.index not in visited:
                        group = []
                        walk_faces(face, group)
                        islands.append(group)

                for island in islands:
                    boundary_edges = set()
                    for face in island:
                        for edge in face.edges:
                            linked_faces = [f for f in edge.link_faces if f in island]
                            if len(linked_faces) == 1:
                                boundary_edges.add(edge)

                    loops = []
                    while boundary_edges:
                        edge = boundary_edges.pop()
                        loop = [edge.verts[0], edge.verts[1]]
                        changed = True
                        while changed:
                            changed = False
                            for e in list(boundary_edges):
                                if loop[-1] in e.verts:
                                    v = e.other_vert(loop[-1])
                                    if v != loop[0]:  # Avoid closing loop early
                                        loop.append(v)
                                        boundary_edges.remove(e)
                                        changed = True
                                        break
                        if loop[0] != loop[-1]:
                            loop.append(loop[0])  # Close the loop
                        loops.append(loop)

                    if loops:
                        path_data = ""
                        for loop in loops:
                            first = True
                            for v in loop:
                                co = mat_world @ v.co
                                p = project(co)
                                update_bounds(p)
                                if first:
                                    path_data += f'M {p[0]:.4f},{p[1]:.4f} '
                                    first = False
                                else:
                                    path_data += f'L {p[0]:.4f},{p[1]:.4f} '
                            path_data += 'Z '
                        svg_lines.append(
                            f'<path d="{path_data.strip()}" fill="#b3b3b3" stroke="none" fill-rule="evenodd"/>'
                        )

                bm.free()
                eval_obj.to_mesh_clear()

            elif obj.type == 'CURVE':
                for spline in obj.data.splines:
                    points = []
                    is_closed = spline.use_cyclic_u
                    if spline.type == 'BEZIER':
                        for bp in spline.bezier_points:
                            co = mat_world @ bp.co
                            p = project(co)
                            points.append(f"{p[0]:.4f},{p[1]:.4f}")
                            update_bounds(p)
                    else:
                        for bp in spline.points:
                            co = mat_world @ bp.co
                            p = project(co)
                            points.append(f"{p[0]:.4f},{p[1]:.4f}")
                            update_bounds(p)
                    if points:
                        tag = "polygon" if is_closed else "polyline"
                        attr = 'fill="#b3b3b3" stroke="none"' if is_closed else 'fill="none" stroke="#b3b3b3" stroke-width="0.2mm" vector-effect="non-scaling-stroke"'
                        svg_lines.append(
                            f'<{tag} points="{" ".join(points)}" {attr}/>'
                        )

        if not svg_lines:
            self.report({'ERROR'}, "No valid geometry in selection")
            return {'CANCELLED'}

        width = max_x - min_x
        height = max_y - min_y

        content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width:.4f}mm" height="{height:.4f}mm"',
            f' viewBox="{min_x:.4f} {min_y:.4f} {width:.4f} {height:.4f}" xmlns:xlink="http://www.w3.org/1999/xlink">'
        ] + svg_lines + ['</svg>']

        with open(self.filepath, 'w') as f:
            f.write('\n'.join(content))

        self.report({'INFO'}, f"Exported {len(objects)} object(s) to {self.filepath}")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "auto_name")

class VIEW3D_PT_svg_export(bpy.types.Panel):
    bl_label = "SVG Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Box Design"
    bl_parent_id = "PT_ExportPanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator(EXPORT_OT_svg_from_selection.bl_idname)

def register():
    bpy.utils.register_class(EXPORT_OT_svg_from_selection)
    bpy.utils.register_class(VIEW3D_PT_svg_export)

def unregister():
    bpy.utils.unregister_class(EXPORT_OT_svg_from_selection)
    bpy.utils.unregister_class(VIEW3D_PT_svg_export)

if __name__ == "__main__":
    register()