import bpy

# Chọn armature
arm = bpy.data.objects["DeformationSystem"]

# Đảm bảo đang ở Pose Mode
bpy.context.view_layer.objects.active = arm
if arm.mode != 'POSE':
    bpy.ops.object.mode_set(mode='POSE')

# Chọn bone controller (ví dụ: "Hand_CTRL")
pb = arm.pose.bones["Wrist_R"]

# ✅ Tạo thuộc tính IK_FK
if "IK_FK" not in pb:
    pb["IK_FK"] = 0.0  # 0 = FK, 1 = IK

# Cấu hình giao diện slider
ui = pb.id_properties_ui("IK_FK")
ui.update(
    min=0.0,
    max=1.0,
    soft_min=0.0,
    soft_max=1.0,
    description="Chuyển giữa IK (1) và FK (0)"
)

print("✅ Đã tạo property IK_FK trên bone Hand_CTRL")
