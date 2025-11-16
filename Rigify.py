import bpy

def TurnOnRigify(*arr):
    addonName =  "rigify"
    enabled = addonName in bpy.context.preferences.addons
    if not enabled:
        bpy.ops.preferences.addon_enable(module="rigify")
TurnOnRigify()

def AddHumanRig(*arr):
    bpy.ops.object.armature_human_metarig_add()
    rig = bpy.context.object
    return(rig)

def RenameBone(rig,oldName,newName):
    rig.data.edit_bones[oldName].name = newName


def GeneralRig():
    rig = bpy.context.object 
    rig.select_set(True)
    bpy.ops.pose.rigify_generate() 

def AddRigType(type):
    rig = bpy.context.object
    bones = bpy.context.selected_pose_bones
    for bone in bones:
        rig.pose.bones[bone.name]["rigify_type"] = type
    #AddRigType("spines.basic_spine")
    #AddRigType("spines.super_head")
    
def GetCurrentData():
    rig = bpy.context.object
    print(rig.data["rigify_layers"])
    print(rig.data["rigify_colors"])
    print(rig.data["rigify_colors_lock"])
    print(rig.data["rigify_colors_ui"])

#print(dir(bpy.ops.armature))
attr = [
    'align',
    'assign_to_collection',
    'autoside_names',
    'bone_primitive_add',
    'calculate_roll',
    'click_extrude',
    'collection_add',
    'collection_assign',
    'collection_create_and_assign',
    'collection_deselect',
    'collection_move',
    'collection_remove',
    'collection_remove_unused',
    'collection_select',
    'collection_show_all',
    'collection_unassign',
    'collection_unassign_named',
    'collection_unsolo_all',
    'copy_bone_color_to_selected',
    'delete',
    'dissolve',
    'duplicate',
    'duplicate_move',
    'extrude',
    'extrude_forked',
    'extrude_move',
    'fill',
    'flip_names',
    'hide',
    'metarig_sample_add',
    'move_to_collection',
    'parent_clear',
    'parent_set',
    'reveal',
    'rigify_add_color_sets',
    'rigify_apply_selection_colors',
    'rigify_collection_add_ui_row',
    'rigify_collection_select',
    'rigify_collection_set_ui_row',
    'rigify_color_set_add',
    'rigify_color_set_add_theme',
    'rigify_color_set_remove',
    'rigify_color_set_remove_all',
    'rigify_encode_metarig',
    'rigify_encode_metarig_sample',
    'rigify_upgrade_layers',
    'rigify_use_standard_colors',
    'rigify_validate_layers',
    'roll_clear',
    'select_all',
    'select_hierarchy',
    'select_less',
    'select_linked',
    'select_linked_pick',
    'select_mirror',
    'select_more',
    'select_similar',
    'separate',
    'shortest_path_pick',
    'split',
    'subdivide',
    'switch_direction',
    'symmetrize'
]

def GetAllBoneCollection(armature):
    returnArray = []
    collections = armature.data.collections
    for collection in collections:
        returnArray.append(collection.name)
    return(returnArray)

def CreateBoneCollection(armature,name):
    armature.data.collections.new(name)

def DeleteBoneCollection(armature,name):
    boneCollection = armature.data.collections.get(name)
    if boneCollection:
        armature.data.collections.remove(boneCollection)

def GetCollectionIndexByName(arm,name):
    cols = arm.data.collections
    colIndex = None
    for i,col in enumerate(cols):
        if col.name == name:
            return(i)
    return(None)
    
def DeleteAllCollection(armature):
    collections = armature.data.collections
    for collection in collections:
        DeleteBoneCollection(armature,collection.name)
        
def AssignBoneCollection(armature,colName,bones):
    boneCol = armature.data.collections.get(colName)
    if not boneCol:
        CreateBoneCollection(armature,colName)
    boneCol = armature.data.collections.get(colName)
    for bone in bones:
        boneCol.assign(bone)

def CreateRootCollection():
    armature = bpy.context.active_object    
    CreateBoneCollection(armature,"Root")

def CreateModule(data):
    arm = data["arm"]
    moduleName = data["moduleName"]
    if arm and arm.type == 'ARMATURE' and bpy.context.mode == 'EDIT_ARMATURE':
        bones = [bone for bone in arm.data.edit_bones if bone.select]
        print(bones)
        AssignBoneCollection(arm,moduleName,bones)
"""
DeleteAllCollection(armature)
CreateRootCollection()

CreateModule({
    "arm":bpy.context.active_object,
    "moduleName":"Arm.R",
})

bpy.ops.armature.rigify_collection_select(index=0)
bpy.ops.armature.rigify_collection_set_ui_row(index=0, row=1)
bpy.ops.armature.rigify_collection_select(index=1)
bpy.ops.armature.rigify_collection_set_ui_row(index=1, row=2)
bpy.ops.armature.rigify_collection_select(index=2)
bpy.ops.armature.rigify_collection_set_ui_row(index=2, row=3)
"""

import bpy

arm = bpy.data.objects["Armature"]

# Tạo hoặc lấy text template
if "LabelText" not in bpy.data.objects:
    bpy.ops.object.text_add()
    txt_template = bpy.context.object
    txt_template.name = "LabelText"
else:
    txt_template = bpy.data.objects["LabelText"]

labels = {
    "Bone.001": "L",
    "Bone.002": "R",
}

for bone_name, text in labels.items():

    # duplicate text object
    txt = txt_template.copy()
    txt.data = txt_template.data.copy()
    txt.data.body = text
    bpy.context.collection.objects.link(txt)

    # apply to pose bone
    pb = arm.pose.bones[bone_name]
    pb.custom_shape = txt
    pb.use_custom_shape_bone_size = False
    #pb.custom_shape_scale = 0.1

#CONSTRAINT TEXT TO BONE 
import bpy

arm = bpy.data.objects["Armature"]
bone_name = "hand.L"
txt = bpy.data.objects["LabelText"]

# Copy Location
con = txt.constraints.new(type='COPY_LOCATION')
con.target = arm
con.subtarget = bone_name
con.target_space = 'POSE'
con.owner_space = 'WORLD'