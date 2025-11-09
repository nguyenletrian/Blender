import bpy
armature = bpy.data.objects["DeformationSystem"]
poseBone = armature.pose.bones["Hip_R"]
print(poseBone.custom_shape)

"""
bbone_curveinx
bbone_curveinz
bbone_curveoutx
bbone_curveoutz
bbone_custom_handle_end
bbone_custom_handle_start
bbone_easein
bbone_easeout
bbone_rollin
bbone_rollout
bbone_scalein
bbone_scaleout
bbone_segment_index
bbone_segment_matrix
bl_rna
bone
child
children
color
compute_bbone_handles
constraints
custom_shape
custom_shape_rotation_euler
custom_shape_scale_xyz
custom_shape_transform
custom_shape_translation
custom_shape_wire_width
evaluate_envelope
head
ik_linear_weight
ik_max_x
ik_max_y
ik_max_z
ik_min_x
ik_min_y
ik_min_z
ik_rotation_weight
ik_stiffness_x
ik_stiffness_y
ik_stiffness_z
ik_stretch
is_in_ik_chain
length
location
lock_ik_x
lock_ik_y
lock_ik_z
lock_location
lock_rotation
lock_rotation_w
lock_rotations_4d
lock_scale
matrix
matrix_basis
matrix_channel
motion_path
name
parent
rna_type
rotation_axis_angle
rotation_euler
rotation_mode
rotation_quaternion
scale
tail
use_custom_shape_bone_size
use_ik_limit_x
use_ik_limit_y
use_ik_limit_z
use_ik_linear_control
use_ik_rotation_control
"""

"""
import bpy
# Tên object mới
shape_name = "Bone_Circle"

# Xoá object nếu đã tồn tại
if shape_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[shape_name], do_unlink=True)

# Tạo circle mesh
bpy.ops.mesh.primitive_circle_add(vertices=32, radius=0.2, enter_editmode=False, location=(0,0,0))
circle_obj = bpy.context.active_object
circle_obj.name = shape_name

# Tắt hiển thị render (chỉ dùng làm shape)
circle_obj.hide_render = True
circle_obj.show_in_front = True  # để luôn thấy xương

arm = bpy.data.objects["DeformationSystem"]
pb = arm.pose.bones["EyeBrowOuterJoint_R"]

# Gán transform
pb.custom_shape_transform = transform_bone
# Chọn object làm shape (ví dụ một Circle mesh)
circle_obj = bpy.data.objects["Circle"]  # mesh object hình tròn

pb.custom_shape = circle_obj
pb.custom_shape_scale = 1.0  # chỉnh kích thước hiển thị
pb.custom_shape_transform = pb  # nếu muốn offset hoặc rotation thêm
"""