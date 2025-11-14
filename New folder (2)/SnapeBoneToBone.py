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

class pastAnimation_OP(bpy.types.Operator):
    bl_label = "Import Data"
    bl_idname = "animation.past_animation"

    type:bpy.props.StringProperty(default='Location, Rotation & Scale')
    def execute(self, context):
        armature1 = bpy.data.objects["DeformationSystem"]
        armature2 = bpy.data.objects["DeformationSystem.001"]
        animationRange = GetAnimationRange(armature1)
        for i in range(animationRange['min'],animationRange['max']):
            bpy.context.scene.frame_set(i)
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
        row = layout.row(align=True)
        row.operator("animation.past_animation", text="Past Animation")

classArray = [  
    mainForm_PT,
    pastAnimation_OP,
]

def register():
    for classItem in classArray:
        bpy.utils.register_class(classItem)
    

def unregister():
    for classItem in classArray:
        try:
            bpy.utils.unregister_class(classItem)
        except:pass


if __name__ == "__main__":
    register()