"""Smart Render Guard — Pre-Render Warning Popup.

Displays a modal dialog with scan issues before rendering.
Invoked via bpy.app.timers.register() from the render_pre handler
(never called directly inside the handler).
"""

import bpy
from ..core.scanner import get_last_report
from ..utils.helpers import format_number, format_mb


class SRG_OT_ShowRenderWarning(bpy.types.Operator):
    """Pre-render warning popup for Smart Render Guard."""
    bl_idname = "srg.show_render_warning"
    bl_label = "Smart Render Guard — Pre-Render Warning"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        report = get_last_report()

        if not report:
            layout.label(text="No scan data available.", icon='INFO')
            return

        # Risk header
        if report.overall_risk == 'critical':
            header = layout.box()
            header.alert = True
            header.label(text="⚠ CRITICAL RISK DETECTED", icon='CANCEL')
            header.label(text="Rendering may crash or consume excessive resources.")
        elif report.overall_risk == 'warning':
            header = layout.box()
            header.label(text="⚠ Warnings Found", icon='ERROR')
            header.label(text="Some issues may affect render performance.")

        layout.separator()

        # Issues list
        issues = _get_popup_issues(report)
        if issues:
            issues_box = layout.box()
            issues_box.label(text="Issues:", icon='INFO')
            for issue in issues:
                issues_box.label(text=f"  • {issue}")

        layout.separator()

        # Auto-fix button
        if report.fixes_available:
            layout.operator("srg.auto_fix", text="⚡ Auto-Fix Safe Issues", icon='SHADERFX')

        layout.label(text="Click OK to dismiss this warning.")

    def execute(self, context):
        return {'FINISHED'}


def _get_popup_issues(report):
    """Extract issue strings for popup display."""
    issues = []
    if not report:
        return issues

    meshes = report.meshes
    if meshes:
        for obj_info in meshes.get('objects', []):
            if obj_info.get('risk_level') in ('warning', 'critical'):
                name = obj_info.get('name', 'Unknown')
                tris = format_number(obj_info.get('final_tris', 0))
                sub = obj_info.get('subdivision_levels', 0)
                if sub > 0:
                    issues.append(f"Subsurf on \"{name}\" at Level {sub} ({tris} tris)")
                else:
                    issues.append(f"\"{name}\" = {tris} triangles")

    textures = report.textures
    if textures:
        for tex in textures.get('large_textures', []):
            issues.append(f"Texture \"{tex['name']}\" = {format_mb(tex['size_mb'])}")

    particles = report.particles
    if particles and particles.get('risk_level') in ('warning', 'critical'):
        issues.append(f"Particles: {format_number(particles.get('total_particles', 0))} total")

    vram = report.vram
    if vram and not vram.get('detection_failed', False) and vram.get('total_mb', 0) > 0:
        pct = (vram['used_mb'] / vram['total_mb']) * 100
        if pct > 70:
            issues.append(f"VRAM: {pct:.0f}% used")

    ram = report.ram
    if ram and not ram.get('detection_failed', False):
        pct = ram.get('used_percent', 0)
        if pct > 60:
            issues.append(f"RAM: {pct:.0f}% used")

    return issues


def register():
    bpy.utils.register_class(SRG_OT_ShowRenderWarning)


def unregister():
    bpy.utils.unregister_class(SRG_OT_ShowRenderWarning)
