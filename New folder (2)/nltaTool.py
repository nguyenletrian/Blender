bl_info = {
    "name":"Sparx Rigging tool",
    "author": "Nguyen Le Tri An",
    "version":(1, 0),
    "blender": (2, 80 ,0),
    "location":"VIEW 3D",    
}

import bpy, math, os, json, functools, datetime,re
from mathutils import Matrix
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

#########
# SESSION
#########
bpy.types.Scene.session = {
    "sourceSideLeft":"",
    "sourceSideRight":"",
    "targetSideLeft":"",
    "targetSideRight":"",
    "scaleExampleArmature":"",
    "scaleExampleBone":"",
    "exportFolder":"",
    "importFile":"",
    "frameMin":0,
    "frameMax":0,
    "armatureSource":"",
    "armatureTarget":"",
    "boneAnimationData":{},
}

##################
# GENERAL FUNCTION
##################

def getDistanceBetween(objFromName,objToName):
    objFrom = bpy.data.objects[objFromName]
    objTo = bpy.data.objects[objToName]
    locationFrom = objFrom.matrix_world.to_translation()
    locationTo = objFrom.matrix_world.to_translation()
    return((locationTo -  locationFrom).length)

def objTypes():
    types = bpy.context.object.bl_rna.properties['type'].enum_items
    for t in types:
        print(f'Type {t.identifier}: {t.name}')

def cleanUp():
    if(bpy.context.active_object):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        
    for item in bpy.data.objects:
        if item.name[0:10] == "temp_Empty":
            bpy.data.objects[item.name]
            bpy.ops.object.delete()
            
def selectedObjs():
    objs = bpy.context.view_layer.objects.active
    if objs:
        returnArray = []
        for obj in objs:
            returnArray.append(obj.name)
        return(returnArray)
    else:
        return(None)            
            
#BONE FUNCTIONS
def getArmature():
    poseBone = bpy.context.active_pose_bone
    return(poseBone.id_data)

def createEmptyFromBone(armatureName,boneName):
    armature = bpy.data.objects[armatureName]
    poseBone = armature.pose.bones[boneName]
    armatureMatrix = armature.matrix_world
    poseBoneMatrix = poseBone.matrix    
    resultMatrix = armatureMatrix @ poseBoneMatrix    
    
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location= (0,0,0), scale=(1, 1, 1))
    empty = bpy.context.selected_objects[0]
    empty.matrix_world = resultMatrix
    return(empty)

def getBoneMatrix(armature,poseBone):
    return(armature.matrix_world @ poseBone.matrix)

"""
def getBoneMatrix(armature,poseBone):
    armature = bpy.data.objects[armatureName]
    bonePose = armature.pose.bones[boneName]
    return(armature.matrix_world @ poseBone.matrix)
"""
def matchBoneToObject(armatureName,boneName,object):
    armature = bpy.data.objects[armatureName]
    poseBone = armature.pose.bones[boneName]
    object = bpy.data.objects[object]
    
    objectMatrix = object.matrix_world
    poseBoneNewMatrix =  armature.matrix_world.inverted() @ objectMatrix
    poseBone.matrix = poseBoneNewMatrix
    poseBone.location.x =20
    
def matchObjectToBone(armatureName,boneName,object):
    armature = bpy.data.objects[armatureName]
    poseBone = armature.pose.bones[boneName]
    object = bpy.data.objects[object]    
    matrixFinal = armature.matrix_world @ poseBone.matrix
    object.matrix_world = matrixFinal

def matchBoneToBone(armatureName1,boneName1,armatureName2,boneName2):
    armature1 = bpy.data.objects[armatureName1]
    poseBone1 = armature1.pose.bones[boneName1]
    armature2 = bpy.data.objects[armatureName2]
    poseBone2 = armature2.pose.bones[boneName2]
    
    poseBone1Matrix = armature1.matrix_world @ poseBone1.matrix
    poseBone2Matrix = armature2.matrix_world.inverted() @ poseBone1Matrix
    poseBone2.matrix = poseBone2Matrix

def boneAutoKeyframe():
    bpy.context.active_pose_bone.rotation_mode = "XYZ"
    bpy.context.active_pose_bone.rotation_euler.rotate_axis("X",math.radians(60))
    bpy.ops.anim.keyframe_insert()


    """
    if myProp.scaleExample!="":
        armatureScene = bpy.data.objects[myProp.scaleExample]
        heightScene = armatureScene.dimensions.y
        armatureFbx = armature
        heightFbx = armatureFbx.dimensions.y
        ratio = (heightScene / heightFbx)/100
        armatureFbx.scale = (ratio,ratio,ratio)
    """

def getBoneKeyframes(data):
    armatureName = data["armatureName"]
    boneName = data["boneName"]
    armature = bpy.data.objects[armature_name]
    action = armature.animation_data.action
    keyframes = {}
    for fcurve in action.fcurves:
        if bone_name in fcurve.data_path:
            keyframes[fcurve.data_path] = [kp.co for kp in fcurve.keyframe_points]
    return keyframes
    
    
def insertKeyframe(data):
    armature = data["armature"]
    data_path = data["data_path"]
    array_index = data["array_index"]
    frame = data["frame"]
    value = data["value"]
    
    armature= bpy.data.objects["Armature"]
    action = armature.animation_data.action
    fcurve = action.fcurves.find(data_path, index=array_index)    
    keyframe = fcurve.keyframe_points.insert(frame=frame,value=value)
    if "interpolation" in data:
        keyframe.interpolation = data["interpolation"]
    if "handle_left" in data:
        keyframe.handle_left = data["handle_left"]
    if "handle_left_type" in data:
        keyframe.handle_left_type = data["handle_left_type"]
    if "handle_right" in data:
        keyframe.handle_right = data["handle_right"]
    if "handle_right_type" in data:
        keyframe.handle_right_type = data["handle_right_type"]

def deleteKeyframe(data):
    armature = data["armature"]
    data_path = data["data_path"]
    array_index = data["array_index"]
    frame = data["frame"]
    
    armature= bpy.data.objects["Armature"]
    action = armature.animation_data.action
    fcurve = action.fcurves.find(data_path, index=array_index)    
    fcurve.keyframe_delete(data_path=data_path,frame=frame)

############
# PROPERTIES
############
class myProperties_PG(bpy.types.PropertyGroup):
    session = bpy.types.Scene.session
    sourceSideRight:bpy.props.StringProperty(name="R",default=session["sourceSideRight"])
    sourceSideLeft:bpy.props.StringProperty(name="L",default=session["sourceSideLeft"])
    targetSideRight:bpy.props.StringProperty(name="R",default=session["targetSideRight"])
    targetSideLeft:bpy.props.StringProperty(name="L",default=session["targetSideLeft"])
    scaleExampleArmature:bpy.props.StringProperty(name="scaleExampleArmature",default=session["scaleExampleArmature"])
    scaleExampleBone:bpy.props.StringProperty(name="scaleExampleBone",default=session["scaleExampleBone"])
    exportFolder: bpy.props.StringProperty(
        name = "Custom Path",
        description = "Choose a directory:",
        subtype = "DIR_PATH",
        default=session["exportFolder"]
    )
    importFile: bpy.props.StringProperty(
        name = "Custom Path",
        description ="Choose a directory:",
        subtype = "FILE_PATH",
        default=session["importFile"]
    )
    
def clearProperty(context):
    myProp = context.scene.myProp
    myProp.sourceSideRight = ""
    myProp.sourceSideLeft = ""
    myProp.targetSideRight = ""
    myProp.targetSideLeft = ""
    myProp.scaleExample = ""
    myProp.exportFolder = ""
    myProp.importFile = ""


###########
# OPERATORS
###########
class loadFbx_OP(bpy.types.Operator, ImportHelper):
    bl_label = "Create Animation"
    bl_idname = "animation.load_fbx"
    file: StringProperty(options={'HIDDEN'})
    filter_glob: StringProperty(options={'HIDDEN'},default='*.fbx')# default='*.jpg;*.jpeg;*.png;*.bmp'
    def invoke(self,context,event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session

        oldCollection = bpy.data.collections.get("NLTACollection")
        if oldCollection:
            for obj in oldCollection.objects:
                bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(oldCollection)
        new_collection = bpy.data.collections.new("NLTACollection")
        bpy.context.scene.collection.children.link(new_collection)
        layer_collection = bpy.context.view_layer.layer_collection.children[new_collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        bpy.ops.import_scene.fbx(filepath = self.filepath)

        armature = [obj for obj in new_collection.objects if obj.type == 'ARMATURE'][0]
        session["armatureSource"] = armature.name
        session["boneAnimationData"] = {
            "boneOrder":[]
        }

        #GET BONE ORDER
        for bone in armature.data.bones:
            session["boneAnimationData"]["boneOrder"].append({
                "source":bone.name,
                "target":""
            })
        return{'FINISHED'}



        #bone name, bone match, mirror, no use      

        
            
        #GET VALUE
        #bpy.data.objects["Lily_Armature"].pose.bones.get("anim_fk_arm_2_L_1").rotation_euler



        #bpy.context.active_pose_bone.location[0] = 0.174317
        

        """
        oldCollection = bpy.data.collections.get("NLTACollection")
        if oldCollection:
            for obj in oldCollection.objects:
                bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(oldCollection)

        bpy.types.Scene.session = session
        """


        """
        #for keyframe in :
            #frame, value = keyframe.co
            #print(f"Frame {frame}: Location X = {value}")
            
            for bone in armature.data.bones:
                print(bone.name)
            #GET KEY MAX
            
            for a in range(len(obj.animation_data.action.fcurves)):
                groupName = obj.animation_data.action.fcurves[a].group.name
                if groupName == ""
                print(obj.animation_data.action.fcurves[a].data_path)
                print(obj.animation_data.action.fcurves[a].keyframe_points)
                for keyframe in obj.animation_data.action.fcurves[a].keyframe_points:
                    frame, value = keyframe.co
                    print(f"Frame {frame}: Location X = {value}")
        """
            
        """
            for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
                print(frame)
                bpy.context.scene.frame_set(frame)

                for bone in armature.data.bones:
                    if bone.name == "spine_1_C_1":
                        print("--------------------")
                        print(bone.name)
                        pose_bone = armature.pose.bones.get(bone.name)
                        x_location = pose_bone.location.x
                        print(x_location)
        """
        """
            for a in range(len(obj.animation_data.action.fcurves)):
                groupName = obj.animation_data.action.fcurves[a].group.name
                if groupName == ""
                print(obj.animation_data.action.fcurves[a].data_path)
                print(obj.animation_data.action.fcurves[a].keyframe_points)
                for keyframe in obj.animation_data.action.fcurves[a].keyframe_points:
                    frame, value = keyframe.co
                    print(f"Frame {frame}: Location X = {value}")
        """
        """
            for keyframe in fcurve.keyframe_points:
                # Get the frame number (x-coordinate of the keyframe)
                frame = keyframe.co[0]
                # Set the scene frame to the current keyframe
                bpy.context.scene.frame_set(frame)
                # Retrieve the object's location at this frame
                location_x = obj.location.x
                print(f"Frame {frame}: X-coordinate = {location_x:.4f}")

            # Get the active pose bone (replace 'my_bone_name' with your bone's name)
            pb = bpy.context.active_pose_bone

            # Set the bone location (for example, along the X-axis)
            pb.location = (1, 0, 0)

            # Insert a keyframe for the bone's location at frame 10
            pb.keyframe_insert("location", frame=10)
        """


        """


        ob = bpy.context.object
        ob.location = (1, 2, 4)  # Set the desired location
        ob.keyframe_insert("location", frame=10)  # Add a keyframe at frame 10
        current_frame = bpy.context.scene.frame_current
        obj = bpy.data.objects['Cube']  # Replace with your object name
        obj.keyframe_insert(data_path='location', frame=0)
        obj.location.z += 5
        obj.keyframe_insert(data_path='location', frame=100)
        bpy.context.scene.frame_set(current_frame)
        """

        #obj = bpy.context.scene.objects.get(obj_name)
        #if obj:
            #obj.select_set(True)  # Select the object

        
        """
        currentObj = bpy.context.active_object
        currentObj.name = "Nguyen le tri an"
        currentObj.keyframe_insert("location",frame=0)
        currentObj.keyframe_insert("rotation_euler",frame=0)
        currentObj.rotation_euler.z = math.radians(0) #math.degrees(radians)
        currentObj.location.z = 2
        currentObj.rotation_euler.z = math.radians(90) #math.degrees(radians)
        currentObj.keyframe_insert("location",frame=60)
        currentObj.keyframe_insert("rotation_euler",frame=60)
        """

class getFbxData_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.get_fbx_data"
    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        armature =bpy.data.objects[session["armatureSource"]]
        action = armature.animation_data.action
        sessionAnimation = bpy.types.Scene.session["boneAnimationData"]
        sessionAnimation["action"] = action.name
        sessionAnimation["animation"] = {}

        curveData = {}
        frameMin = 0
        frameMax = 0
        axis_name = ["X","Y","Z"]
        quat_name = ["W","X","Y","Z"]
        frameArray = []
        for curve in action.fcurves:
            #['__doc__', '__module__', '__slots__', 'array_index', 'auto_smoothing', 'bake', 'bl_rna', 'color', 'color_mode', 'convert_to_keyframes', 'convert_to_samples', 'data_path', 'driver', 'evaluate', 'extrapolation', 'group', 'hide', 'is_empty', 'is_valid', 'keyframe_points', 'lock', 'modifiers', 'mute', 'range', 'rna_type', 'sampled_points', 'select', 'update', 'update_autoflags']

            dataPathArray = curve.data_path.split(".")
            if len(dataPathArray)>1:
                boneName = dataPathArray[1]
                if boneName not in sessionAnimation["animation"]:
                    sessionAnimation["animation"][boneName] = {}

                #GET AXIS       
                curveType = dataPathArray[-1]
                if curveType in ["location","rotation_euler","rotation_quaternion","scale"]:
                    if "quaternion" in curveType:
                        axis = quat_name[curve.array_index]
                    else:
                        axis = axis_name[curve.array_index]
                curveName = curveType+axis

                sessionAnimation["animation"][boneName][curveName] = {
                    "data_path":curve.data_path,
                    "index":curve.array_index,
                }
                        
                keyTime = []
                keyValue = []       
                keyframePoints = curve.keyframe_points
                for keyframe in keyframePoints:
                    frame = int(keyframe.co[0])
                    keyTime.append(frame)
                    keyValue.append(keyframe.co[1])
                    if frame < frameMin:
                        frameMin = frame
                    if frame > frameMax:
                        frameMax = frame

                    if frame not in frameArray:
                        frameArray.append(frame)
                    
                sessionAnimation["animation"][boneName][curveName]["keyTime"]=keyTime
                sessionAnimation["animation"][boneName][curveName]["keyValue"]=keyValue
        sessionAnimation["frameMin"] = frameMin
        sessionAnimation["frameMax"] = frameMax
        sessionAnimation["frameArray"] = sorted(frameArray)

        sessionAnimation["matrixData"] = {}
        for frame in sessionAnimation["frameArray"]:
            bpy.context.scene.frame_set(frame)
            frameData = {}
            for bone in armature.data.bones:
                poseBone = armature.pose.bones[bone.name]
                poseBoneMatrix = getBoneMatrix(armature,poseBone)
                poseBoneMatrixToList = [list(row) for row in poseBoneMatrix]
                frameData[bone.name] = poseBoneMatrixToList
            sessionAnimation["matrixData"][frame] = frameData
        return{'FINISHED'}


class import_OP(bpy.types.Operator):
    bl_label = "Import Data"
    bl_idname = "animation.import_data"
    def execute(self, context):
        myProp = context.scene.myProp
        importFile = myProp.importFile
        with open(importFile, "r") as json_file:
            bpy.types.Scene.session = json.load(json_file)      
        session = bpy.types.Scene.session
        myProp.sourceSideRight = session["sourceSideRight"]
        myProp.sourceSideLeft = session["sourceSideLeft"]
        myProp.targetSideRight = session["targetSideRight"]
        myProp.targetSideLeft = session["targetSideLeft"]
        #myProp.scaleExample = session["scaleExample"]
        myProp.exportFolder = session["exportFolder"]
        myProp.importFile = session["importFile"]
        self.report({'WARNING'}, "Import complete!")
        return{'FINISHED'}

class pastAnimation_OP(bpy.types.Operator):
    bl_label = "Import Data"
    bl_idname = "animation.past_animation"

    type:bpy.props.StringProperty(default='Location, Rotation & Scale')
    def execute(self, context):
        armature1 = bpy.data.objects["DeformationSystem"]
        armature2 = bpy.data.objects["DeformationSystem.001"]
        arrayBones = []
        for bone in armature2.pose.bones.items():#arrayBones
            poseBone1 = armature1.pose.bones[bone[0]]
            poseBone2 = armature2.pose.bones[bone[0]]
            if not poseBone1 or not poseBone2:
                continue
            poseBone1Matrix = armature1.matrix_world @ poseBone1.matrix
            poseBone2Matrix = armature2.matrix_world.inverted() @ poseBone1Matrix
            poseBone2.matrix = poseBone2Matrix            
            bpy.context.view_layer.update()
            deps = bpy.context.evaluated_depsgraph_get()
            deps.update()
            poseBone2.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_current)
            if poseBone2.rotation_mode == 'QUATERNION':
                poseBone2.keyframe_insert(data_path="rotation_quaternion", frame=bpy.context.scene.frame_current)
            else:
                poseBone2.keyframe_insert(data_path="rotation_euler", frame=bpy.context.scene.frame_current)
            poseBone2.keyframe_insert(data_path="scale", frame=bpy.context.scene.frame_current)
        
        
        
        
        
        """
        session = context.scene.session
        armature =  bpy.data.objects[session["armatureTarget"]]
        index = 0

        keyingSet = context.scene.keying_sets_all
        keyingSet.active = keyingSet[self.type]

        animationData = session["boneAnimationData"]
        armatureSource =  bpy.data.objects[session["armatureSource"]]
        armatureTarget =  bpy.data.objects[session["armatureTarget"]]
        
        for frame in animationData["frameArray"]:
            bpy.context.scene.frame_set(frame)
            matrixFrameData = matrixData[frame]
            for order in range(len(animationData['boneOrder'])):
                boneSource = animationData['boneOrder'][order]["source"]
                boneTargetName = animationData['boneOrder'][order]["target"]

                
                if boneTargetName!="":
                    boneTarget = armature.pose.bones[boneTargetName]
                    maxtriBoneData = Matrix(matrixFrameData[boneSource])
                    if boneTarget!="":
                        boneTarget.matrix = maxtriBoneData
                
        
        
        animationData = session["boneAnimationData"]
        for index in range(len(animationData)):
            for order in range(len(animationData["boneOrder"])):
                if animationData["boneOrder"][order]["target"]!="":
                    boneSource = animationData["boneOrder"][order]["source"]
                    boneTargetName = animationData["boneOrder"][order]["target"]
                    boneTarget = armature.pose.bones[boneTargetName]
                    boneTarget.rotation_mode = "XYZ"                    
                    animationData = animationData[index][boneSource]
                    print(animationData)
                    #boneTarget.location.x = animationData["rx"]
                    #boneTarget.location.y = animationData["ry"]
                    #boneTarget.location.z = animationData["rz"]
                    boneTarget.rotation_euler.rotate_axis("X",math.radians(animationData["rx"]))
                    boneTarget.rotation_euler.rotate_axis("Y",math.radians(animationData["ry"]))
                    boneTarget.rotation_euler.rotate_axis("Z",math.radians(animationData["rz"]))
                    boneTarget.keyframe_insert(data_path="rotation_euler",frame=index)
        bpy.context.scene.frame_set(0)
        """

        return{'FINISHED'} 
        #src = armA.pose.bones[src_name]
        #dst = armB.pose.bones[dst_name]
        #dst.rotation_quaternion = src.rotation_quaternion.copy()
        #dst_bone.location = src_bone.location.copy()

        """
        matrixData = animationData["matrixData"]
        for frame in animationData["frameArray"]:
            bpy.context.scene.frame_set(frame)
            matrixFrameData = matrixData[frame]
            for order in range(len(animationData['boneOrder'])):
                boneSource = animationData['boneOrder'][order]["source"]
                boneTargetName = animationData['boneOrder'][order]["target"]
                if boneTargetName!="":
                    boneTarget = armature.pose.bones[boneTargetName]
                    maxtriBoneData = Matrix(matrixFrameData[boneSource])
                    if boneTarget!="":
                        boneTarget.matrix = maxtriBoneData
        return{'FINISHED'}  
        """
        """
        #for frame in range(session["frameMin"],session["frameMax"]):
        for index in range(len(session["boneAnimation"])):
            for order in range(len(session["boneOrder"])):
                if session["boneOrder"][order]["target"]!="":
                    boneSource = session["boneOrder"][order]["source"]
                    boneTargetName = session["boneOrder"][order]["target"]
                    boneTarget = armature.pose.bones[boneTargetName]
                    boneTarget.rotation_mode = "XYZ"                    
                    animationData = session["boneAnimation"][index][boneSource]
                    print(animationData)
                    #boneTarget.location.x = animationData["rx"]
                    #boneTarget.location.y = animationData["ry"]
                    #boneTarget.location.z = animationData["rz"]
                    boneTarget.rotation_euler.rotate_axis("X",math.radians(animationData["rx"]))
                    boneTarget.rotation_euler.rotate_axis("Y",math.radians(animationData["ry"]))
                    boneTarget.rotation_euler.rotate_axis("Z",math.radians(animationData["rz"]))
                    boneTarget.keyframe_insert(data_path="rotation_euler",frame=index)
        bpy.context.scene.frame_set(0)
        """

        """
        for a in range(len(session["boneOrder"])):
            if session["boneOrder"][a]["target"]!="":
                bonePose = session["boneOrder"][a]["target"]
                bonePose.rotation_mode = "XYZ"

                animationData = session["boneAnimation"][index][boneSource]
                print(animationData)
                boneTarget.location.x = session["boneAnimation"][index][boneSource]["px"]
                boneTarget.location.y = session["boneAnimation"][index][boneSource]["py"]
                boneTarget.location.z = session["boneAnimation"][index][boneSource]["pz"]
                boneTarget.rotation_quaternion.x = session["boneAnimation"][index][boneSource]["rx"]
                boneTarget.rotation_quaternion.y = session["boneAnimation"][index][boneSource]["ry"]
                boneTarget.rotation_quaternion.z = session["boneAnimation"][index][boneSource]["rz"]
                #print(boneTarget.rotation_quaternion)
                boneTarget.keyframe_insert(data_path="rotation_euler", frame=frame)
                boneTarget.keyframe_insert(data_path="location", frame=frame)

        for a in range(len(session["boneOrder"])):
            if session["boneOrder"][a]["target"]!="":
                boneTargetName = session["boneOrder"][a]["target"]
                #boneTarget = armature.pose.bones.get(boneTargetName)
                #boneTarget.bone.select = True
                bpy.data.objects[armature.name].data.bones[boneTargetName].select =True                             
                bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP",iterations=30)
                bpy.ops.anim.keyframe_insert_menu(type='__ACTIVE__')
                bpy.data.objects[armature.name].data.bones[boneTargetName].select = False
                #boneTarget.bone.select = False
                        
                #boneTarget.keyframe_insert(data_path="location")
                #bpy.ops.anim.keyframe_insert(data_path="location")
                #boneTarget.bone.select = False
        """


        """
        for frame in range(session["frameMin"],session["frameMax"]):
            bpy.context.scene.frame_set(frame)
            for a in range(len(session["boneOrder"])):
                if session["boneOrder"][a]["target"]!="":
                    boneSource = session["boneOrder"][a]["source"]
                    boneTargetName = session["boneOrder"][a]["target"]
                    for a in armature.pose.bones:
                        clearBone = armature.pose.bones.get(a.name)
                        clearBone.bone.select = False
                    boneTarget = armature.pose.bones.get(boneTargetName)
                    boneTarget.bone.select = True

                    keyingSet = context.scene.keying_sets_all
                    keyingSet.active = keyingSet[self.type]
                    bpy.ops.anim.keyframe_insert()
                    bpy.ops.poselib.create_pose_asset(activate_new_action=True)
                    animationData = session["boneAnimation"][index][boneSource]

                    bpy.ops.anim.keyframe_insert("rotation")
                    bpy.ops.transform.rotate(value=animationData["rx"], orient_axis='X')
                    bpy.ops.transform.rotate(value=animationData["ry"], orient_axis='Y')
                    bpy.ops.transform.rotate(value=animationData["rz"], orient_axis='Z')

                    
                    boneTarget.keyframe_insert(data_path="rotation_euler", frame=frame)
                    boneTarget.keyframe_insert(data_path="location", frame=frame)
                    bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP",iterations=1)


                    boneTarget = armature.pose.bones[boneTargetName]""
                    animationData = session["boneAnimation"][index][boneSource]
                    print(animationData)
                    boneTarget.location.x = session["boneAnimation"][index][boneSource]["px"]
                    boneTarget.location.y = session["boneAnimation"][index][boneSource]["py"]
                    boneTarget.location.z = session["boneAnimation"][index][boneSource]["pz"]
                    boneTarget.rotation_quaternion.x = session["boneAnimation"][index][boneSource]["rx"]
                    boneTarget.rotation_quaternion.y = session["boneAnimation"][index][boneSource]["ry"]
                    boneTarget.rotation_quaternion.z = session["boneAnimation"][index][boneSource]["rz"]
                    #print(boneTarget.rotation_quaternion)
                    boneTarget.keyframe_insert(data_path="rotation_euler", frame=frame)
                    boneTarget.keyframe_insert(data_path="location", frame=frame)



                    for a in armature.pose.bones:
                        clearBone = armature.pose.bones.get(a.name)
                        clearBone.bone.select = False
                    boneTarget = armature.pose.bones.get(boneTargetName)
                    boneTarget.bone.select = True
                    boneTarget.rotation_mode = 'XYZ'
                    currentRotation = boneTarget.rotation_euler
                    differenceData = session["boneAnimation"][index][boneSource]
                    #boneTarget.rotation_euler.rotate_axis('Z', math.radians(angle_degrees))
                    print(differenceData)
                    newX = currentRotation[0] + differenceData["rx"]
                    newY = currentRotation[1] + differenceData["ry"]
                    newZ = currentRotation[2] + differenceData["rz"]
                    print(boneTarget)
                    print("x:"+str(newX))
                    print("y:"+str(newY))
                    print("z:"+str(newZ))
                    bpy.context.object.rotation_euler[0] = newX
                    bpy.context.object.rotation_euler[1] = newY
                    bpy.context.object.rotation_euler[2] = newZ


                    armature_name = "Lily_Armature"
                    bone_name = "spine_1_C_1"
                    bpy.ops.object.mode_set(mode="POSE")
                    bpy.data.objects[armature_name]
                    poseBones = bpy.context.object.pose.bones
                    print(poseBones["spine_1_C_1"].rotation_quaternion.x)


                    #poseBones["spine_1_C_1"].location.y = 0
                    #poseBones["spine_1_C_1"].location.z = 0

                
                #boneSource = session["boneOrder"][a]["source"]
                #boneSourceData = session["boneAnimation"][boneSource][index]
                #boneTarget = session["boneOrder"][a]["target"]

        #index += 1

        bpy.context.active_pose_bone.rotation_quaternion

        armature = bpy.data.objects['Armature']
        bone_name = 'Bone'

        # Select the bone
        bone = armature.pose.bones.get(bone_name)
        if bone:
            bone.bone.select = True

            # Set rotation mode to Euler XYZ
            bone.rotation_mode = 'XYZ'

            # Rotate the bone around the Z-axis (in degrees)
            angle_degrees = 120
            bone.rotation_euler.rotate_axis('Z', math.radians(angle_degrees))

            # Insert a keyframe for the rotation
            bone.keyframe_insert(data_path="rotation_euler", frame=1)

            -----
            #bpy.data.objects["Lily_Armature"].data.bones.active = bpy.data.objects["Lily_Armature"].pose.bones["anim_fk_arm_2_L_1"].bone

        """


        




class export_OP(bpy.types.Operator):
    bl_label = "Import Data"
    bl_idname = "animation.export_data"
    def execute(self, context):
        session = context.scene.session     
        myProp = context.scene.myProp
        session["sourceSideRight"] = myProp.sourceSideRight
        session["sourceSideLeft"] = myProp.sourceSideLeft
        session["targetSideRight"] = myProp.targetSideRight
        session["targetSideLeft"] = myProp.targetSideLeft
        session["scaleExampleArmature"] = myProp.scaleExampleArmature
        session["scaleExampleBone"] = myProp.scaleExampleBone
        session["exportFolder"] = myProp.exportFolder
        session["importFile"] = myProp.importFile
        folder_temp = myProp.exportFolder
        if folder_temp:
            folder_temp = os.path.join(folder_temp, 'nltaDataFolder')
            if not os.path.exists(folder_temp):
                os.makedirs(folder_temp)
            file_path = folder_temp+"/animationData.json"               
            with open(file_path,"w") as json_file:
                json.dump(session,json_file,indent=4)#sort_keys=False
        self.report({'WARNING'}, "Export complete!")
        return{'FINISHED'}

class setPair_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.set_pair"
    boneSource:bpy.props.StringProperty(name="boneSource")
    def execute(self, context):

        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        sourceSideRight = myProp.sourceSideRight
        sourceSideLeft = myProp.sourceSideLeft
        targetSideRight = myProp.targetSideRight
        targetSideLeft = myProp.targetSideLeft

        activeBone = bpy.context.selected_pose_bones_from_active_object
        if activeBone:
            session["armatureTarget"] = bpy.context.active_object.name
            boneSource = self.boneSource
            boneTarget = activeBone[0].name                 
            for a in range(len(session["boneAnimationData"]["boneOrder"])):
                if session["boneAnimationData"]["boneOrder"][a]["source"]==boneSource:
                    session["boneAnimationData"]["boneOrder"][a]["target"] = boneTarget

            if sourceSideLeft!="" and targetSideLeft!="":
                boneSourceMirror = boneSource.replace(sourceSideRight,sourceSideLeft)
                boneTargetMirror = boneTarget.replace(targetSideRight,targetSideLeft)
                for a in range(len(session["boneAnimationData"]["boneOrder"])):
                    if session["boneAnimationData"]["boneOrder"][a]["source"] == boneSourceMirror:
                        session["boneAnimationData"]["boneOrder"][a]["target"] = boneTargetMirror
        else:
            boneSource = self.boneSource
            for a in range(len(session["boneAnimationData"]["boneOrder"])):
                if session["boneAnimationData"]["boneOrder"][a]["source"]==boneSource:
                    session["boneAnimationData"]["boneOrder"][a]["target"] = ""

            if sourceSideLeft!="" and targetSideLeft!="":
                boneSourceMirror = boneSource.replace(sourceSideRight,sourceSideLeft)
                for a in range(len(session["boneAnimationData"]["boneOrder"])):
                    if session["boneAnimationData"]["boneOrder"][a]["source"] == boneSourceMirror:
                        session["boneAnimationData"]["boneOrder"][a]["target"] = ""     
        return{'FINISHED'}

class fixScale_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.fix_scale"
    boneSource:bpy.props.StringProperty(name="boneSource")
    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        armature1Name = myProp.scaleExampleArmature
        bone1Name = myProp.scaleExampleBone
        armature2Name = session["armatureSource"]
        bone2Name = self.boneSource
        empty1 = createEmptyFromBone(armature1Name,bone1Name)
        empty2 = createEmptyFromBone(armature2Name,bone2Name)
        ratio = (empty1.location.z / empty2.location.z)/100
        armature2 = bpy.data.objects[armature2Name]
        armature2.scale = (ratio,ratio,ratio)

        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[empty1.name].select_set(True)
        bpy.data.objects[empty2.name].select_set(True)
        bpy.ops.object.delete()
        return{'FINISHED'}



class deleteFbx_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.delete_fbx"
    def execute(self, context):
        oldCollection = bpy.data.collections.get("NLTACollection")
        if oldCollection:
            for obj in oldCollection.objects:
                bpy.data.objects.remove(obj,do_unlink=True)
            bpy.data.collections.remove(oldCollection)
        return{'FINISHED'}




class reloadScript_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.reload_script"
    def execute(self, context):
        bpy.ops.script.reload()
        clearProperty(context)
        return{'FINISHED'}

class scaleExample_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.scale_example"
    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        armature = bpy.context.active_object.name
        session["armatureTarget"] = armature
        activeBone = bpy.context.selected_pose_bones_from_active_object[0]
        if activeBone:
            myProp.scaleExampleArmature = armature
            myProp.scaleExampleBone = activeBone.name
            session["scaleExampleArmature"] = armature
            session["scaleExampleBone"] = activeBone.name
        else:
            myProp.scaleExampleArmature = ""
            myProp.scaleExampleBone = ""
            session["scaleExampleArmature"] = ""
            session["scaleExampleBone"] = ""

        return{'FINISHED'}

class setMirror_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "animation.set_mirror"
    boneSource:bpy.props.StringProperty()

    def execute(self, context):
        session = bpy.types.Scene.session
        sideRight = context.scene.myProp.sideRight
        sideLeft = context.scene.myProp.sideLeft
        activeBone = bpy.context.selected_pose_bones_from_active_object
        if activeBone:
            boneSource = self.boneSource            
            boneTarget = activeBone[0].name
            if sideRight in boneSource:
                boneSourceMirror = boneSource.replace(sideRight,sideLeft)
            if sideLeft in boneSource:
                print("----")
            for a in range(len(session["boneOrder"])):
                if session["boneOrder"][a]["source"]==boneSource:
                    session["boneOrder"][a]["target"] = boneTarget
        return{'FINISHED'}
        """
        activeBone = bpy.context.selected_pose_bones_from_active_object
        if len(activeBone) != 0:
            boneSource = self.boneSource            
            boneTarget = activeBone[0].name
            for a in range(len(bpy.types.Scene.session["boneOrder"])):
                if bpy.types.Scene.session["boneOrder"][a][0]==boneSource:
                    bpy.types.Scene.session["boneOrder"][a][1] = boneTarget
        else:
            boneSource = self.boneSource
            for a in range(len(bpy.types.Scene.session["boneOrder"])):
                if bpy.types.Scene.session["boneOrder"][a][0]==boneSource:
                    bpy.types.Scene.session["boneOrder"][a][1] = ""         
        return{'FINISHED'}
        """

class createEmpty_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "setup.create_empty"
    def execute(self, context):
        arm = bpy.context.active_object
        cleanUp()
        if arm.type == "ARMATURE":
            for pb in arm.pose.bones:
                obj = bpy.data.objects.new("Empty",None)
                obj.name = "temp_"+obj.name
                obj.empty_display_size = .05
                obj.empty_display_type = "CONE"
                bpy.context.scene.collection.objects.link(obj)
                obj.matrix_world = pb.matrix
        else:
            print("Please select an armature")
        return{'FINISHED'}

class createBone_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "setup.create_bone"
    def execute(self, context):
        arm = bpy.context.active_object
        cleanUp()
        if arm.type == "ARMATURE":   
            bpy.ops.object.mode_set(mode="EDIT",toggle=False)
            obArm = bpy.context.active_object
            ebs = obArm.data.edit_bones
            eb = ebs.new("BoneName")
            eb.head = (0,1,1)
            eb.tail = (0,1,2)
        else:
            print("Please select an armature")
        return{'FINISHED'}


class createBoneAnimtion_OP(bpy.types.Operator):
    bl_label = "Create Animation"
    bl_idname = "setup.create_animation"
    def execute(self, context):
        #bpy.context.scene.objects.active = ob #active object
        #bpy.ops.object.mode_set(mode="OBJECT")
        arm = bpy.context.active_object
        bpy.ops.object.mode_set(mode="POSE",toggle=False)
        cleanUp()
        if arm.type == "ARMATURE":
            #bonePose = bpy.context.selected_bones[0]
            bonePose = arm.pose.bones["anim_fk_arm_1_L_1"]
            if bonePose:
                #bpy.data.objects[armature.name].data.bones[boneTargetName]
                bonePose = arm.pose.bones["anim_fk_arm_1_L_1"]
                bonePose.rotation_mode = "XYZ"
                bonePose.keyframe_insert(data_path="rotation_euler",frame=1)
                bonePose.rotation_euler.rotate_axis("X",math.radians(90))
                bonePose.keyframe_insert(data_path="rotation_euler",frame=20)
                bonePose.rotation_euler.rotate_axis("X",math.radians(-90))
                bonePose.keyframe_insert(data_path="rotation_euler",frame=40)
                bpy.context.scene.frame_set(0)
        else:
            print("Please select an armature")
        return{'FINISHED'}


########
# PANELS
######## 

class mainForm_PT(bpy.types.Panel):
    bl_label = "Sparx*"
    bl_idname = "NLTA.main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Sparx tool'
    def draw(self,context):
        layout = self.layout
        layout.scale_y = 1.6
        layout.scale_x = 0.5
        
class animationUI_PT(bpy.types.Panel):#sub panel
    bl_label = "Rigging tool"
    bl_idname = "NLTA.animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "NLTA.main"
    bl_options = {"DEFAULT_CLOSED"}#DEK WORK
    def draw(self,context): 
        layout = self.layout
        layout.scale_y = 1.6
        myProp = context.scene.myProp
        session = bpy.types.Scene.session

        row = layout.row()
        row.label(text="Source SideFix:")
        row.prop(myProp,"sourceSideRight")
        row.prop(myProp,"sourceSideLeft")

        row = layout.row()
        row.label(text="Target SideFix:")
        row.prop(myProp,"targetSideRight")
        row.prop(myProp,"targetSideLeft")

        row = layout.row()
        row.prop(myProp,"scaleExampleArmature",text="Armature")
        row.prop(myProp,"scaleExampleBone",text="Bone")
        row.operator("animation.scale_example", text="Scale Example")

        row = layout.row()
        row.prop(myProp,"exportFolder")
        row.operator("animation.export_data", text="Export")
        row = layout.row()
        row.prop(myProp,"importFile")
        row.operator("animation.import_data", text="Import")

        row = layout.row(align=True)
        row.operator("animation.load_fbx", text="Load Fbx")
        row.operator("animation.get_fbx_data", text="Get Fbx Data")
        row.operator("animation.delete_fbx", text="Delete Fbx")

        row = layout.row(align=True)
        row.operator("animation.past_animation", text="Past Animation")
        row.operator("animation.reload_script", text="Clear")


        sideRight = myProp.sourceSideRight
        sideLeft = myProp.sourceSideLeft
        if "boneOrder" in session["boneAnimationData"]:
            boneOrder = session["boneAnimationData"]["boneOrder"]
                
            if len(boneOrder)!=0:
                box = layout.box()      
                for a in range(len(boneOrder)):
                    boneName = boneOrder[a]["source"]
                    if sideLeft=="":
                        row = box.row(align=True)
                        row.label(text=boneName)
                        setPairOperator = row.operator("animation.set_pair",text=boneOrder[a]["target"])                    
                        setPairOperator.boneSource = boneName
                        fixScaleOperator = row.operator("animation.fix_scale",icon="FACESEL",text="")
                        fixScaleOperator.boneSource = boneName
                    else:
                        if sideLeft not in boneName:
                            row = box.row(align=True)
                            row.label(text=boneName)
                            setPairOperator = row.operator("animation.set_pair",text=boneOrder[a]["target"])                    
                            setPairOperator.boneSource = boneName
                            fixScaleOperator = row.operator("animation.fix_scale",icon="FACESEL",text="")
                            fixScaleOperator.boneSource = boneName

            #bpy.context.scene.tool_settings.use_keyframe_insert_auto = True


            #bpy.data.objects["Lily_Armature"].data.dones["jaw"].select = True
            #mybone = bpy.context.object.pose.bones["name"]
            #mybone.rotation_mode ="YZX"



            """
            for a in myProperties:
                print(a.value)
            
            row = box.row()
            row.prop(myProperties_PG,"myRandomNumber")
            for a in range(len(bpy.types.Scene.session["boneOrder"])):
                row.prop(myProperties,bpy.types.Scene.session["boneOrder"][a])
            """


            #ops.open_file_browser = True
            """
            layout = self.layout
            layout.scale_y = 1.6
            layout.prop(self,"path")
            
            row = layout.row()
            row.label(text="Match transfrom",icon="CON_TRACKTO")
            row.StringProperty(name="Enter Text",default="")
            #print(context.scene.session)
            #layout.prop(context.scene.session,"path",text="")
            #row = layout.row()
            #row.operator("animation.create_animation",text="Create Animation")
            """

class setupUI_PT(bpy.types.Panel):#sub panel
    bl_label = "Setup tool"
    bl_idname = "NLTA.setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "NLTA.main"
    bl_options = {"DEFAULT_CLOSED"}#DEK WORK
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.operator("setup.create_empty", text="Create Empty")
        row.operator("setup.create_bone", text="Create Bone")
        row = layout.row()
        row.operator("setup.create_animation", text="Create Animation")
        

#####
# RUN
#####

classArray = [  
    myProperties_PG,
    mainForm_PT,
    animationUI_PT,
    setPair_OP,
    setMirror_OP,   
    loadFbx_OP,
    getFbxData_OP,
    deleteFbx_OP,
    import_OP,
    export_OP,
    pastAnimation_OP,
    reloadScript_OP,
    setupUI_PT,
    createEmpty_OP,
    createBone_OP,
    createBoneAnimtion_OP,
    scaleExample_OP,
    fixScale_OP
]

def register():
    for classItem in classArray:
        bpy.utils.register_class(classItem)
    bpy.types.Scene.myProp = bpy.props.PointerProperty(type=myProperties_PG)
    

def unregister():
    for classItem in classArray:
        try:
            bpy.utils.unregister_class(classItem)
        except:pass


if __name__ == "__main__":
    register()