"""Smart Render Guard - Scan Operator.

Provides SRG_OT_ScanScene which runs the full diagnostic scan on the
current scene, updates the scene properties with results, and tags
all areas for redraw.
"""

import bpy
import time
from ..core.scanner import run_full_scan, store_report


class SRG_OT_ScanScene(bpy.types.Operator):
    """Run Smart Render Guard diagnostic scan on the current scene."""
    bl_idname = "srg.scan_scene"
    bl_label = "Scan Scene"
    bl_description = "Run Smart Render Guard diagnostic scan"

    def execute(self, context):
        context.scene.srg.scan_status = 'SCANNING'

        try:
            report = run_full_scan(context)
            store_report(report)

            status_map = {
                'safe': 'SAFE',
                'warning': 'WARNING',
                'critical': 'CRITICAL',
            }
            context.scene.srg.scan_status = status_map.get(
                report.overall_risk, 'IDLE'
            )
            context.scene.srg.last_scan_time = time.strftime("%H:%M:%S")

            # Build info message
            risk = report.overall_risk.upper()
            duration = f"{report.scan_duration_ms:.0f}ms"
            self.report(
                {'INFO'},
                f"Smart Render Guard: {risk} — scan completed in {duration}"
            )

            if report.errors:
                for err in report.errors:
                    self.report({'WARNING'}, f"SRG: {err}")

        except Exception as e:
            self.report({'ERROR'}, f"Scan failed: {str(e)}")
            context.scene.srg.scan_status = 'IDLE'
            return {'CANCELLED'}

        # Trigger redraw of all areas
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SRG_OT_ScanScene)


def unregister():
    bpy.utils.unregister_class(SRG_OT_ScanScene)
