import bpy

def TurnOnRigify(*arr):
    bpy.ops.preferences.addon_enable(module="rigify")

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
        
def AssignBoneCollection(armature,colName,bones):
    #AssignBoneCollection(obj,"Nguyen Le Tri An",["upper_arm.R"])  
    boneCol = armature.data.collections.get(colName)
    if boneCol:
        for bone in bones:
            boneNode = armature.data.bones.get(bone)
            if boneNode:
                print(boneNode)
                boneCol.assign(boneNode)
                    
obj = bpy.context.active_object