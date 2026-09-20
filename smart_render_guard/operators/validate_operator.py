# SRG_VALIDATOR
"""Smart Render Guard - Validate Operator.

Provides SRG_OT_RunValidation operator to scan the scene for crash-prone configurations
and cache the results in custom scene properties.
"""

import bpy


# SRG_VALIDATOR
class SRG_OT_RunValidation(bpy.types.Operator):
    bl_idname = "srg.run_validation"
    bl_label = "Run Scene Validation"
    bl_description = "Scan scene for broken drivers, missing files, and high-risk modifiers"
    
    def execute(self, context):
        from ..core.validator import validate_scene
        
        results = validate_scene(context)
        
        # Store results in scene custom properties for UI display
        # SRG_VALIDATOR: Cache results in scene props
        context.scene['srg_validation_severity'] = results['severity']
        context.scene['srg_validation_total_issues'] = results['total_issues']
        context.scene['srg_val_broken_drivers'] = len(results['broken_drivers'])
        context.scene['srg_val_missing_libs'] = len(results['missing_libraries'])
        context.scene['srg_val_missing_tex'] = len(results['missing_textures'])
        context.scene['srg_val_heavy_mods'] = len(results['heavy_modifiers'])
        
        # Print summary to console
        print(f"[SRG] Validation complete — Severity: {results['severity']}")
        print(f"[SRG] Broken drivers: {len(results['broken_drivers'])}")
        print(f"[SRG] Missing libraries: {len(results['missing_libraries'])}")
        print(f"[SRG] Missing textures: {len(results['missing_textures'])}")
        print(f"[SRG] High-risk modifiers: {len(results['heavy_modifiers'])}")
        
        # Show popup if CRITICAL
        if results['severity'] == 'CRITICAL':
            self.report({'ERROR'}, 
                f"CRITICAL: {results['total_issues']} issue(s) found. "
                f"Check SRG panel for details. "
                f"Fix before rendering to prevent crashes."
            )
        elif results['severity'] == 'WARNING':
            self.report({'WARNING'}, 
                f"WARNING: {results['total_issues']} issue(s) found. "
                f"Check SRG panel for details."
            )
        else:
            self.report({'INFO'}, "Scene validation passed. Safe to render.")
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SRG_OT_RunValidation)


def unregister():
    bpy.utils.unregister_class(SRG_OT_RunValidation)
