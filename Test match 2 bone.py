"""
import bpy

armA = bpy.data.objects["DeformationSystem"]
armB = bpy.data.objects["DeformationSystem.001"]

pb_src = armA.pose.bones["Head_M"]
pb_dst = armB.pose.bones["Head_M"]

# Lấy world matrix của bone nguồn
world_mat_src = armA.matrix_world @ pb_src.matrix

# Chuyển sang local của bone đích
local_mat_dst = armB.matrix_world.inverted() @ world_mat_src

# Gán matrix cho bone đích
pb_dst.matrix = local_mat_dst
"""
"""
import bpy

# ====== CONFIG ======
source_arm_name = "DeformationSystem"
target_arm_name = "DeformationSystem.001"

# Mapping bone nếu tên khác, nếu giống tên thì để trống {}
bone_map = {
    # "source_name": "target_name",
    # ví dụ: "spine01": "spine"
}

# ====== SETUP ======
arm_src = bpy.data.objects[source_arm_name]
arm_tgt = bpy.data.objects[target_arm_name]

# đảm bảo pose mode
bpy.context.view_layer.objects.active = arm_tgt
bpy.ops.object.mode_set(mode='POSE')

# ====== MATCH ALL BONES ======
for tgt_bone_name, tgt_pb in arm_tgt.pose.bones.items():
    print(tgt_bone_name)
    # xác định bone source tương ứng
    src_bone_name = bone_map.get(tgt_bone_name, tgt_bone_name)
    print(src_bone_name)
    if src_bone_name not in arm_src.pose.bones:
        continue

    src_pb = arm_src.pose.bones[src_bone_name]

    # world matrix của bone source
    src_world = arm_src.matrix_world @ src_pb.matrix

    # convert sang local matrix của armature target
    tgt_local = arm_tgt.matrix_world.inverted() @ src_world


    # gán cho bone target
    tgt_pb.matrix = tgt_local

    # ====== CHÈN KEYFRAME NẾU CẦN ======
    # tgt_pb.keyframe_insert(data_path="location")
    # tgt_pb.keyframe_insert(data_path="rotation_quaternion")
    # tgt_pb.keyframe_insert(data_path="scale")

print("✅ Matching completed for all target bones.")
"""

"""
import bpy

source_arm_name = "DeformationSystem"
target_arm_name = "DeformationSystem.001"


arm_src = bpy.data.objects[source_arm_name]
arm_tgt = bpy.data.objects[target_arm_name]

bpy.context.view_layer.objects.active = arm_tgt
bpy.ops.object.mode_set(mode='POSE')

for tgt_bone_name, tgt_pb in arm_tgt.pose.bones.items():
    # Bone tương ứng
    src_pb = arm_src.pose.bones.get(tgt_bone_name)
    if not src_pb:
        continue

    armature1 = bpy.data.objects[armatureName1]
    poseBone1 = armature1.pose.bones[boneName1]
    armature2 = bpy.data.objects[armatureName2]
    poseBone2 = armature2.pose.bones[boneName2]
    
    poseBone1Matrix = armature1.matrix_world @ poseBone1.matrix
    poseBone2Matrix = armature2.matrix_world.inverted() @ poseBone1Matrix
    poseBone2.matrix = poseBone2Matrix
    
    # Lấy world matrix của bone source
    src_world = arm_src.matrix_world @ src_pb.matrix

    # Nếu bone target có parent, trừ parent transform
    if tgt_pb.parent:
        tgt_local = tgt_pb.parent.matrix.inverted() @ src_world
    else:
        tgt_local = arm_tgt.matrix_world.inverted() @ src_world

    tgt_pb.matrix = tgt_local
"""

"""
import bpy

armatureName1 = "DeformationSystem"
armatureName2 = "DeformationSystem.001"
armature1 = bpy.data.objects[armatureName1]
armature2 = bpy.data.objects[armatureName2]
boneName1 ="Spine2_M"
boneName2 ="Spine2_M"
poseBone1 = armature1.pose.bones[boneName1]
poseBone2 = armature2.pose.bones[boneName2]

for bone in ["Root_M","Spine1_M","Spine2_M"]:
    poseBone1Matrix = armature1.matrix_world @ poseBone1.matrix
    poseBone2Matrix = armature2.matrix_world.inverted() @ poseBone1Matrix
    poseBone2.matrix = poseBone2Matrix

"""

import bpy

armatureName1 = "DeformationSystem"
armatureName2 = "DeformationSystem.001"
armature1 = bpy.data.objects[armatureName1]
armature2 = bpy.data.objects[armatureName2]
arrayBones = []
for obj in armature2.pose.bones.items():
    arrayBones.append(obj[0])
#for targetBoneName, targetBone in armature2.pose.bones.items():


array = [
    'Root_M',   
    'Hip_R',
    'Knee_R',
    'Ankle_R',
    'Toes_R',
    'ToesEnd_R',
    'Spine1_M',
    'Spine2_M',
    'Chest_M',
    'Neck_M',
] 
#'Head_M', 'HeadEnd_M', 'Ear_R', 'Glass_M', 'GlassClose_M', 'Teeth_R', 'Ear_L', 'Teeth_L', 'FaceJoint_M', 'EyeJoint_R', 'IrisJoint_R', 'PupilJoint_R', 'EyeJoint_L', 'IrisJoint_L', 'PupilJoint_L', 'EyeLidJoints_M', 'innerLidMainJoint_R', 'upperLidMainJoint_R', 'upperLidMain_R', 'upperLidMain4_R', 'outerLidMainJoint_R', 'lowerLidMain1_R', 'lowerLidMain_R', 'lowerLidMain4_R', 'innerLidMainJoint_L', 'upperLidMainJoint_L', 'upperLidMain_L', 'upperLidMain4_L', 'outerLidMainJoint_L', 'lowerLidMain1_L', 'lowerLidMain_L', 'lowerLidMain4_L', 'LipJoints_M', 'upperLipAJoint_R', 'upperLipBJoint_R', 'upperLipCJoint_R', 'cornerLipJoint_R', 'lowerLipAJoint_R', 'lowerLipBJoint_R', 'lowerLipCJoint_R', 'upperLipAJoint_L', 'upperLipBJoint_L', 'upperLipCJoint_L', 'cornerLipJoint_L', 'lowerLipAJoint_L', 'lowerLipBJoint_L', 'lowerLipCJoint_L', 'CheekBoneJoint_R', 'CheekBoneJoint_L', 'NoseSideJoint_R', 'NoseSideJoint_L', 'NoseBridgeJoint_M', 'NoseCornerJoint_R', 'NoseCornerJoint_L', 'NoseUnderJoint_M', 'FrownBulgeJoint_R', 'FrownBulgeJoint_L', 'SmileBulgeJoint_R', 'SmileBulgeJoint_L', 'CheekJoint_R', 'CheekJoint_L', 'ChinCreaseJoint_M', 'NoseJoint_M', 'NostrilJoint_R', 'NostrilJoint_L', 'EyeBrowInnerJoint_R', 'EyeBrowInnerJoint_L', 'EyeBrowOuterJoint_R', 'EyeBrowOuterJoint_L', 'EyeBrowCenterJoint_M', 'NoseCreaseJoint_M', 'JawJoint_M', 'upperTeethJoint_M', 'lowerTeethJoint_M', 'Tongue0Joint_M', 'Tongue1Joint_M', 'Tongue2Joint_M', 'Tongue3Joint_M', 'Scapula_R', 'Shoulder_R', 'Elbow_R', 'Wrist_R', 'NeckLake_M', 'Pendant_M', 'Scapula_L', 'Shoulder_L', 'Elbow_L', 'Wrist_L', 'Hip_L', 'Knee_L', 'Ankle_L', 'Toes_L', 'ToesEnd_L']

for bone in array:#arrayBones
        poseBone1 = armature1.pose.bones[bone]
        poseBone2 = armature2.pose.bones[bone]
        if not poseBone1 or not poseBone2:
            continue
        poseBone1Matrix = armature1.matrix_world @ poseBone1.matrix
        poseBone2Matrix = armature2.matrix_world.inverted() @ poseBone1Matrix
        poseBone2.matrix = poseBone2Matrix
        poseBone2.keyframe_insert(data_path="location")
"""
for targetBoneName, targetBone in armature2.pose.bones.items():
    sourceBone = armature1.pose.bones.get(targetBoneName)
    if not sourceBone:
        continue
    sourceBoneMatrix = armature1.matrix_world @ sourceBone.matrix
    targetBoneMatrix = armature2.matrix_world.inverted() @ sourceBoneMatrix
    targetBone.matrix = targetBoneMatrix
    
    targetBone.keyframe_insert(data_path="location")
    targetBone.keyframe_insert(data_path="rotation_quaternion")
    targetBone.keyframe_insert(data_path="scale")
"""  
"""
#poseBone1 = armature1.pose.bones[boneName1]
#armature2 = bpy.data.objects[armatureName2]
for targetBoneName, targetBone in armature2.pose.bones.items():
    sourceBone = armature1.pose.bones.get(targetBoneName)
    if not sourceBone:
        continue
    sourceBoneMatrix = armature1.matrix_world @ sourceBone.matrix
    targetBoneMatrix = armature2.matrix_world.inverted() @ sourceBoneMatrix
    targetBone.matrix = targetBoneMatrix
"""