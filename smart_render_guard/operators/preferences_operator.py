"""Smart Render Guard - Preferences Operators.

Provides utility operators for the addon preferences:
  - SRG_OT_OpenDocs:         Opens documentation in a web browser
  - SRG_OT_ResetPreferences: Resets all preferences to default values
    (uses REGISTER + UNDO since it modifies addon state)
"""

import bpy
import webbrowser


class SRG_OT_OpenDocs(bpy.types.Operator):
    """Open the Smart Render Guard documentation in a web browser."""
    bl_idname = "srg.open_docs"
    bl_label = "Open Documentation"
    bl_description = "Open Smart Render Guard documentation"

    def execute(self, context):
        webbrowser.open("https://novastrikes.com/smart-render-guard")
        return {'FINISHED'}


class SRG_OT_ResetPreferences(bpy.types.Operator):
    """Reset Smart Render Guard preferences to default values."""
    bl_idname = "srg.reset_preferences"
    bl_label = "Reset Preferences"
    bl_description = "Reset all Smart Render Guard settings to defaults"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        if prefs:
            prefs.vram_warning_threshold = 70
            prefs.vram_critical_threshold = 85
            prefs.ram_warning_threshold = 60
            prefs.ram_critical_threshold = 80
            prefs.total_tris_warning = 5
            prefs.total_tris_critical = 15
            prefs.texture_warning_mb = 2048
            prefs.texture_critical_mb = 4096
            prefs.particle_warning = 500000
            prefs.particle_critical = 2000000
            prefs.show_popup_on_warning = True
            prefs.show_popup_on_critical = True
            prefs.max_subsurf_autofix = 2
            prefs.create_auto_backup = True
            prefs.output_location_type = 'SAME_DIR'
            prefs.custom_output_dir = ""
            self.report({'INFO'}, "Smart Render Guard: Preferences reset to defaults")
        else:
            self.report({'ERROR'}, "Could not reset preferences: Preferences object not found")
            return {'CANCELLED'}

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SRG_OT_OpenDocs)
    bpy.utils.register_class(SRG_OT_ResetPreferences)


def unregister():
    bpy.utils.unregister_class(SRG_OT_ResetPreferences)
    bpy.utils.unregister_class(SRG_OT_OpenDocs)
