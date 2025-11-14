import bpy

armature = bpy.data.objects["DeformationSystem"]  # thay tên nếu khác
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='EDIT')

for bone in armature.data.bones:
    bone.display_type = 'BBONE'
    bone.bbone_segments = 8
    
# ---- TẠO XƯƠNG COPY ----
source_name = "Ear_L"        # tên xương gốc
copy_name = "Ear_L_Copy"     # tên xương mới

src = armature.data.edit_bones[source_name]
new_bone = armature.data.edit_bones.new(copy_name)

# Match vị trí, hướng, roll
new_bone.head = src.head.copy()
new_bone.tail = src.tail.copy()
new_bone.roll = src.roll
new_bone.parent = src.parent

bpy.ops.object.mode_set(mode='POSE')

# ---- THÊM CONSTRAINT ----
pose_bone = armature.pose.bones[copy_name]
src_bone = armature.pose.bones[source_name]




# Xoá constraint cũ nếu có
for c in pose_bone.constraints:
    pose_bone.constraints.remove(c)

# Copy Location
con_loc = pose_bone.constraints.new('COPY_LOCATION')
con_loc.target = armature
con_loc.subtarget = source_name
con_loc.use_offset = True

# Copy Rotation
con_rot = pose_bone.constraints.new('COPY_ROTATION')
con_rot.target = armature
con_rot.subtarget = source_name
con_loc.use_offset = True

# Copy Scale
con_scl = pose_bone.constraints.new('COPY_SCALE')
con_scl.target = armature
con_scl.subtarget = source_name
con_loc.use_offset = True

bpy.ops.object.mode_set(mode='OBJECT')

print(f"✅ Đã tạo {copy_name} và thêm 3 constraint từ {source_name}")
