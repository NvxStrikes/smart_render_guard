"""Smart Render Guard - Optimization and Fix Operators.

Provides operators to apply safe automatic fixes, purge memory cache,
instance duplicates, downscale large textures, throttle Cycles bounces,
simplify material shaders, and restore simplified shaders.
"""
import bpy
from ..core.auto_fixer import apply_all_safe_fixes
from ..core.scanner import run_full_scan, store_report

class SRG_OT_AutoFix(bpy.types.Operator):
    """Apply all safe auto-fixes identified by Smart Render Guard."""
    bl_idname = 'srg.auto_fix'
    bl_label = 'Auto-Fix Safe Issues'
    bl_description = 'Apply safe automatic fixes (subdivision reduction)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        max_level = prefs.max_subsurf_autofix if prefs else 2
        results = apply_all_safe_fixes(context, max_subsurf_level=max_level)
        bpy.context.view_layer.update()
        sub_fixes = results.get('subdivision_fixes', [])
        if sub_fixes:
            for fix in sub_fixes:
                self.report({'INFO'}, f'Fixed: {fix}')
            self.report({'INFO'}, f'Smart Render Guard: {len(sub_fixes)} subdivision(s) reduced')
        else:
            has_subsurf_above_default = False
            for obj in context.scene.objects:
                if obj.type == 'MESH':
                    for mod in obj.modifiers:
                        if mod.type == 'SUBSURF' and mod.render_levels > 2:
                            has_subsurf_above_default = True
                            break
            if has_subsurf_above_default and max_level > 2:
                self.report({'WARNING'}, f'No subdivisions reduced. Max Subsurf Level is set to {max_level} in preferences. Set it to 2 or lower under Edit > Preferences > Add-ons > Smart Render Guard to fix L3+ subdivisions.')
            else:
                self.report({'INFO'}, 'Smart Render Guard: No subdivision fixes needed')
        purged = results.get('purged_count', 0)
        if purged > 0:
            self.report({'INFO'}, f'Smart Render Guard: Purged {purged} orphan data block(s)')
        instanced = results.get('instanced_count', 0)
        if instanced > 0:
            self.report({'INFO'}, f'Smart Render Guard: Linked {instanced} duplicate object(s)')
        p_warnings = results.get('particle_warnings', [])
        for warn in p_warnings:
            self.report({'WARNING'}, f'SRG: {warn}')

        def _run_scan():
            try:
                report = run_full_scan(context)
                store_report(report)
                for area in context.screen.areas:
                    area.tag_redraw()
            except Exception:
                pass
            return None
        bpy.app.timers.register(_run_scan, first_interval=0.2)
        return {'FINISHED'}

class SRG_OT_PurgeCache(bpy.types.Operator):
    """Purge all unused cache, images, and orphan data blocks from Blender memory."""
    bl_idname = 'srg.purge_cache'
    bl_label = 'Purge Memory Cache'
    bl_description = 'Purge orphan data blocks and clear unused cache/images'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..core.optimizer import purge_garbage
        purged = purge_garbage(context)
        self.report({'INFO'}, f'Smart Render Guard: Purged {purged} orphan data block(s)')
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}
classes = (SRG_OT_AutoFix, SRG_OT_PurgeCache)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)