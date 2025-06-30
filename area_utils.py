import bpy
import math

def calculate_area_of_selected_object():
    obj = bpy.context.active_object
    if not obj or obj.type not in {'MESH', 'CURVE'}:
        return None
    
    # Lấy đối tượng
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    
    # Chuyển đổi thành lưới (hoạt động cho cả đối tượng Lưới và Đường cong)
    mesh = obj_eval.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    if not mesh:
        return None
    
    # Tính diện tích bằng cách sử dụng tam giác
    mesh.calc_loop_triangles()
    area = 0.0
    for tri in mesh.loop_triangles:
        verts = [obj_eval.matrix_world @ mesh.vertices[i].co for i in tri.vertices]
        a, b, c = verts
        area += ((b - a).cross(c - a)).length / 2.0
    
    # Dọn sạch lưới tạm thời
    obj_eval.to_mesh_clear()
    
    return area
