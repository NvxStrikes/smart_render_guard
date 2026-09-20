"""Smart Render Guard - Safe Render Operator.

Provides SRG_OT_SafeRender which runs a diagnostic scan before starting
the render. If critical issues are found and blocking is enabled, the
render is cancelled. Warning popups are invoked via bpy.app.timers to
ensure they run safely outside the operator context.
"""

import bpy
from ..core.scanner import run_full_scan, store_report


class SRG_OT_SafeRender(bpy.types.Operator):
    """Run Smart Render Guard scan, then start render if safe."""
    bl_idname = "srg.safe_render"
    bl_label = "Safe Render"
    bl_description = "Scan scene for issues before starting render"

    def execute(self, context):
        import time

        # Run full scan
        report = run_full_scan(context)
        store_report(report)



        # If critical and blocking is enabled, show warning instead of rendering
        if (
            report.overall_risk == 'critical'
            and context.scene.srg.block_render_on_critical
        ):
            self.report(
                {'WARNING'},
                "Smart Render Guard: CRITICAL issues found — render blocked"
            )
            # Show popup via timer (safe from operator context)
            bpy.app.timers.register(
                lambda: _invoke_warning_popup() or None,
                first_interval=0.1
            )
            return {'CANCELLED'}

        # If warning/critical, show popup but continue
        if report.overall_risk in ('warning', 'critical'):
            from ..utils.helpers import get_addon_preferences
            prefs = get_addon_preferences(context)
            if prefs:
                show_on_warn = prefs.show_popup_on_warning
                show_on_crit = prefs.show_popup_on_critical
            else:
                show_on_warn = True
                show_on_crit = True

            should_show = (
                (report.overall_risk == 'warning' and show_on_warn)
                or (report.overall_risk == 'critical' and show_on_crit)
            )
            if should_show:
                bpy.app.timers.register(
                    lambda: _invoke_warning_popup() or None,
                    first_interval=0.1
                )
                # Continue to render after showing warning

        # Safe — start render
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}


def _invoke_warning_popup():
    """Helper to invoke the warning popup from a timer."""
    try:
        bpy.ops.srg.show_render_warning('INVOKE_DEFAULT')
    except Exception:
        pass
    return None


def register():
    bpy.utils.register_class(SRG_OT_SafeRender)


def unregister():
    bpy.utils.unregister_class(SRG_OT_SafeRender)
