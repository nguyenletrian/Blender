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

def GetAnimationRange(armature):
    action = armature.animation_data.action
    frameMin = 0
    frameMax = 0
    for curve in action.fcurves:
        dataPathArray = curve.data_path.split(".")
        if len(dataPathArray)>1:
            keyframePoints = curve.keyframe_points
            for keyframe in keyframePoints:
                frame = int(keyframe.co[0])
                if frame < frameMin:
                    frameMin = frame
                if frame > frameMax:
                    frameMax = frame
    return({"min":frameMin,"max":frameMax})

bpy.types.Scene.session = {
    "sourceArmature":"",
    "targetArmature":"",
}

class myProperties_PG(bpy.types.PropertyGroup):
    session = bpy.types.Scene.session
    sourceArmature:bpy.props.StringProperty(name="sourceArmature",default=session["sourceArmature"])
    targetArmature:bpy.props.StringProperty(name="targetArmature",default=session["sourceArmature"])

class pickSource_OP(bpy.types.Operator):
    bl_label = "Pick Source"
    bl_idname = "animation.pick_source"
    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        
        armature = bpy.context.active_object.name
                
        session["sourceArmature"] = armature
        myProp.sourceArmature = armature
            
        return{'FINISHED'}

class pickTarget_OP(bpy.types.Operator):
    bl_label = "Pick Target"
    bl_idname = "animation.pick_target"
    def execute(self, context):
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        
        armature = bpy.context.active_object.name
                
        session["targetArmature"] = armature
        myProp.targetArmature = armature
            
        return{'FINISHED'}
    

class pastAnimation_OP(bpy.types.Operator):
    bl_label = "Import Data"
    bl_idname = "animation.past_animation"

    type:bpy.props.StringProperty(default='Location, Rotation & Scale')
    def execute(self, context):
        session["sourceArmature"]
        armatureSource = bpy.data.objects["Armature.001"]
        armatureTarget = bpy.data.objects["Armature"]
        animationRange = GetAnimationRange(armatureSource)
        for i in range(animationRange['min'],animationRange['max']):
            bpy.context.scene.frame_set(i)
            for bone in armatureTarget.pose.bones.items():#arrayBones
                boneSource = armatureSource.pose.bones[bone[0]]
                boneTarget = armatureTarget.pose.bones[bone[0]]
                if not boneSource or not boneTarget:
                    continue
                boneSourceMatrix = armatureSource.matrix_world @ boneSource.matrix
                boneTargetMatrix = armatureTarget.matrix_world.inverted() @ boneSourceMatrix
                boneTarget.matrix = boneTargetMatrix        
                bpy.context.view_layer.update()
                deps = bpy.context.evaluated_depsgraph_get()
                deps.update()
                boneTarget.keyframe_insert(data_path="location", frame=i)
                if boneTarget.rotation_mode == 'QUATERNION':
                    boneTarget.keyframe_insert(data_path="rotation_quaternion", frame=i)
                else:
                    boneTarget.keyframe_insert(data_path="rotation_euler", frame=i)
                boneTarget.keyframe_insert(data_path="scale", frame=i)
        return{'FINISHED'}
        
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
        
        myProp = context.scene.myProp
        session = bpy.types.Scene.session
        
        row = layout.row()
        row.prop(myProp,"sourceArmature")
        row.operator("animation.pick_source", text="Pick Source")
        
        row = layout.row()
        row.prop(myProp,"targetArmature")
        row.operator("animation.pick_target", text="Pic Target")
        
        row = layout.row(align=True)
        row.operator("animation.past_animation", text="Past Animation")




classArray = [
    myProperties_PG,
    mainForm_PT,    
    pickSource_OP,
    pickTarget_OP,
    pastAnimation_OP,
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