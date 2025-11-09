import bpy

armature = bpy.data.objects["DeformationSystem"]  # tên armature
driver_bone = "Wrist_R"               # bone điều khiển
driven_bone = "Wrist_L"                # bone bị điều khiển
driver_boneNode = armature.pose.bones[driver_bone]
driver_boneNode.rotation_mode = 'XYZ'
driven_boneNode = armature.pose.bones[driven_bone]
driven_boneNode.rotation_mode = 'XYZ'

# Đảm bảo đang ở Object Mode
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='OBJECT')

# Lấy kênh rotation Z của xương bị điều khiển
fcurve = armature.pose.bones[driven_bone].driver_add('rotation_euler', 2)  # 0=X, 1=Y, 2=Z

# Tạo driver
driver = fcurve.driver
driver.type = 'SCRIPTED'

# Xoá variable cũ nếu có
while driver.variables:
    driver.variables.remove(driver.variables[0])

# Tạo variable mới
var = driver.variables.new()
var.name = 'ctrl'
var.targets[0].id = armature
var.targets[0].data_path = f'pose.bones["{driver_bone}"].rotation_euler[0]'  # X của Controller

# Thiết lập biểu thức điều khiển (ví dụ: nhân hệ số)
driver.expression = 'ctrl * 2.0'  # X xoay 1 radian → Bone_Copy xoay 2 radian trên Z
