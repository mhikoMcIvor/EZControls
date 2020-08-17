
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


bl_info= {
    "name" : "EZ-Controls",
    "author" : "Alexander Mhiko McIvor <alexandermcivor356@gmail.com>",
    "category": "Rigging",
    "location": "View3D > Tools > EZ Controls",
    "description": "Automate common-used practices once a manual rig has been made",
    "version": (1,0),
    "blender": (2,80,0),
}

if 'bpy' in locals():
    import importlib
    import bpy
    importlib.reload("Main")
    importlib.reload("WidgetValues")
    importlib.reload("FKIKSnap")
    importlib.reload("addon_updater_ops")

else:
    import bpy
    from . import Main
    from . import WidgetValues
    from . import FKIKSnap
    from . import addon_updater_ops


class updaterPreferences(bpy.types.AddonPreferences):
    """EZ Controls updaterPreferences"""
    bl_idname = __package__
    # addon updater preferences
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )

    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout =self.layout
        addon_updater_ops.update_settings_ui(self, context)



def register():
    bpy.utils.register_class(updaterPreferences)
    addon_updater_ops.register(bl_info)
    Main.register()
    WidgetValues.register()
    FKIKSnap.register()

def unregister():
    bpy.utils.unregister_class(updaterPreferences)
    addon_updater_ops.unregister()
    FKIKSnap.unregister()
    Main.unregister()
    WidgetValues.unregister()



if __name__ == "__main__":
    register()
