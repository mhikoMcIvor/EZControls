
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
import bgl
import blf
import mathutils
import math
from .WidgetValues import *
from . import addon_updater_ops

#-----------------------------------------------------------------------------------------------------------------------------

#Variables and Settings
#Was necessary to use a different list for each execution so that each panel could only undo its own last execution
lastbones = []
new_bones = []
og_bones = []
chain_bones = []
lastChain_bones = []
existingboneSetup = []
#-----------------------------------------------------------------------------------------------------------------------------


class MySettings(bpy.types.PropertyGroup):

    def_bool = bpy.props.BoolProperty(
        name="Deform?",
        description=" A bool property",
        default=False)

    inh_bool = bpy.props.BoolProperty(
        name="Copy Constraints from Original?",
        description=" A bool property",
        default=False)

    name_enum = bpy.props.EnumProperty(
        name="Name Method",
        description="Set how the new bones will be named",
        items=[('OP1', "Find/Replace", ""),
               ('OP2', "Add Prefix", ""),
               ('OP3', "Add Suffix", ""),
               ]
    )

    find_string = bpy.props.StringProperty(
        name="Find",
        description="Replaceable String to find",
        default="",
        maxlen=50, )

    pref_string = bpy.props.StringProperty(
        name="Name",
        description="String to add to bones",
        default="",
        maxlen=50, )

    "-------------------------------------------------------------------------------------------------------------------------"

    "Variables for a single property path Driver"

    "-------------------------------------------------------------------------------------------------------------------------"

    ArmatureTarget = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Target")

    PropTarget = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Prop")

    drivInv_bool = bpy.props.BoolProperty(
        name="Invert Driver",
        description="Invert Driver modifier so that when property is 0, driver is 1 and driver is 0 when property is 1",
        default=False)

    driv_bool = bpy.props.BoolProperty(
        name="Set Driver?",
        description=" A bool property",
        default=False)

    drivpath_string = bpy.props.StringProperty(
        name="Path",
        description=":",
        default="",
        maxlen=1024, )

    "-------------------------------------------------------------------------------------------------------------------------"

    "Constraint variables"

    "-------------------------------------------------------------------------------------------------------------------------"

    ScalePower_float = bpy.props.FloatProperty(
        name="Power",
        description="Raise the target's scale to the specified power",
        default=1.000,
    )

    ScaleUniform_bool = bpy.props.BoolProperty(
        name="Make Uniform",
        description="Redistribute the copied change in volume equally between the three axes of the owner.",
        default=False)

    ScaleAdditive_bool = bpy.props.BoolProperty(
        name="Additive",
        description="Use addition instead of multiplication to combine scale (2.7 compatibility)",
        default=False)

    RotationMix_enum = bpy.props.EnumProperty(
        name="Mix",
        description="Specify how the copied and existing rotations are combined",
        items=[('OP1', "Replace", ""),
               ('OP2', "Add", ""),
               ('OP3', "Before Original", ""),
               ('OP4', "After Original", ""),
               ('OP5', "Offset(Legacy)", ""),
               ]
    )

    RotationOrder_enum = bpy.props.EnumProperty(
        name="Euler Order",
        description="Explicitly specify the Euler Rotation Order",
        items=[('OP1', "Default", ""),
               ('OP2', "XYZ Euler", ""),
               ('OP3', "XZY Euler", ""),
               ('OP4', "YXZ Euler", ""),
               ('OP5', "YZX Euler", ""),
               ('OP6', "ZXY Euler", ""),
               ('OP7', "ZYX Euler", ""),
               ]
    )

    TranslationMix_enum = bpy.props.EnumProperty(
        name="Mix",
        description="Specify how the copied and existing transformations are combined",
        items=[('OP1', "Replace", ""),
               ('OP2', "Before Original", ""),
               ('OP3', "After Original", ""),
               ]
    )

    offset_bool = bpy.props.BoolProperty(
        name="Offset",
        description="Combine value of original to the copied value",
        default=True)

    "-------------------------------------------------------------------------------------------------------------------------"

    "Shared Constraint variables"

    "-------------------------------------------------------------------------------------------------------------------------"

    constraint_enum = bpy.props.EnumProperty(
        name="Armature Constraint ",
        description="Applied Constraint to Original Armature",
        items=[('OP1', "COPY LOCATION", ""),
               ('OP2', "COPY ROTATION", ""),
               ('OP3', "COPY SCALE", ""),
               ('OP4', "COPY TRANSFORMATIONS", ""),
               ]
    )

    x_bool = bpy.props.BoolProperty(
        name="X",
        description=" X value of constraint",
        default=True)

    xInv_bool = bpy.props.BoolProperty(
        name="Invert",
        description=" Invert X value of constraint",
        default=False)

    y_bool = bpy.props.BoolProperty(
        name="Y",
        description=" X value of constraint",
        default=True)

    yInv_bool = bpy.props.BoolProperty(
        name="Invert",
        description=" Invert Y value of constraint",
        default=False)

    z_bool = bpy.props.BoolProperty(
        name="Z",
        description=" Z value of constraint",
        default=True)

    zInv_bool = bpy.props.BoolProperty(
        name="Invert",
        description=" Invert Z value of constraint",
        default=False)

    influence_float = bpy.props.FloatProperty(
        name="Influence",
        description="Amount of influence constraint will have on final solution",
        default=1.000,
        min=0.000,
        max=1.000
    )

    SpaceTarget_enum = bpy.props.EnumProperty(
        name="Target Space ",
        description="Space that Target is evaluated in",
        items=[('OP1', "World Space", ""),
               ('OP2', "Pose Space", ""),
               ('OP3', "Local with Parent", ""),
               ('OP4', "Local Space", ""),
               ]
    )

    SpaceOwner_enum = bpy.props.EnumProperty(
        name="Owner Space ",
        description="Space that Owner is evaluated in",
        items=[('OP1', "World Space", ""),
               ('OP2', "Pose Space", ""),
               ('OP3', "Local with Parent", ""),
               ('OP4', "Local Space", ""),
               ]
    )

    "-------------------------------------------------------------------------------------------------------------------------"

    "Shape Variables"

    "-------------------------------------------------------------------------------------------------------------------------"

    shape_size = bpy.props.FloatProperty(
        name="Size",
        description="Size of Generated Shape",
        default=1.0,
        min=-5,
        max=100)

    shape_enum = bpy.props.EnumProperty(
        name="Shape",
        description="Generate a custom bone shape",
        items=[('OP1', "Arrow", ""),
               ('OP2', "Arrow Wireframe", ""),
               ('OP3', "Double-Sided Arrow", ""),
               ('OP4', "Double-Sided Arrow Wireframe", ""),
               ('OP5', "Tripple-Sided Arrow", ""),
               ('OP6', "Tripple-Sided Arrow Wireframe", ""),
               ('OP7', "Quad-Sided Arrow", ""),
               ('OP8', "Quad-Sided Arrow Wireframe", ""),
               ('OP9', "Left-Curved Arrow", ""),
               ('OP10', "Left-Curved Arrow Wireframe", ""),
               ('OP11', "Right-Curved Arrow", ""),
               ('OP12', "Right-Curved Arrow Wireframe", ""),
               ('OP13', "Circle", ""),
               ('OP14', "Square", ""),
               ('OP15', "Cube", ""),
               ('OP16', "Cube Wireframe", ""),
               ('OP17', "Compass", ""),
               ('OP18', "Sphere", ""),
               ('OP19', "Diamond", ""),
               ('OP20', "Diamond Wireframe", ""),
               ('OP21', "Head Control", ""),
               ('OP22', "Arm FK", ""),
               ('OP23', "Hand FK", ""),
               ('OP24', "Finger FK", ""),
               ('OP25', "Foot FK", ""),
               ('OP26', "Foot IK", ""),
               ('OP27', "Boot Toe FK", ""),
               ]
    )


""""-------------------------------------------------------------------------------------------------------------------------------------------------

Constraint Functions

-------------------------------------------------------------------------------------------------------------------------------------------------"""


def checkforDrivers(path, settings):
    propList = []
    bones = settings.ArmatureTarget.pose.bones
    for obj in bones:
        if len(obj.keys()) > 1:
            for K in obj.keys():
                if K not in '_RNA_UI':
                    #makes a list of paths for all pose bone custom properties
                    propList.append(str('"pose.bones["' + obj.name + '"]["' + K + '"]"'))

    #Checks to see if User's entered Driver Path is amongst the list and returns False if it isn't
    if any(path in s for s in propList):
        return True
    else:
        return False


def changeLayers(settings):
    bones_selected = bpy.context.selected_bones
    all_Bones = settings.ArmatureTarget.data.edit_bones
    # Find what layers have bones on them
    active_layers = []
    for bone in all_Bones:
        for i in range(len(bone.layers)):
            if bone.layers[i]:
                if i not in active_layers:
                    active_layers.append(i)

    active_layers.sort()
    #Boolean to check if an empty Layer Found
    nextlayerFound = False
    if (len(active_layers) > 1):
        for i in range(len(active_layers) - 1):
            #If there is a gap between a listed layer with Bones in it and the next layer in the list then we have found the next available layer
            if ((active_layers[i] + 1) != active_layers[i + 1] and not nextlayerFound) :
                nextlayerFound = True
                nextlayer = i + 1
    else:
        #if there is only 1 layer with bones then we simply set the next layer as our next available layer
        nextlayerFound = True
        nextlayer = 1

    if not (nextlayerFound):
        nextlayer = active_layers[(len(active_layers) - 1)] + 1

    if (nextlayer >= 32):
        nextlayer = 0
    new_Layer = [n == nextlayer for n in range(0, 32)]#Sets all other layers except the next available layer as false

    for bone in bones_selected:
        bone.layers = new_Layer#assign each bone the new layer set up where it is only present in the chosen layer
    bpy.context.object.data.layers = new_Layer



def setConstraints(settings, new_bones, original_bones):
    """Takes the settings entered in the UI panels to set constraints in the armature pose mode. Function is called by both new and existing chain constraint executions """
    bpy.ops.object.mode_set(mode='POSE')
    arm = settings.ArmatureTarget
    for i in range(0, len(original_bones)):
        controller = arm.pose.bones.get(original_bones[i])
        target = (new_bones[i])
        if controller:
            if (settings.constraint_enum == 'OP1'):
                crc = controller.constraints.new(type='COPY_LOCATION')
                crc.use_offset = settings.offset_bool
                crc.use_x = settings.x_bool
                crc.use_y = settings.y_bool
                crc.use_z = settings.z_bool
                crc.invert_x = settings.xInv_bool
                crc.invert_y = settings.yInv_bool
                crc.invert_z = settings.zInv_bool
            elif (settings.constraint_enum == 'OP2'):
                crc = controller.constraints.new(type='COPY_ROTATION')
                crc.use_x = settings.x_bool
                crc.use_y = settings.y_bool
                crc.use_z = settings.z_bool
                crc.invert_x = settings.xInv_bool
                crc.invert_y = settings.yInv_bool
                crc.invert_z = settings.zInv_bool

                if (settings.RotationMix_enum == 'OP1'):
                    crc.mix_mode = 'REPLACE'
                elif (settings.RotationMix_enum == 'OP2'):
                    crc.mix_mode = 'ADD'
                elif (settings.RotationMix_enum == 'OP3'):
                    crc.mix_mode = 'BEFORE'
                elif (settings.RotationMix_enum == 'OP4'):
                    crc.mix_mode = 'AFTER'
                elif (settings.RotationMix_enum == 'OP5'):
                    crc.mix_mode = 'OFFSET'

                if (settings.RotationOrder_enum == 'OP1'):
                    crc.euler_order = 'AUTO'
                elif (settings.RotationOrder_enum == 'OP2'):
                    crc.euler_order = 'XYZ'
                elif (settings.RotationOrder_enum == 'OP3'):
                    crc.euler_order = 'XZY'
                elif (settings.RotationOrder_enum == 'OP4'):
                    crc.euler_order = 'YXZ'
                elif (settings.RotationOrder_enum == 'OP5'):
                    crc.euler_order = 'YZX'
                elif (settings.RotationOrder_enum == 'OP6'):
                    crc.euler_order = 'ZXY'
                elif (settings.RotationOrder_enum == 'OP7'):
                    crc.euler_order = 'ZYX'

            elif (settings.constraint_enum == 'OP3'):
                crc = controller.constraints.new(type='COPY_SCALE')
                crc.use_x = settings.x_bool
                crc.use_y = settings.y_bool
                crc.use_z = settings.z_bool
                crc.power = settings.ScalePower_float
                crc.use_make_uniform = settings.ScaleUniform_bool
                crc.use_offset = settings.offset_bool
                crc.use_add = settings.ScaleAdditive_bool
            elif (settings.constraint_enum == 'OP4'):
                crc = controller.constraints.new(type='COPY_TRANSFORMS')
                if (settings.TranslationMix_enum == 'OP1'):
                    crc.mix_mode = 'REPLACE'
                elif (settings.TranslationMix_enum == 'OP2'):
                    crc.mix_mode = 'BEFORE'
                elif (settings.TranslationMix_enum == 'OP3'):
                    crc.mix_mode = 'AFTER'
            crc.target = arm
            crc.subtarget = target
            crc.influence = settings.influence_float

            if (settings.SpaceOwner_enum == 'OP1'):
                crc.owner_space = 'WORLD'
            elif (settings.SpaceOwner_enum == 'OP2'):
                crc.owner_space = 'POSE'
            elif (settings.SpaceOwner_enum == 'OP3'):
                crc.owner_space = 'LOCAL_WITH_PARENT'
            elif (settings.SpaceOwner_enum == 'OP4'):
                crc.owner_space = 'LOCAL'

            if (settings.SpaceTarget_enum == 'OP1'):
                crc.target_space = 'WORLD'
            elif (settings.SpaceTarget_enum == 'OP2'):
                crc.target_space = 'POSE'
            elif (settings.SpaceTarget_enum == 'OP3'):
                crc.target_space = 'LOCAL_WITH_PARENT'
            elif (settings.SpaceTarget_enum == 'OP4'):
                crc.target_space = 'LOCAL'


def setDriver(settings, original_bones):
    driverBones = []
    arm = settings.ArmatureTarget
    for i in range(0, len(original_bones)):
        print(str(arm.pose.bones.get(original_bones[i])))
        driverBones.append(arm.pose.bones.get(original_bones[i]))

    for bone in driverBones:
        if (len(bone.constraints) - 1 >= 0):
            const = bone.constraints[len(bone.constraints) - 1]
            newDrive = const.driver_add('influence').driver
            newDrive.type = 'SCRIPTED'
            var = newDrive.variables.new()
            var.name = 'var_driver'
            var.type = 'SINGLE_PROP'
            target = var.targets[0]
            target.id = arm
            target.data_path = settings.drivpath_string
            if settings.drivInv_bool:
                newDrive.expression = ("1-" + var.name)
            else:
                newDrive.expression = var.name


def clearconstraints(settings, bones):
    bpy.ops.object.mode_set(mode='POSE')
    arm = settings.ArmatureTarget
    for i in range(0, len(bones)):
        controller = arm.pose.bones.get(bones[i])
        if controller:
            if len(controller.constraints) > 0:
                for c in controller.constraints:
                    controller.constraints.remove(c)
    bpy.ops.object.mode_set(mode='EDIT')


class RootControls(bpy.types.Operator):
    bl_idname = "scene.root_operator"
    bl_label = "Add Root Bone"

    @classmethod
    def poll(self, context):
        settings = context.scene.my_tool
        if (not settings.ArmatureTarget == None):
            return True
        else:
            return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        settings = context.scene.my_tool
        arm = settings.ArmatureTarget
        root_bone = arm.data.edit_bones.new("Root")
        root_bone.head = (0, 0, 0)
        root_bone.tail = (0, 1, 0)
        root_bone.roll = 0
        rootname = root_bone.name
        arm.data.edit_bones[rootname].select = True
        changeLayers(settings)
        # Get a list of all the bones in the armature
        bones = [bone.name for bone in arm.data.bones]
        bpy.ops.object.mode_set(mode='EDIT')

        # Parent any free-floating bones to the root.
        for bone in bones:
            if arm.data.edit_bones[bone].parent is None:
                arm.data.edit_bones[bone].use_connect = False
                arm.data.edit_bones[bone].parent = arm.data.edit_bones[rootname]
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


"""
---------------------------------------------------------------------------------------------------------------------------------------------------------------

Chain Selection Code

---------------------------------------------------------------------------------------------------------------------------------------------------------------
"""


def draw_callback_px(self, context):
    #used to make the text on the bottom left of the view port when selecting bone chains, as well as the instructions
    font_id = 0
    font_idInst = 0
    blf.position(font_id, 15, 45, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, " / ".join([b.name for b in self.bones]))
    blf.position(font_idInst, 15, 30, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Select Bones in chosen order from Child to Parent")
    blf.position(font_idInst, 15, 20, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Enter to accept Chain")
    blf.position(font_idInst, 15, 10, 0)
    blf.size(font_idInst, 10, 72)
    blf.draw(font_idInst, "Press Escape To Cancel")


class singleChainOperator(bpy.types.Operator):
    bl_idname = "scene.singlechain_operator"
    bl_label = "Create Single Rotation Chain "
    bl_description = "Create a Single Chain of Rotations. Useful for tails, fingers, curtains. Requires you to select a Bone Chain"

    @classmethod
    def poll(self, context):
        global chain_bones
        #Check to make sure at least one bone has been selected, otherwise lock button to avoid user error
        if (len(chain_bones) > 0):
            return True
        else:
            return False

    def execute(self, context):
        global chain_bones
        global lastChain_bones
        settings = context.scene.my_tool
        bpy.ops.object.mode_set(mode='POSE')
        arm = settings.ArmatureTarget
        lastChain_bones = chain_bones
        if len(chain_bones) > 1:
            for i in range(1, len(chain_bones)):
                controller = arm.pose.bones.get(chain_bones[i])
                target = (chain_bones[i - 1])
                if controller:
                    crc = controller.constraints.new(type='COPY_ROTATION')
                    crc.use_x = settings.x_bool
                    crc.use_y = settings.y_bool
                    crc.use_z = settings.z_bool
                    crc.invert_x = settings.xInv_bool
                    crc.invert_y = settings.yInv_bool
                    crc.invert_z = settings.zInv_bool

                    if (settings.RotationMix_enum == 'OP1'):
                        crc.mix_mode = 'REPLACE'
                    elif (settings.RotationMix_enum == 'OP2'):
                        crc.mix_mode = 'ADD'
                    elif (settings.RotationMix_enum == 'OP3'):
                        crc.mix_mode = 'BEFORE'
                    elif (settings.RotationMix_enum == 'OP4'):
                        crc.mix_mode = 'AFTER'
                    elif (settings.RotationMix_enum == 'OP5'):
                        crc.mix_mode = 'OFFSET'

                    if (settings.RotationOrder_enum == 'OP1'):
                        crc.euler_order = 'AUTO'
                    elif (settings.RotationOrder_enum == 'OP2'):
                        crc.euler_order = 'XYZ'
                    elif (settings.RotationOrder_enum == 'OP3'):
                        crc.euler_order = 'XZY'
                    elif (settings.RotationOrder_enum == 'OP4'):
                        crc.euler_order = 'YXZ'
                    elif (settings.RotationOrder_enum == 'OP5'):
                        crc.euler_order = 'YZX'
                    elif (settings.RotationOrder_enum == 'OP6'):
                        crc.euler_order = 'ZXY'
                    elif (settings.RotationOrder_enum == 'OP7'):
                        crc.euler_order = 'ZYX'
                    crc.target = arm
                    crc.subtarget = target
                    crc.influence = settings.influence_float

                    if (settings.SpaceOwner_enum == 'OP1'):
                        crc.owner_space = 'WORLD'
                    elif (settings.SpaceOwner_enum == 'OP2'):
                        crc.owner_space = 'POSE'
                    elif (settings.SpaceOwner_enum == 'OP3'):
                        crc.owner_space = 'LOCAL_WITH_PARENT'
                    elif (settings.SpaceOwner_enum == 'OP4'):
                        crc.owner_space = 'LOCAL'

                    if (settings.SpaceTarget_enum == 'OP1'):
                        crc.target_space = 'WORLD'
                    elif (settings.SpaceTarget_enum == 'OP2'):
                        crc.target_space = 'POSE'
                    elif (settings.SpaceTarget_enum == 'OP3'):
                        crc.target_space = 'LOCAL_WITH_PARENT'
                    elif (settings.SpaceTarget_enum == 'OP4'):
                        crc.target_space = 'LOCAL'

        return {'FINISHED'}

class constraintChainOperator(bpy.types.Operator):
    bl_idname = "scene.constraintchain_operator"
    bl_label = "Add Constraints"
    global og_bones
    global new_bones
    global existingboneSetup
    bl_description = "Create Constraints between two existing Chains. Requires an Armature Target and for you to choose an Owner Chain and Target Chain from child bone to parent in the exact same order"

    @classmethod
    def poll(self, context):
        settings = context.scene.my_tool
        if (not settings.driv_bool and len(og_bones) > 0 and len(
                new_bones) > 0 and not settings.ArmatureTarget == None):
            return True
        elif (settings.driv_bool and not settings.ArmatureTarget == None and len(settings.drivpath_string) > 0 and len(
                og_bones) > 0 and len(new_bones) > 0 and not settings.ArmatureTarget == None):
            return True
        else:
            return False

    def execute(self, context):
        if any(i in new_bones for i in og_bones):
            self.report({'INFO'}, 'Execution Cancelled, Owner and Target Chains share at least one bone')
        elif len(new_bones)!=len(og_bones):
            self.report({'INFO'}, 'Execution Cancelled, Owner and Target Chains are not equal in length')
        else:
            settings = context.scene.my_tool
            if (settings.driv_bool):
                if not (checkforDrivers(settings.drivpath_string, settings)):
                    self.report({'INFO'}, 'Execution Cancelled, Driver Path does not exist')
                    return {'CANCELLED'}
            settings = context.scene.my_tool
            setConstraints(settings, new_bones, og_bones)
            global existingboneSetup
            existingboneSetup = og_bones
            if (settings.driv_bool):
                setDriver(settings, og_bones)
        return {'FINISHED'}


class ModalDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "scene.modal_operator"
    bl_label = "Choose Bone Chain"

    def modal(self, context, event):
        global chain_bones
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        # Enter here allows to enters chosen bones as selected chain
        elif event.type == 'RET':
            for b in self.bones:
                self.bonenames.append(b.name)
            chain_bones = self.bonenames
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in context.selected_bones if b not in self.bones] + [b for b in self.bones if
                                                                                   b in context.selected_bones]

        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'EDIT_ARMATURE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            global chain_bones
            # Empty bones at the beginning
            self.bones = []
            self.bonenames = []
            context.window_manager.modal_handler_add(self)

            chain_bones = self.bones
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class OwnerDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "scene.owner_operator"
    bl_label = "Choose Constraint Owner Chain"

    def modal(self, context, event):
        global og_bones
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        # Enter here allows to enters chosen bones as selected chain
        elif event.type == 'RET':
            for b in self.bones:
                self.bonenames.append(b.name)
            og_bones = self.bonenames
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in context.selected_bones if b not in self.bones] + [b for b in self.bones if
                                                                                   b in context.selected_bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'EDIT_ARMATURE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            global og_bones
            # Empty bones at the beginning
            self.bones = []
            self.bonenames = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class TargetDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "scene.target_operator"
    bl_label = "Choose Target Bone Chain"

    def modal(self, context, event):
        global new_bones
        # Escape here allows to stop, but you can also do it from any other property from your addon
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        # Enter here allows to enters chosen bones as selected chain
        elif event.type == 'RET':
            for b in self.bones:
                self.bonenames.append(b.name)
            new_bones = self.bonenames
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}

        # Last selected is first in this way of coding
        self.bones = [b for b in context.selected_bones if b not in self.bones] + [b for b in self.bones if
                                                                                   b in context.selected_bones]
        # Return PASS_THROUGH in order to allow Blender interpret the events
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')
        # Check the context for 'EDIT_ARMATURE'
        if context.area.type == 'VIEW_3D' and context.mode == 'EDIT_ARMATURE':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            global new_bones
            # Empty bones at the beginning
            self.bones = []
            self.bonenames = []
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}



"""
----------------------------------------------------------------------------------------------------------------------

Functions for each Panel Undo Execution Command
----------------------------------------------------------------------------------------------------------------------
"""

class Undo(bpy.types.Operator):
    bl_idname = "scene.undo_operator"
    bl_label = "Undo last Execution"
    global lastbones
    global og_bones
    bl_description = "Undo and delete the last carried out execution"

    @classmethod
    def poll(self, context):
        settings = context.scene.my_tool
        if (len(og_bones) > 0):
            return True
        else:
            return False

    def execute(self, context):
        global lastbones
        global og_bones
        bpy.ops.object.mode_set(mode='POSE')
        settings = context.scene.my_tool
        arm = settings.ArmatureTarget
        Active = bpy.context.active_object
        for i in range(0, len(og_bones)):
            bone = arm.pose.bones.get(og_bones[i])
            n = len(bone.constraints) - 1
            # print(bone.constraints[n])
            bone.constraints.remove(bone.constraints[n])

        bpy.ops.object.mode_set(mode='EDIT')
        arm = settings.ArmatureTarget
        for i in range(0, len(lastbones)):
            controller = arm.data.edit_bones.get(lastbones[i])
            arm.data.edit_bones.remove(controller)
        bpy.context.object.data.layers[0] = True
        lastbones = []
        og_bones = []
        return {'FINISHED'}


class UndoChain(bpy.types.Operator):
    bl_idname = "scene.undochain_operator"
    bl_label = "Undo last Chain Setup"
    global lastChain_bones
    bl_description = "Undo and delete the last carried out execution"

    @classmethod
    def poll(self, context):
        print("lst chain is " + str(lastChain_bones))
        settings = context.scene.my_tool
        if (len(lastChain_bones) > 0):
            return True
        else:
            return False

    def execute(self, context):
        global lastChain_bones
        bpy.ops.object.mode_set(mode='POSE')
        settings = context.scene.my_tool
        arm = settings.ArmatureTarget
        Active = bpy.context.active_object
        for i in range(1, len(lastChain_bones)):
            bone = arm.pose.bones.get(lastChain_bones[i])
            if len(bone.constraints) > 0:
                n = len(bone.constraints) - 1
                bone.constraints.remove(bone.constraints[n])
        lastChain_bones = []
        return {'FINISHED'}




class UndoExisting(bpy.types.Operator):
    bl_idname = "scene.undoexisting_operator"
    bl_label = "Undo last Execution"
    global existingboneSetup
    bl_description = "Undo and delete the last carried out execution"

    @classmethod
    def poll(self, context):
        settings = context.scene.my_tool
        if (len(existingboneSetup) > 0):
            return True
        else:
            return False

    def execute(self, context):
        global existingboneSetup
        bpy.ops.object.mode_set(mode='POSE')
        settings = context.scene.my_tool
        arm = settings.ArmatureTarget
        Active = bpy.context.active_object
        for i in range(0, len(existingboneSetup)):
            bone = arm.pose.bones.get(existingboneSetup[i])
            n = len(bone.constraints) - 1
            # print(bone.constraints[n])
            bone.constraints.remove(bone.constraints[n])
        existingboneSetup = []
        return {'FINISHED'}


class ExecuteEZControls(bpy.types.Operator):
    bl_idname = "scene.execute_operator"
    bl_label = "Execute"
    bl_description = "Create Controls, requires an Armature Target and a MINIMUM of at least one selected bone in edit mode"

    @classmethod
    def poll(self, context):
        settings = context.scene.my_tool
        if (context.active_object is not None and context.active_object.type == 'ARMATURE' and not settings.driv_bool and context.active_object.mode == 'EDIT' and not settings.ArmatureTarget == None and len(
                bpy.context.selected_bones) > 0):
            return True
        elif (settings.driv_bool and not settings.ArmatureTarget == None and len(
                settings.drivpath_string) > 0 and context.active_object.mode == 'EDIT' and not settings.ArmatureTarget == None and len(
                bpy.context.selected_bones) > 0):
            return True
        else:
            return False

    def execute(self, context):
        settings = context.scene.my_tool
        if (settings.driv_bool):
            if not (checkforDrivers(settings.drivpath_string, settings)):
                self.report({'INFO'}, 'Execution Cancelled, Driver Path does not exist')
                return {'CANCELLED'}
        settings = context.scene.my_tool
        original_bones = [bone.name for bone in bpy.context.selected_bones]
        global og_bones
        og_bones = original_bones
        bpy.ops.armature.duplicate()
        bones_selected = bpy.context.selected_bones
        for item in bones_selected:
            if (settings.name_enum == 'OP1'):
                item.name = item.name[:-4].replace(settings.find_string, settings.pref_string)
            elif (settings.name_enum == 'OP2'):
                item.name = settings.pref_string + item.name[:-4]
            elif (settings.name_enum == 'OP3'):
                item.name = item.name[:-4] + settings.pref_string
            item.use_deform = settings.def_bool

        new_bones = [bone.name for bone in bones_selected]
        if not (settings.inh_bool):
            clearconstraints(settings, new_bones)
        global lastbones
        lastbones = new_bones
        changeLayers(settings)
        setConstraints(settings, new_bones, original_bones)
        if (settings.driv_bool):
            setDriver(settings, original_bones)

        return {'FINISHED'}

"""
-----------------------------------------------------------------------------------------------------------------------

Shape Controls Function

------------------------------------------------------------------------------------------------------------------------"""


class generateShape(bpy.types.Operator):
    '''Generate a Shape for selected Bone'''
    bl_idname = "scene.genboneshape_operator"
    bl_label = "Generate Custom Bone Shape"

    def execute(self, context):
        settings = context.scene.my_tool
        if (settings.shape_enum == 'OP1'):
            create_Arrow_widget('WGT-Arrow',settings.shape_size)
        elif (settings.shape_enum == 'OP2'):
            create_ArrowWireframe_widget('WGT-Arrow-WireFrame', settings.shape_size)
        elif (settings.shape_enum == 'OP3'):
            create_doublesidedArrow_widget('WGT-Double-Sided-Arrow', settings.shape_size)
        elif (settings.shape_enum == 'OP4'):
            create_doublesidedArrowWireframe_widget('WGT-Double-Sided-Arrow-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP5'):
            create_3sideArrow_widget('WGT-Tripple-Sided-Arrow', settings.shape_size)
        elif (settings.shape_enum == 'OP6'):
            create_3sideArrowWireframe_widget('WGT-Tripple-Sided-Arrow-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP7'):
            create_4sideArrow_widget('WGT-Quad-Sided-Arrow', settings.shape_size)
        elif (settings.shape_enum == 'OP8'):
            create_4sideArrowWireframe_widget('WGT-Quad-Sided-Arrow-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP9'):
            create_leftCurveArrow_widget('WGT-Left-Curved-Arrow', settings.shape_size)
        elif (settings.shape_enum == 'OP10'):
            create_leftCurveWireframe_widget('WGT-Left-Curved-Arrow-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP11'):
            create_rightCurveArrow_widget('WGT-Right-Curved-Arrow', settings.shape_size)
        elif (settings.shape_enum == 'OP12'):
            create_rightCurveArrowWireframe_widget('WGT-Right-Curved-Arrow-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP13'):
            create_Circle_widget('WGT-Circle', settings.shape_size)
        elif (settings.shape_enum == 'OP14'):
            create_Square_widget('WGT-Square', settings.shape_size)
        elif (settings.shape_enum == 'OP15'):
            create_FilledCube_widget('WGT-Cube', settings.shape_size)
        elif (settings.shape_enum == 'OP16'):
            create_Cube_widget('WGT-Cube-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP17'):
            create_compass_widget('WGT-Compass', settings.shape_size)
        elif (settings.shape_enum == 'OP18'):
            create_FilledSphere_widget('WGT-Sphere', settings.shape_size)
        elif (settings.shape_enum == 'OP19'):
            create_Diamond_widget('WGT-Diamond', settings.shape_size)
        elif (settings.shape_enum == 'OP20'):
            create_DiamondWireframe_widget('WGT-Diamond-Wireframe', settings.shape_size)
        elif (settings.shape_enum == 'OP21'):
            create_head_widget('WGT-Head', settings.shape_size)
        elif (settings.shape_enum == 'OP22'):
            create_ArmFK_widget('WGT-Arm-FK', settings.shape_size)
        elif (settings.shape_enum == 'OP23'):
            create_hand_widget('WGT-Hand-FK', settings.shape_size)
        elif (settings.shape_enum == 'OP24'):
            create_FingerFK_widget('WGT-Finger-FK', settings.shape_size)
        elif (settings.shape_enum == 'OP25'):
            create_FootFK_widget('WGT-Foot-FK', settings.shape_size)
        elif (settings.shape_enum == 'OP26'):
            create_FootIK_widget('WGT-Foot-IK', settings.shape_size)
        elif (settings.shape_enum == 'OP27'):
            create_ToeFK_widget('WGT-Boot-Toes-FK', settings.shape_size)
        return {'FINISHED'}


class extractShape(bpy.types.Operator):
    '''Extract the bone's selected custom shape as a new object'''
    bl_idname = "scene.extractshape_operator"
    bl_label = "Extract custom shape"

    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE' and context.selected_pose_bones):
            return True
        else:
            return False

    def execute(self, context):

        armatureName = bpy.context.active_object.name
        armature = bpy.data.objects[armatureName]

        activePoseBone = bpy.context.active_pose_bone
        boneName = bpy.context.active_pose_bone.name
        bone = armature.data.bones[boneName]

        # If the user didn't pick a custom_shape return
        if not activePoseBone.custom_shape:
            return {'CANCELLED'}

        objectName = activePoseBone.custom_shape.name
        shapeObject = bpy.data.objects[objectName]

        # Create new mesh
        name = objectName
        mesh = bpy.data.meshes.new(name)
        # Create new object associated with the mesh
        ob_new = bpy.data.objects.new(name, mesh)

        # Copy data block from the old object into the new object
        ob_new.data = shapeObject.data.copy()
        ob_new.scale = shapeObject.scale
        ob_new.rotation_euler = shapeObject.rotation_euler
        ob_new.location = shapeObject.location

        # Link new object to the given scene and select it
        bpy.context.scene.collection.objects.link(ob_new)

        # switch from Pose mode to Object mode & select the new duplicated custom shape
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        ob_new.select_set(True)

        return {'FINISHED'}


class alignShape(bpy.types.Operator):
    '''Align selected bone's bone shape '''
    bl_idname = "scene.alignboneshape_operator"
    bl_label = "Set and Align bone shape"

    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE'
            and context.selected_pose_bones
            and [sel for sel in context.selected_objects if sel.type == 'MESH']):
            return True
        else:
            return False

    def execute(self, context):
        objects = [sel for sel in context.selected_objects if sel.type == 'MESH']
        shape = objects[0]

        bpy.ops.object.mode_set(mode='POSE')
        bone = context.selected_pose_bones[0]
        armature = context.view_layer.objects.active
        shape.name = "WGT_" + bone.name
        bone.custom_shape = shape
        bone.use_custom_shape_bone_size = True

        mat = armature.matrix_world @ bone.matrix
        mat.invert()

        shape.matrix_world = mathutils.Matrix.Scale(1 / bone.length, 4) @ mat @ shape.matrix_world

        bpy.ops.object.posemode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        shape.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        shape.matrix_world = armature.matrix_world @ bone.matrix @ mathutils.Matrix.Scale(bone.length, 4)
        shape.select_set(False)
        armature.select_set(True)
        bpy.ops.object.posemode_toggle()

        return {'FINISHED'}


class SnapShape(bpy.types.Operator):
    '''Align selected object to selected bone'''
    bl_idname = "scene.snapboneshape_operator"
    bl_label = "Snap selected Shape to bone"

    @classmethod
    def poll(self, context):
        if (context.mode == 'POSE'
            and context.selected_pose_bones
            and [sel for sel in context.selected_objects if sel.type == 'MESH']):
            return True
        else:
            return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        objects = [sel for sel in context.selected_objects if sel.type == 'MESH']

        shape = objects[0]
        boneName = context.selected_pose_bones[0].name
        armature = context.view_layer.objects.active
        bone = armature.pose.bones[boneName]
        bMat = bone.matrix.to_translation() + bone.vector / 2

        # obB.matrix_world = arm.matrix_world @ mathutils.Matrix.Translation(b)

        mat = armature.matrix_world @ mathutils.Matrix.Translation(bMat)
        shape.location = mat.to_translation()

        shape.rotation_mode = 'XYZ'
        print("rotation: " + str(bone.matrix.to_euler()))
        shape.rotation_euler = bone.matrix.to_euler()
        #shape.rotation_euler.x += math.pi / 2

        scale = mat.to_scale()
        scale_avg = (scale[0] + scale[1] + scale[2]) / 3
        shape.scale = (bone.length * scale_avg), (bone.length * scale_avg), (bone.length * scale_avg)

        return {'FINISHED'}

"""
-----------------------------------------------------------------------------------------------------------------------

Constraint GUI Layout

------------------------------------------------------------------------------------------------------------------------
"""
def copyLocationConstraints(settings,box):
    row = box.row()
    row.prop(settings, "x_bool")
    row.prop(settings, "y_bool")
    row.prop(settings, "z_bool")
    row = box.row()
    row.prop(settings, "xInv_bool")
    row.prop(settings, "yInv_bool")
    row.prop(settings, "zInv_bool")
    row = box.row()
    row.prop(settings, "offset_bool")
    row = box.row()
    row.label(text="Space: ")
    row.prop(settings, "SpaceTarget_enum")
    row.label(text=" <->")
    row.prop(settings, "SpaceOwner_enum")
    row = box.row()
    if not settings.driv_bool:
        row = box.row()
        row.prop(settings, "influence_float")


def copyRotationConstraints(settings,box):
    row = box.row()
    row.prop(settings, "RotationOrder_enum", text="Order")
    row = box.row()
    row.prop(settings, "x_bool")
    row.prop(settings, "y_bool")
    row.prop(settings, "z_bool")
    row = box.row()
    row.prop(settings, "xInv_bool")
    row.prop(settings, "yInv_bool")
    row.prop(settings, "zInv_bool")
    row = box.row()
    row.prop(settings, "RotationMix_enum")
    row = box.row()
    row.label(text="Space: ")
    row.prop(settings, "SpaceTarget_enum")
    row.label(text=" <->")
    row.prop(settings, "SpaceOwner_enum")
    if not settings.driv_bool:
        row = box.row()
        row.prop(settings, "influence_float")


def copyScaleConstraints(settings, box):
    row = box.row()
    row.prop(settings, "x_bool")
    row.prop(settings, "y_bool")
    row.prop(settings, "z_bool")
    row = box.row()
    row.prop(settings, "ScalePower_float")
    row = box.row()
    row.prop(settings, "ScaleUniform_bool")
    row = box.row()
    row.prop(settings, "offset_bool")
    row.prop(settings, "ScaleAdditive_bool")
    row = box.row()
    row.label(text="Space: ")
    row.prop(settings, "SpaceTarget_enum")
    row.label(text=" <->")
    row.prop(settings, "SpaceOwner_enum")
    if not settings.driv_bool:
        row = box.row()
        row.prop(settings, "influence_float")

def copyTransformationConstraints(settings, box):
    row = box.row()
    row.prop(settings, "TranslationMix_enum")
    row = box.row()
    row.label(text="Space: ")
    row.prop(settings, "SpaceTarget_enum")
    row.label(text=" <->")
    row.prop(settings, "SpaceOwner_enum")
    if not settings.driv_bool:
        row = box.row()
        row.prop(settings, "influence_float")


"""
------------------------------------------------------------------------------------------------------------------------

Panels

------------------------------------------------------------------------------------------------------------------------
"""


class EZControls(bpy.types.Panel):
    bl_label = "Create Controls"
    bl_idname = "ControlPanel_A"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EZ Controls'
    global lastConstraints

    def draw(self, context):
        layout = self.layout

        #call to check for update in background
        addon_updater_ops.check_for_update_background()

        settings = context.scene.my_tool

        row = layout.row()
        row.prop(settings, "name_enum")
        row = layout.row()
        if (settings.name_enum == 'OP1'):
            row.prop(settings, "find_string")
            row = layout.row()
        row.prop(settings, "pref_string")

        row = layout.row()
        row.label(text="NB. To avoid manually renaming new controls, please ensure no bone ends with a numeric value ")

        row = layout.row()
        row.prop(settings, "def_bool")
        row.prop(settings, "inh_bool")

        box = layout.box()
        box.prop(settings, "ArmatureTarget")
        box.label(text="Choose Bone Constraint")
        box.prop(settings, "constraint_enum")

        if (settings.constraint_enum == 'OP1'):
            # print("Use Case 1")
            copyLocationConstraints(settings, box)

        elif (settings.constraint_enum == 'OP2'):
            # print("Use Case 2")
            copyRotationConstraints(settings, box)
        elif (settings.constraint_enum == 'OP3'):
            # print("Use Case 3")
            copyScaleConstraints(settings, box)
        elif (settings.constraint_enum == 'OP4'):
            copyTransformationConstraints(settings, box)

        box = layout.box()
        box.prop(settings, "driv_bool")

        if settings.driv_bool:
            row = box.row()
            box.prop(settings, "ArmatureTarget", text="Prop")
            box.prop(settings, "drivpath_string")
            box.prop(settings, "drivInv_bool")

        row = layout.row()
        row.operator("scene.root_operator")
        row = layout.row()
        row.operator("scene.execute_operator")
        row = layout.row()
        row.operator("scene.undo_operator")

        addon_updater_ops.update_notice_box_ui(self, context)


class singleChainControls(bpy.types.Panel):
    bl_label = "Single Rotation Chain"
    bl_idname = "ControlPanel_B"
    bl_space_type = 'VIEW_3D'
    bl_options = {'DEFAULT_CLOSED'}
    bl_region_type = 'UI'
    bl_category = 'EZ Controls'
    global og_bones

    def draw(self, context):
        settings = context.scene.my_tool
        layout = self.layout
        row = layout.row()
        row.operator("scene.modal_operator")
        row = layout.row()
        row.label(text=" / ".join([b for b in chain_bones]))
        # print(og_bones)
        box = layout.box()
        copyRotationConstraints(settings, box)

        row = layout.row()
        row.operator("scene.singlechain_operator")
        row = layout.row()
        row.operator("scene.undochain_operator")


class ExistingChainControls(bpy.types.Panel):
    bl_label = "Constrain Existing Chains"
    bl_idname = "ControlPanel_C"
    bl_space_type = 'VIEW_3D'
    bl_options = {'DEFAULT_CLOSED'}
    bl_region_type = 'UI'
    bl_category = 'EZ Controls'
    global og_bones
    global new_bones

    def draw(self, context):
        settings = context.scene.my_tool
        layout = self.layout
        row = layout.row()
        row.operator("scene.owner_operator")
        row = layout.row()
        row.label(text=" / ".join([b for b in og_bones]))
        # print(og_bones)

        row = layout.row()
        row.operator("scene.target_operator")
        row = layout.row()
        row.label(text=" / ".join([b for b in new_bones]))

        box = layout.box()
        box.prop(settings, "ArmatureTarget")
        box.label(text="Choose Bone Constraint")
        box.prop(settings, "constraint_enum")
        if (settings.constraint_enum == 'OP1'):
            # print("Use Case 1")
            copyLocationConstraints(settings, box)
        elif (settings.constraint_enum == 'OP2'):
            # print("Use Case 2")
            copyRotationConstraints(settings, box)
        elif (settings.constraint_enum == 'OP3'):
            # print("Use Case 3")
            copyScaleConstraints(settings, box)
        elif (settings.constraint_enum == 'OP4'):
            copyTransformationConstraints(settings, box)
        box = layout.box()
        box.prop(settings, "driv_bool")

        if settings.driv_bool:
            row = box.row()
            box.prop(settings, "ArmatureTarget", text="Prop")
            box.prop(settings, "drivpath_string")
            box.prop(settings, "drivInv_bool")

        row = layout.row()
        row.operator("scene.constraintchain_operator")
        row = layout.row()
        row.operator("scene.undoexisting_operator")


class ShapeControls(bpy.types.Panel):
    bl_label = "Custom Control Shapes"
    bl_idname = "ControlPanel_D"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = 'EZ Controls'

    def draw(self, context):
        settings = context.scene.my_tool
        layout = self.layout
        row = layout.row()
        row.prop(settings, "shape_enum")
        row.prop(settings, "shape_size")
        row = layout.row()
        row.operator("scene.genboneshape_operator")
        row = layout.row()
        row.operator("scene.snapboneshape_operator")
        row = layout.row()
        row.operator("scene.alignboneshape_operator")
        row = layout.row()
        row.operator("scene.extractshape_operator")


"""
------------------------------------------------------------------------------------------------------------------------

Class Registration

------------------------------------------------------------------------------------------------------------------------
"""

classes = [MySettings, RootControls, ExecuteEZControls, EZControls, ModalDrawOperator, UndoChain, singleChainOperator,
           singleChainControls, Undo, UndoExisting, OwnerDrawOperator, TargetDrawOperator, constraintChainOperator,
           ExistingChainControls, extractShape, alignShape, ShapeControls, generateShape, SnapShape]


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError:
            pass
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MySettings)


def unregister():
    del bpy.types.Scene.my_tool
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

