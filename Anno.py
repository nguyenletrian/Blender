import bpy, math, os, json, functools, datetime,re
from mathutils import Matrix
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper





def ActiveObject(obj):
	if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')  
    bpy.ops.object.select_all(action='DESELECT')   
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def ModeObject(obj):
	ActiveObject(obj)
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='OBJECT')

def ModeEdit(obj):
	ActiveObject(obj)
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='EDIT')

def ModePose(obj):
	ActiveObject(obj)
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='POSE')

def GetState():
    objs = [obj for obj in bpy.context.selected_objects]  # lưu tất cả selected objects
    active_obj = bpy.context.view_layer.objects.active      # lưu object active
    mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'  # lưu mode, fallback OBJECT    
    return {
        "objs": objs,
        "active": active_obj,
        "mode": mode
    }

def BackState(data):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')  
    bpy.ops.object.select_all(action='DESELECT')   
    for obj in data["objs"]:
        obj.select_set(True)    
    bpy.context.view_layer.objects.active = data["active"]  
    if data["mode"] != 'OBJECT' and data["active"]:
        bpy.context.view_layer.objects.active = data["active"]
        bpy.ops.object.mode_set(mode=data["mode"])

def ModifyArmParent(arm):
	state = GetCurrentState()

	BackState()

def GeneralRig():
    before = set(bpy.data.objects)
    
    #Build
    rig = bpy.context.object 
    rig.select_set(True)
    bpy.ops.pose.rigify_generate()

    # Danh sách sau khi generate
    after = set(bpy.data.objects)
    new_objects = after - before

    rig = None
    for obj in new_objects:
        if obj.type == 'ARMATURE':
            rig = obj
            break    
    return(rig)

# BONE COLLECTION
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

def AssignBoneCollection(arm,colName,bones):
    boneCol = arm.data.collections.get(colName)
    if not boneCol:        
        CreateBoneCollection(arm,colName)
        boneCol = arm.data.collections.get(colName)
    for bone in bones:
        if isinstance(bone, str):
            boneTemp = arm.data.bones.get(bone)
        else:
            boneTemp = bone
        boneCol.assign(boneTemp)

def CreateRootCollection():
    arm = bpy.context.active_object    
    CreateBoneCollection(arm,"Root")


def GetAllBoneCollection(armature):
    returnArray = []
    collections = armature.data.collections
    for collection in collections:
        returnArray.append(collection.name)
    return(returnArray)
    
def DeleteAllCollection(armature):
    collections = armature.data.collections
    for collection in collections:
        if collection:
            DeleteBoneCollection(armature,collection.name)
        
### ARMATURE
def ApplyTransform(obj):
    oldState = GetState()    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')    
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)    
    BackState(oldState)

def GetAllBone(arm):
    returnData = []
    bones = arm.data.bones
    for bone in bones:
        returnData.append(bone.name)
    return(returnData)

def GetBoneChildren(arm,boneName):
	returnArray = []
	bone = arm.data.bones[boneName]
	children = bone.children
	if children:
		for child in children:
			returnArray.append(child.name)
		return(returnArray)
	return(None)

def BoneParent(arm,parentName,childName):
    state = GetState()
    ModeEdit(arm)
    child = arm.data.edit_bones[childName]
    parent = arm.data.edit_bones[parentName]    
    parent.tail = child.head.copy()
    child.parent = parent
    child.use_connect = True
    
    BackState(state)
    
def BoneParentConnect(arm,boneName):
    state = GetCurrentState()
    ModeEdit(arm)
    bone = arm.data.edit_bones[boneName]
    if bone.parent: 
        bone.use_connect = True    
    BackState(state)
    
def BoneUnParent(arm,boneName):
    state = GetCurrentState()    
	ModeEdit(arm)
    child = arm.data.edit_bones[boneName]
    child.parent = None    
    BackState(state)


def ArmModifyParent(arm):
	bones = GetAllBone(arm)
	for bone in bones:
		children = GetBoneChildren(bone)
		if children!=None and len(children)==1:
			child = children[0]
			BoneParentConnect(arm,boneName)


def GetBonesSelected(arm):
    returnData = []
    selectedBones =  None
    if arm.mode == 'EDIT':
        selectedBones = [b for b in arm.data.edit_bones if b.select]
    elif arm.mode == 'POSE':
        selectedBones = [b for b in arm.pose.bones if b.bone.select]
    if selectedBones:
        for bone in selectedBones:
            returnData.append(bone.name)
    return(returnData)

def ConstraintArmsBone(armSource,armTarget,boneSourceName,boneTargetName):
    boneTarget = armTarget.pose.bones[boneTargetName]
    con = boneTarget.constraints.new(type='COPY_TRANSFORMS')
    con.target = armSource
    con.subtarget = boneSourceName





### RIGIFY
def ClearRigType(arm):
    bones = GetAllBone(arm)
    for bone in bones:
        arm.pose.bones[bone].rigify_type = ""

def TurnOnRigify(*arr):
    addonName =  "rigify"
    enabled = addonName in bpy.context.preferences.addons
    if not enabled:
        bpy.ops.preferences.addon_enable(module="rigify")
TurnOnRigify()

