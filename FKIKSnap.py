
# ##### BEGIN GPL LICENSE BLOCK #####

#    EZ Controls Blender Rigging Assistant
#    Copyright (C) 2020 Alexander Mhiko McIvor

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####


import bpy
import mathutils
import math
import bgl
import blf

ikChainBones = []
fkChainBones = []
ikPole = ''
ikTarget = ''
ikAnchor = ''
ikBase = ''
root = ''
armature = ''


class ListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    itemName = bpy.props.StringProperty(
        name="Name",
        description="A name for this item",
        default="Untitled Chain",
        maxlen=50, )

    ikChain_prop = bpy.props.StringProperty(
        name="IK Pole",
        description="IK Pole of the IK constraint",
        default="", )  # Please choose a chain of IK Bones

    fkChain_prop = bpy.props.StringProperty(
        name="Name",
        description="A name for this item",
        default="", )  # Please choose the corresponding FK chain

    ikPole_prop = bpy.props.StringProperty(
        name="IK Pole",
        description="IK Pole of the IK constraint",
        default="",  # Please choose the IK Pole Target
        maxlen=50, )

    ikTarget_prop = bpy.props.StringProperty(
        name="IK Target",
        description="IK Target of the IK constraint",
        default="",  # Please Choose the IK target bone
        maxlen=50, )

    ik_bool = bpy.props.BoolProperty(
        name="IK Pole Target?",
        description="Does IK have a Pole Target",
        default=True)

    foot_bool = bpy.props.BoolProperty(
        name="IK FootRoll Setup?",
        description="Does the IK use a Foot Roll Setup?",
        default=False)

    ArmatureTarget = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target")

    ikfootBase_prop = bpy.props.StringProperty(
        name="IK Foot Base",
        description="IK Control Bone to control the Foot IK",
        default="",
        maxlen=50, )

    ikAnchor_prop = bpy.props.StringProperty(
        name="IK Foot Anchor",
        description="The bone which the foot bone is usually parented to in a traditional Foot Roll Rig",
        default="",
        maxlen=50, )

    rootBone_prop = bpy.props.StringProperty(
        name="Root Bone",
        description="Rig Root bone to parent the controlling IK bone to",
        default="",
        maxlen=50, )


def draw_callback(self, context):
    font_id = 0
    font_idInst = 0
    blf.position(font_id, 15, 45, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, self.bones[0].name)  # " / ".join([b.name for b in self.bones]))
    blf.position(font_idInst, 15, 30, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Select Bone")
    blf.position(font_idInst, 15, 20, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Enter to accept Chain")
    blf.position(font_idInst, 15, 10, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Escape To Cancel")


class poleDrawOperator(bpy.types.Operator):
    bl_idname = "scene.pole_operator"
    bl_label = "Choose IK Pole"
    bl_description = "Choose the Pole Target of the selected IK constraint"

    def modal(self, context, event):
        global ikPole
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            if (len(self.bones) > 0):
                ikPole = self.bones[0].name
            else:
                ikPole = ''
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.ikPole_prop = ikPole
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            global ikPole
            # Empty bones at the beginning
            self.bones = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class AnchorDrawOperator(bpy.types.Operator):
    bl_idname = "scene.anchor_operator"
    bl_label = "Choose IK Anchor Bone"
    bl_description = "Choose the Anchor Bone to which the foot bone is parented to in a traditional IK Foot Roll Rig"

    def modal(self, context, event):
        global ikPole
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            if (len(self.bones) > 0):
                ikAnchor = self.bones[0].name
            else:
                ikAnchor = ''
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.ikAnchor_prop = ikAnchor
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            global ikPole
            # Empty bones at the beginning
            self.bones = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class ikBaseDrawOperator(bpy.types.Operator):
    bl_idname = "scene.ikbase_operator"
    bl_label = "Choose IK Foot Base Controller"
    bl_description = "Choose the Main Controller of the selected IK constraint"

    def modal(self, context, event):
        global ikPole
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            if (len(self.bones) > 0):
                ikBase = self.bones[0].name
            else:
                ikBase = ''
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.ikfootBase_prop = ikBase
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            global ikPole
            # Empty bones at the beginning
            self.bones = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class RootDrawOperator(bpy.types.Operator):
    bl_idname = "scene.chooseroot_operator"
    bl_label = "Choose Root Bone"
    bl_description = "Choose the Armature Root Bone to parent the controlling bone to"

    def modal(self, context, event):
        global root
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            if (len(self.bones) > 0):
                root = self.bones[0].name
            else:
                root = ''
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.rootBone_prop = root
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            global ikPole
            # Empty bones at the beginning
            self.bones = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


# --------------------------------------------------------------------------------------------------------

class ikTargetDrawOperator(bpy.types.Operator):
    bl_idname = "scene.iktarget_operator"
    bl_label = "Choose IK Target"
    bl_description = "Choose the IK Target of the selected IK constraint"

    def modal(self, context, event):
        scene = context.scene
        global ikTarget
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            if (len(self.bones) > 0):
                ikTarget = self.bones[0].name
            else:
                ikTarget = ''
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.ikTarget_prop = ikTarget
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, args, 'WINDOW', 'POST_PIXEL')
            global ikTarget
            # Empty bones at the beginning
            self.bones = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def draw_callback_ik(self, context):
    font_id = 0
    font_idInst = 0
    blf.position(font_id, 15, 45, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, " / ".join([b.name for b in self.bones]))
    blf.position(font_idInst, 15, 30, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Select Bones in order from Last Bone of IK Chain to and including the IK target")
    blf.position(font_idInst, 15, 20, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Enter to accept Chain")
    blf.position(font_idInst, 15, 10, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Escape To Cancel")


class iKDrawOperator(bpy.types.Operator):
    bl_idname = "scene.ikchain_operator"
    bl_label = "Choose IK Bone Chain"
    bl_description = "Choose the IK bone chain that will be used in IKFK snap script"

    def modal(self, context, event):
        global ikChainBones
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            for b in self.bones:
                self.bonenames.append(b.name)
            ikChainBones = self.bonenames
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.ikChain_prop = " / ".join([b for b in ikChainBones])
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_ik, args, 'WINDOW', 'POST_PIXEL')
            global ikChainBones
            # Empty bones at the beginning
            self.bones = []
            self.bonenames = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def draw_callback_fk(self, context):
    font_id = 0
    font_idInst = 0
    blf.position(font_id, 15, 45, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, " / ".join([b.name for b in self.bones]))
    blf.position(font_idInst, 15, 30, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst,
             "Select FK Bones in corresponding order to the chosen IK Chain from the Last bone to and including an FK bone to snap the IK target bone to")
    blf.position(font_idInst, 15, 20, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Enter to accept Chain")
    blf.position(font_idInst, 15, 10, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Escape To Cancel")


class fKDrawOperator(bpy.types.Operator):
    bl_idname = "scene.fkchain_operator"
    bl_label = "Choose FK Bone Chain"
    bl_description = "Choose the FK bone chain that will be used in IKFK snap script"

    def modal(self, context, event):
        global fkChainBones
        scene = context.scene
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'RET':
            for b in self.bones:
                self.bonenames.append(b.name)
            fkChainBones = self.bonenames
            if scene.list_index >= 0 and scene.my_list:
                item = scene.my_list[scene.list_index]
                item.fkChain_prop = " / ".join([b for b in fkChainBones])
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in self.bones if b in context.selected_pose_bones] + [b for b in
                                                                                    context.selected_pose_bones if
                                                                                    b not in self.bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='POSE')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'POSE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_fk, args, 'WINDOW', 'POST_PIXEL')
            global fkChainBones
            # Empty bones at the beginning
            self.bones = []
            self.bonenames = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class BaseToTarget(bpy.types.Operator):
    bl_idname = "scene.basetarget_operator"
    bl_label = "Target as Parent"
    bl_description = "Parent IK Base to IK Target for IKFK Snap"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            arm = item.ArmatureTarget
            return context.object and context.object.type == 'ARMATURE' and len(item.ikTarget_prop) > 0 and len(
                item.ikfootBase_prop) > 0 and len(item.ikAnchor_prop) > 0 and not arm == None

    def execute(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            arm = item.ArmatureTarget
            if arm.pose.bones[item.ikAnchor_prop].parent == arm.pose.bones[item.ikTarget_prop]:
                self.report({'INFO'},
                            'Execution Cancelled, Possible Cycle dependency: Roll System Anchor is currently parented to IK Target instead of Base')
            else:
                if len(item.rootBone_prop) > 0:
                    root = item.rootBone_prop
                else:
                    root = None
                footIKParent(arm, 0, item.ikTarget_prop, item.ikfootBase_prop, item.ikAnchor_prop, root)
        return {'FINISHED'}


class TargetToBase(bpy.types.Operator):
    bl_idname = "scene.targetbase_operator"
    bl_label = "Base as Parent"
    bl_description = "Parent IK Target to IK Base for Foot Roll"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            arm = item.ArmatureTarget
            return context.object and context.object.type == 'ARMATURE' and len(item.ikTarget_prop) > 0 and len(
                item.ikfootBase_prop) > 0 and len(item.ikAnchor_prop) > 0 and not arm == None

    def execute(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            arm = item.ArmatureTarget
            if len(item.rootBone_prop) > 0:
                root = item.rootBone_prop
            else:
                root = None
            footIKParent(arm, 1, item.ikTarget_prop, item.ikfootBase_prop, item.ikAnchor_prop, root)
        return {'FINISHED'}


class IKtoFKButton(bpy.types.Operator):
    bl_idname = "scene.ikfk_operator"
    bl_label = "IK -> FK"
    bl_description = "Snap IK chain to the current FK chain position"
    global ikChainBones, fkChainBones, ikPole, ikTarget,armature

    @classmethod
    def poll(self, context):
        return context.object and context.object.type == 'ARMATURE' and len(ikChainBones) > 0 and len(
            fkChainBones) > 0 and not armature== None

    def execute(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
        arm = item.ArmatureTarget

        if any(i in ikChainBones for i in fkChainBones):
            self.report({'INFO'}, 'Execution Cancelled, selected FK and IK Chains share at least one bone')
        elif len(ikChainBones) != len(fkChainBones):
            self.report({'INFO'}, 'Execution Cancelled, selected FK and IK Chains are not equal in length')
        elif item.ik_bool and not len(item.ikTarget_prop)>0:
            self.report({'INFO'}, 'Execution Cancelled, IK Target missing')
        elif item.foot_bool and not len(item.ikTarget_prop)>0:
            self.report({'INFO'}, 'Execution Cancelled, IK Target missing')
        elif item.ik_bool and not len(item.ikPole_prop)>0:
            self.report({'INFO'}, 'Execution Cancelled, IK Pole missing')
        elif item.foot_bool and not len(item.ikAnchor_prop)>0:
            self.report({'INFO'}, 'Execution Cancelled, IK Anchor to parent IK Target to is missing')
        elif item.foot_bool and not len(item.ikfootBase_prop)>0:
            self.report({'INFO'}, 'Execution Cancelled, IK Base Control missing')
        elif item.ArmatureTarget == None:
            self.report({'INFO'}, 'Execution Cancelled, Armature Target missing')
        else:
            n = len(fkChainBones)
            if len(ikPole) != 0 and item.ik_bool:
                getmidpt(arm, arm.pose.bones[fkChainBones[0]], arm.pose.bones[fkChainBones[n - 2]],
                         arm.pose.bones[ikPole])

            for i in range(len(fkChainBones)):
                otherspaceTest(arm.pose.bones[ikChainBones[i]], arm.pose.bones[fkChainBones[i]])
        return {'FINISHED'}


class StretchToggle(bpy.types.Operator):
    bl_idname = "scene.stretch_operator"
    bl_label = "IK StretchToggle"
    bl_description = "Turn off IK Stretching for the bones in the IK Chain. Necessary for IK to FK snap"
    global ikChainBones

    @classmethod
    def poll(self, context):
        return context.object and context.object.type == 'ARMATURE' and len(ikChainBones) > 0

    def execute(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
        arm = item.ArmatureTarget
        for i in range(len(ikChainBones)):
            ikBone = arm.pose.bones[ikChainBones[i]]
            for i in range(len(ikBone.constraints)):
                if ikBone.constraints[i].type == "IK":
                    if ikBone.constraints[i].use_stretch:
                        ikBone.constraints[i].use_stretch = False
                    else:
                        ikBone.constraints[i].use_stretch = True

        return {'FINISHED'}


class FKtoIKButton(bpy.types.Operator):
    bl_idname = "scene.fkik_operator"
    bl_label = "FK -> IK"
    bl_description = "Snap FK chain to the current IK chain position"
    global ikChainBones, fkChainBones, ikPole, ikTarget,armature

    @classmethod
    def poll(self, context):
        return context.object and context.object.type == 'ARMATURE' and len(ikChainBones) > 0 and len(
            fkChainBones) > 0 and not armature == None

    def execute(self, context):
        scene = context.scene
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
        arm = item.ArmatureTarget

        if any(i in ikChainBones for i in fkChainBones):
            self.report({'INFO'}, 'Execution Cancelled, selected FK and IK Chains share at least one bone')
        elif len(ikChainBones) != len(fkChainBones):
            self.report({'INFO'}, 'Execution Cancelled, selected FK and IK Chains are not equal in length')
        elif item.ik_bool and not len(item.ikTarget_prop) > 0:
            self.report({'INFO'}, 'Execution Cancelled, IK Target missing')
        elif item.foot_bool and not len(item.ikTarget_prop) > 0:
            self.report({'INFO'}, 'Execution Cancelled, IK Target missing')
        elif item.ik_bool and not len(item.ikPole_prop) > 0:
            self.report({'INFO'}, 'Execution Cancelled, IK Pole missing')
        elif item.foot_bool and not len(item.ikAnchor_prop) > 0:
            self.report({'INFO'}, 'Execution Cancelled, IK Anchor to parent IK Target to is missing')
        elif item.foot_bool and not len(item.ikfootBase_prop) > 0:
            self.report({'INFO'}, 'Execution Cancelled, IK Base Control missing')
        elif item.ArmatureTarget == None:
            self.report({'INFO'}, 'Execution Cancelled, Armature Target missing')
        else:
            for i in range(len(fkChainBones)):
                otherspaceTest(arm.pose.bones[fkChainBones[i]], arm.pose.bones[ikChainBones[i]])

        return {'FINISHED'}


def footIKParent(arm, case, foot, IKBase, anchor, root):
    if case == 0:  # Foot for IKFKsnap
        newParent = arm.pose.bones[foot]
        newChild = arm.pose.bones[IKBase]

        matParent = arm.matrix_world @ newParent.matrix

        bpy.ops.object.mode_set(mode='EDIT')

        arm.data.edit_bones[foot].parent = arm.data.edit_bones[root]
        arm.data.edit_bones[IKBase].parent = arm.data.edit_bones[foot]
    elif case == 1:  # Foot for FootRoll
        newParent = arm.pose.bones[IKBase]
        newChild = arm.pose.bones[foot]

        matParent = arm.matrix_world @ newParent.matrix
        bpy.ops.object.mode_set(mode='EDIT')

        arm.data.edit_bones[IKBase].parent = arm.data.edit_bones[root]
        arm.data.edit_bones[foot].parent = arm.data.edit_bones[anchor]

    bpy.ops.object.mode_set(mode='POSE')
    newParent.matrix = arm.matrix_world.inverted() @ matParent
    newChild.matrix_basis = mathutils.Matrix()
    bpy.ops.object.mode_set(mode='POSE')


def otherspaceTest(poseBone, targetBone):
    """Converts to armature space
    """

    mat = targetBone.matrix
    rest = poseBone.bone.matrix_local.copy()
    rest_inv = rest.inverted()
    if poseBone.parent:
        par_mat = poseBone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = poseBone.parent.bone.matrix_local.copy()
    else:
        par_mat = mathutils.Matrix()
        par_inv = mathutils.Matrix()
        par_rest = mathutils.Matrix()
    # Get matrix in bone's current transform space
    smat = rest_inv @ (par_rest @ (par_inv @ mat))
    q = smat.to_quaternion()
    if poseBone.rotation_mode == 'QUATERNION':
        poseBone.rotation_quaternion = q
    elif poseBone.rotation_mode == 'AXIS_ANGLE':
        poseBone.rotation_axis_angle[0] = q.angle
        poseBone.rotation_axis_angle[1] = q.axis[0]
        poseBone.rotation_axis_angle[2] = q.axis[1]
        poseBone.rotation_axis_angle[3] = q.axis[2]
    else:
        poseBone.rotation_euler = q.to_euler(poseBone.rotation_mode)
    poseBone.scale = smat.to_scale()
    if poseBone.bone.use_local_location is True:
        poseBone.location = smat.to_translation()
    else:
        loc = smat.to_translation()
        rest = poseBone.bone.matrix_local.copy()
        if poseBone.bone.parent:
            par_rest = poseBone.bone.parent.matrix_local.copy()
        else:
            par_rest = mathutils.Matrix()
        q = (par_rest.inverted() * rest).to_quaternion()
        poseBone.location = q * loc
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


# -------------------------------------------------------------------------------------------------------------------
def getmidpt(arm, firstIK, LastIK, poleBone):
    a = firstIK.matrix.to_translation()
    b = LastIK.matrix.to_translation()
    c = LastIK.matrix.to_translation() + LastIK.vector

    # Vector of chain root (shoulder) to chain tip (wrist)
    AC = c - a
    # Vector of chain root (shoulder) to second bone's head (elbow)
    AB = b - a  # AC/2

    # Multiply the two vectors to get the dot product
    dot_prod = AB @ AC

    # Find the point on the vector AC projected from point B
    proj = dot_prod / AC.length

    # Normalize AC vector to keep it a reasonable magnitude
    start_end_norm = AC.normalized()

    # Project an arrow from AC projection point to point B
    proj_vec = start_end_norm * proj
    arrow_vec = AB - proj_vec

    arrow_vec *= 2.0
    final_vec = arrow_vec + b

    mat = mathutils.Matrix.Translation(final_vec)
    rest = poleBone.bone.matrix_local.copy()
    rest_inv = rest.inverted()
    if poleBone.parent:
        par_mat = poleBone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = poleBone.parent.bone.matrix_local.copy()
    else:
        par_mat = mathutils.Matrix()
        par_inv = mathutils.Matrix()
        par_rest = mathutils.Matrix()
    # Get matrix in bone's current transform space
    smat = rest_inv @ (par_rest @ (par_inv @ mat))
    if poleBone.bone.use_local_location is True:
        poleBone.location = smat.to_translation()
    else:
        loc = smat.to_translation()
        rest = poleBone.bone.matrix_local.copy()
        if poleBone.bone.parent:
            par_rest = poleBone.bone.parent.matrix_local.copy()
        else:
            par_rest = mathutils.Matrix()
        q = (par_rest.inverted() * rest).to_quaternion()
        poleBone.location = q * loc
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


# --------------------------------------------------------------------------------------------------------

class FKIKSnappingControls(bpy.types.Panel):
    bl_label = "IK FK Snapping"
    bl_idname = "ControlPanel_E"
    bl_space_type = 'VIEW_3D'
    bl_options = {'DEFAULT_CLOSED'}
    bl_region_type = 'UI'
    bl_category = 'EZ Controls'

    def draw(self, context):
        layout = self.layout
        global ikChainBones, fkChainBones, ikPole, ikTarget, root, ikBase, ikAnchor,armature
        scene = context.scene
        row = layout.row()
        row.label(text="Saved IK - FK Chains")
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            if len(item.ikChain_prop) > 0:
                ikChainBones = item.ikChain_prop.split(" / ")
            else:
                ikChainBones = []
            if len(item.fkChain_prop) > 0:
                fkChainBones = item.fkChain_prop.split(" / ")
            else:
                fkChainBones = []
            ikPole = item.ikPole_prop
            ikTarget = item.ikTarget_prop
            ikAnchor = item.ikAnchor_prop
            ikBase = item.ikfootBase_prop
            root = item.rootBone_prop
            armature=item.ArmatureTarget

        layout.template_list("IKFK_List", "The_List", scene, "my_list", scene, "list_index")
        row = layout.row()
        row.operator('my_list.add_item', text='ADD')
        row.operator('my_list.delete_item', text='REMOVE')

        if scene.list_index >= 0 and scene.my_list:
            row = layout.row()
            row.prop(item, "ArmatureTarget")

            box = layout.box()
            row = box.row()
            row.label(text="Set IK FK Values ")
            row = box.row()
            row.operator("scene.ikchain_operator")
            row = box.row()
            row.label(text=" / ".join([b for b in ikChainBones]))

            row = box.row()
            row.operator("scene.fkchain_operator")
            row = box.row()
            row.label(text=" / ".join([b for b in fkChainBones]))

            row = layout.row()
            row.prop(item, "ik_bool")
            row.prop(item, "foot_bool")
            row = layout.row()
            if item.ik_bool:
                box = layout.box()
                row = box.row()
                row.operator("scene.pole_operator")
                row.operator("scene.iktarget_operator")
                row = box.row()
                row.label(text=ikPole)
                row.label(text=ikTarget)
                row = box.row()
            if item.foot_bool:
                box = layout.box()
                row = box.row()
                row.operator("scene.ikbase_operator")
                row.operator("scene.iktarget_operator")
                row = box.row()
                row.label(text=ikBase)
                row.label(text=ikTarget)
                row = box.row()
                row.operator("scene.anchor_operator")
                row.operator("scene.chooseroot_operator")
                row = box.row()
                row.label(text=ikAnchor)
                row.label(text=root)
                row = box.row()

        row = layout.row()
        row.label(text="Commands: ")
        row = layout.row()
        row.operator("scene.fkik_operator")
        row = layout.row()
        row.operator("scene.ikfk_operator")
        row.operator("scene.stretch_operator")
        if item.foot_bool:
            row = layout.row()
            row.operator("scene.targetbase_operator")
            row.operator("scene.basetarget_operator")


class FKIKSnapMenu(bpy.types.Operator):
    bl_label = "IK FK Snapping Quick Menu"
    bl_idname = "wm.snapmenu"

    fkChain_prop: bpy.props.StringProperty(
        name="Name",
        description="A name for this item",
        default="", )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        global ikChainBones, fkChainBones, ikPole, ikTarget, root, ikBase, ikAnchor,armature
        scene = context.scene
        layout.label(text="Saved IK - FK Chains")
        if scene.list_index >= 0 and scene.my_list:
            item = scene.my_list[scene.list_index]
            if len(item.ikChain_prop) > 0:
                ikChainBones = item.ikChain_prop.split(" / ")
            else:
                ikChainBones = []
            if len(item.fkChain_prop) > 0:
                fkChainBones = item.fkChain_prop.split(" / ")
            else:
                fkChainBones = []
            ikPole = item.ikPole_prop
            ikTarget = item.ikTarget_prop
            ikAnchor = item.ikAnchor_prop
            ikBase = item.ikfootBase_prop
            root = item.rootBone_prop
            armature=item.ArmatureTarget

        layout.template_list("IKFK_List", "The_List", scene, "my_list", scene, "list_index")
        row = layout.row()
        row.label(text="Commands: ")
        row = layout.row()
        row.operator("scene.fkik_operator")
        row = layout.row()
        row.operator("scene.ikfk_operator")
        row.operator("scene.stretch_operator")
        if item.foot_bool:
            row = layout.row()
            row.operator("scene.targetbase_operator")
            row.operator("scene.basetarget_operator")


class addListItem(bpy.types.Operator):
    """Add a new item to the list."""
    bl_idname = "my_list.add_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.scene.my_list.add()
        return {'FINISHED'}


class deleteListItem(bpy.types.Operator):
    """Delete the selected item from the list."""
    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        my_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(my_list) - 1)
        return {'FINISHED'}


class IKFK_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "itemName", text="", emboss=False)
            layout.prop(item, "ikChain_prop", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


classes = [IKFK_List, iKDrawOperator, FKIKSnappingControls, IKtoFKButton, FKtoIKButton, StretchToggle,
           fKDrawOperator, poleDrawOperator, ikTargetDrawOperator, ListItem, addListItem, deleteListItem,
           RootDrawOperator, ikBaseDrawOperator, AnchorDrawOperator, BaseToTarget, TargetToBase, FKIKSnapMenu]

addon_keymaps = []


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError:
            pass
    bpy.types.Scene.my_list = bpy.props.CollectionProperty(type=ListItem)
    bpy.types.Scene.list_index = bpy.props.IntProperty(name="Name Chosen for saved IKFK Chain set", default=0)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.snapmenu', type='O', value='PRESS', shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    try:
        del bpy.types.Scene.my_list
        del bpy.types.Scene.list_index
    except RuntimeError:
        pass
    for cls in classes:
        try:
            for km, kmi in addon_keymaps:
                km.keymap_items.remove(kmi)
            addon_keymaps.clear()
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


