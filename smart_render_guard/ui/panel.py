"""Smart Render Guard — UI Panels.

Provides two panels:
  1. SRG_PT_MainPanel: Full diagnostics panel in the N-panel sidebar (VIEW_3D).
  2. SRG_PT_RenderProperties: Condensed panel in Render Properties.
"""

import bpy
from ..core.scanner import get_last_report
from ..utils.helpers import format_number, format_mb, risk_icon, risk_label
from ..core.tier import has_feature, CURRENT_TIER


def _get_issues(report):
    """Extract human-readable issue strings from a scan report."""
    issues = []
    if not report:
        return issues

    # Mesh issues
    meshes = report.meshes
    if meshes:
        for obj_info in meshes.get('objects', []):
            if obj_info.get('risk_level') in ('warning', 'critical'):
                name = obj_info.get('name', 'Unknown')
                tris = format_number(obj_info.get('final_tris', 0))
                sub_lvl = obj_info.get('subdivision_levels', 0)
                if sub_lvl > 0:
                    issues.append(f"Subsurf on \"{name}\" at L{sub_lvl} ({tris} tris)")
                else:
                    issues.append(f"\"{name}\" has {tris} triangles")

    # Texture issues
    textures = report.textures
    if textures:
        for tex in textures.get('large_textures', []):
            name = tex.get('name', 'Unknown')
            size = tex.get('size_mb', 0)
            res = tex.get('resolution', '')
            issues.append(f"Texture \"{name}\" = {format_mb(size)} ({res})")

    # Particle issues
    particles = report.particles
    if particles and particles.get('risk_level') in ('warning', 'critical'):
        total = format_number(particles.get('total_particles', 0))
        issues.append(f"Total particles: {total}")

    # VRAM issues
    vram = report.vram
    if vram and not vram.get('detection_failed', False):
        total = vram.get('total_mb', 0)
        used = vram.get('used_mb', 0)
        if total > 0:
            pct = (used / total) * 100
            if pct > 85:
                issues.append(f"VRAM usage critical: {pct:.0f}%")
            elif pct > 70:
                issues.append(f"VRAM usage high: {pct:.0f}%")

    # RAM issues
    ram = report.ram
    if ram and not ram.get('detection_failed', False):
        pct = ram.get('used_percent', 0)
        if pct > 80:
            issues.append(f"RAM usage critical: {pct:.0f}%")
        elif pct > 60:
            issues.append(f"RAM usage high: {pct:.0f}%")

    return issues


# NOTE: panel.py's structure is shared intentionally across all tiers.
# Lower tiers hide buttons via has_feature() checks, and the underlying operators
# are physically excluded from the zip at build time.
class SRG_PT_MainPanel(bpy.types.Panel):
    """Full Smart Render Guard diagnostics panel in the 3D-Viewport N-panel."""
    bl_label = "Smart Render Guard"
    bl_idname = "SRG_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Guard"

    # SRG_TIER: Show tier badge in panel header
    def draw_header(self, context):
        layout = self.layout
        if CURRENT_TIER == 'LITE':
            layout.label(text="FREE", icon='SOLO_OFF')
        elif CURRENT_TIER == 'BASIC':
            layout.label(text="BASIC", icon='SOLO_ON')
        elif CURRENT_TIER == 'PRO':
            layout.label(text="PRO ✦", icon='SOLO_ON')

    def draw(self, context):
        layout = self.layout
        
        srg = context.scene.srg
        report = get_last_report()

        # ----- Header -----
        header = layout.box()
        header.label(text="🛡 SMART RENDER GUARD", icon='LOCKED')
        header.label(text="by NovaStrikes")

        # ----- Scan button -----
        layout.separator()
        scan_row = layout.row(align=True)
        scan_row.scale_y = 1.5
        scan_row.operator("srg.scan_scene", text="🔍 SCAN SCENE", icon='VIEWZOOM')

        # ----- Status -----
        status_box = layout.box()
        status = srg.scan_status
        if status == 'IDLE':
            status_box.label(text="Status: No scan performed", icon='QUESTION')
        elif status == 'SCANNING':
            status_box.label(text="Status: Scanning...", icon='SORTTIME')
        elif status == 'SAFE':
            row = status_box.row()
            row.label(text="Status: ● SAFE", icon='CHECKMARK')
        elif status == 'WARNING':
            row = status_box.row()
            row.alert = True
            row.label(text="Status: ⚠ WARNING", icon='ERROR')
        elif status == 'CRITICAL':
            row = status_box.row()
            row.alert = True
            row.label(text="Status: ✖ CRITICAL", icon='CANCEL')

        status_box.label(text=f"Last scan: {srg.last_scan_time}")

        # Workflow tip
        tip_box = layout.box()
        tip_box.label(text="💡 Tip: Click SCAN SCENE to analyze risks,", icon='LIGHT')
        tip_box.label(text="   then click SAFE RENDER to validate and run.", icon='NONE')

        # ----- Diagnostics (collapsible) -----
        if report:
            if has_feature('visual_dashboard'):
                layout.prop(
                    srg, "show_details",
                    text="▼ DIAGNOSTICS" if srg.show_details else "► DIAGNOSTICS",
                    icon='DISCLOSURE_TRI_DOWN' if srg.show_details else 'DISCLOSURE_TRI_RIGHT',
                )

                if srg.show_details:
                    diag_box = layout.box()

                    # GPU VRAM
                    vram = report.vram
                    if vram and not vram.get('detection_failed', False):
                        gpu_name = vram.get('gpu_name', 'Unknown')
                        total_mb = vram.get('total_mb', 0)
                        if total_mb > 0:
                            diag_box.label(text=f"GPU: {gpu_name} ({format_mb(total_mb)})", icon='DESKTOP')
                        else:
                            diag_box.label(text=f"GPU: {gpu_name}", icon='DESKTOP')
                        
                        col = diag_box.column(align=True)
                        col.prop(srg, "vram_pct", text="VRAM Usage", slider=True)
                        if not vram.get('usage_trackable', False):
                            diag_box.label(
                                text="Live usage not available for this GPU — showing total only",
                                icon='INFO'
                            )
                    elif vram:
                        diag_box.label(text="GPU: Detection failed", icon='QUESTION')

                    # RAM
                    ram = report.ram
                    if ram and not ram.get('detection_failed', False):
                        col = diag_box.column(align=True)
                        col.prop(srg, "ram_pct", text="System RAM", slider=True)
                    elif ram:
                        diag_box.label(text="RAM: Detection failed", icon='QUESTION')

                    # Triangles
                    meshes = report.meshes
                    if meshes:
                        total_tris = meshes.get('total_tris', 0)
                        mesh_risk = 'safe'
                        for obj_info in meshes.get('objects', []):
                            if obj_info.get('risk_level') == 'critical':
                                mesh_risk = 'critical'
                                break
                            elif obj_info.get('risk_level') == 'warning':
                                mesh_risk = 'warning'
                        icon = risk_icon(mesh_risk)
                        row = diag_box.row()
                        if mesh_risk != 'safe':
                            row.alert = True
                        row.label(text=f"Triangles: {format_number(total_tris)}", icon=icon)

                    # Textures
                    textures = report.textures
                    if textures:
                        tex_mb = textures.get('total_estimated_mb', 0)
                        tex_risk = textures.get('risk_level', 'safe')
                        icon = risk_icon(tex_risk)
                        row = diag_box.row()
                        if tex_risk != 'safe':
                            row.alert = True
                        row.label(text=f"Textures: {format_mb(tex_mb)}", icon=icon)

                    # Particles
                    particles = report.particles
                    if particles:
                        total_p = particles.get('total_particles', 0)
                        p_risk = particles.get('risk_level', 'safe')
                        icon = risk_icon(p_risk)
                        row = diag_box.row()
                        if p_risk != 'safe':
                            row.alert = True
                        row.label(text=f"Particles: {format_number(total_p)}", icon=icon)
            else:
                row = layout.row()
                row.enabled = False
                row.operator("srg.scan_scene", text="🔒 Visual Dashboard — Basic+", icon='LOCKED')
                hint = layout.row()
                hint.label(text="Upgrade to Basic", icon='URL')

            # ----- Issues section -----
            issues = _get_issues(report)
            if issues:
                layout.separator()
                issues_box = layout.box()
                issues_box.alert = True
                issues_box.label(text="⚠ ISSUES FOUND", icon='ERROR')
                for issue in issues:
                    issues_box.label(text=f"• {issue}")

            # ----- Auto-fix button -----
            if report.fixes_available:
                layout.separator()
                fix_row = layout.row()
                fix_row.scale_y = 1.3
                fix_row.operator("srg.auto_fix", text="⚡ AUTO-FIX SAFE ISSUES", icon='SHADERFX')

            # ----- Scene Optimizers Toolbox -----
            layout.separator()
            opt_box = layout.box()
            opt_box.label(text="🛠 SCENE OPTIMIZERS", icon='MODIFIER')
            
            row = opt_box.row(align=True)
            row.operator("srg.purge_cache", text="Purge Memory Cache", icon='TRASH')
            
            # Geometry Instancer
            if has_feature('geometry_instancer'):
                row = opt_box.row(align=True)
                row.operator("srg.instance_meshes", text="Instance Duplicates", icon='LINKED')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.instance_meshes", text="🔒 Geometry Instancer — Basic+", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Basic", icon='URL')
            
            # Texture Downscaler
            if has_feature('texture_downscaler'):
                row = opt_box.row()
                row.prop(context.scene.srg, "target_texture_size", text="Target Size")
                row = opt_box.row(align=True)
                row.operator("srg.downscale_textures", text="Downscale Textures", icon='IMAGE_DATA')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.downscale_textures", text="🔒 Downscale Textures — Basic+", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Basic", icon='URL')

            # Light Path Throttler
            if has_feature('light_path_throttler'):
                row = opt_box.row(align=True)
                row.operator("srg.throttle_bounces", text="Throttle Cycles Bounces", icon='LIGHT')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.throttle_bounces", text="🔒 Light Path Throttler — Basic+", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Basic", icon='URL')

            # Shader Simplifier
            if has_feature('shader_simplifier'):
                row = opt_box.row(align=True)
                row.operator("srg.simplify_shaders", text="Simplify Material Shaders", icon='NODE')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.simplify_shaders", text="🔒 Shader Simplifier — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro", icon='URL')

            # Revert/Restore Button
            has_simplified = any("srg_simplified_textures" in mat for mat in bpy.data.materials)
            if has_simplified:
                if has_feature('shader_restorer'):
                    row = opt_box.row(align=True)
                    row.alert = True  # Red/highlighted to draw attention
                    row.operator("srg.restore_shaders", text="Restore Simplified Shaders", icon='FILE_REFRESH')
                else:
                    row = opt_box.row(align=True)
                    row.enabled = False
                    row.operator("srg.restore_shaders", text="🔒 Shader Restorer — Pro Only", icon='LOCKED')
                    hint = opt_box.row()
                    hint.label(text="Upgrade to Pro", icon='URL')

            # Forensics Logger
            if has_feature('forensics_logger'):
                row = opt_box.row(align=True)
                row.operator("srg.generate_crash_log", text="Generate Forensic Log", icon='TEXT')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.generate_crash_log", text="🔒 Black Box Logger — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro", icon='URL')

            # CLI Autopilot placeholder
            if not has_feature('cli_autopilot'):
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.purge_cache", text="🔒 CLI Autopilot — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro", icon='URL')

        # SRG_VALIDATOR: Validation Results sub-panel
        box = layout.box()
        row = box.row()
        row.label(text="⚡ Pre-Render Validation", icon='VIEWZOOM')

        # Run Validation button
        row = box.row()
        row.scale_y = 1.3
        row.operator("srg.run_validation", text="Scan Scene Now", icon='PLAY')

        # Pre-render Auto Validate lock
        if has_feature('pre_render_auto_validate'):
            row = box.row()
            row.label(text="✓ Auto Validation Active", icon='CHECKMARK')
        else:
            row = box.row()
            row.enabled = False
            row.label(text="🔒 Auto Validation — Pro Only", icon='LOCKED')
            hint = box.row()
            hint.label(text="Upgrade to Pro", icon='URL')

        # Show results if available
        scene = context.scene
        if 'srg_validation_severity' in scene:
            severity = scene['srg_validation_severity']
            total = scene['srg_validation_total_issues']
            
            # Severity badge
            row = box.row()
            if severity == 'SAFE':
                row.label(text=f"✓ SAFE — No issues found", icon='CHECKMARK')
            elif severity == 'WARNING':
                row.alert = True
                row.label(text=f"⚠ WARNING — {total} issue(s) found", icon='ERROR')
            else:
                row.alert = True
                row.label(text=f"🔴 CRITICAL — {total} issue(s) found", icon='CANCEL')

            # Individual category rows
            col = box.column(align=True)
            
            broken = scene.get('srg_val_broken_drivers', 0)
            missing_lib = scene.get('srg_val_missing_libs', 0)
            missing_tex = scene.get('srg_val_missing_tex', 0)
            heavy_mod = scene.get('srg_val_heavy_mods', 0)
            
            if broken > 0:
                row = col.row()
                row.alert = True
                row.label(text=f"  Broken Drivers: {broken}", icon='DRIVER')
            
            if missing_lib > 0:
                row = col.row()
                row.alert = True
                row.label(text=f"  Missing Libraries: {missing_lib}", icon='LIBRARY_DATA_BROKEN')
            
            if missing_tex > 0:
                row = col.row()
                row.alert = True
                row.label(text=f"  Missing Textures: {missing_tex}", icon='IMAGE_DATA')
            
            if heavy_mod > 0:
                row = col.row()
                row.label(text=f"  High-Risk Modifiers: {heavy_mod}", icon='MODIFIER')
            
            if total == 0:
                col.label(text="  All checks passed ✓")

        # Locate Missing Textures (Basic+)
        row = box.row(align=True)
        if has_feature('locate_missing_textures'):
            row.operator("srg.locate_missing_textures", text="Locate Missing Textures", icon='VIEWZOOM')
        else:
            row.enabled = False
            row.operator("srg.locate_missing_textures", text="🔒 Locate Missing Textures — Basic+", icon='LOCKED')
            hint = box.row()
            hint.label(text="Upgrade to Basic", icon='URL')

        # Relink Results Display
        if srg.missing_texture_matches:
            import json
            import os
            try:
                matches_data = json.loads(srg.missing_texture_matches)
            except Exception:
                matches_data = {}

            if matches_data:
                results_box = box.box()
                results_box.label(text="Missing Texture Matches:", icon='FILE_IMAGE')
                blend_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath)) if bpy.data.filepath else ""

                for img_name, paths in matches_data.items():
                    col_item = results_box.column(align=True)
                    col_item.label(text=f"• {img_name}", icon='IMAGE_DATA')
                    if paths:
                        for p in paths:
                            row_match = col_item.row(align=True)
                            try:
                                rel_p = os.path.relpath(p, blend_dir) if blend_dir else os.path.basename(p)
                            except Exception:
                                rel_p = os.path.basename(p)
                            op = row_match.operator("srg.relink_texture", text=f"Relink: {rel_p}", icon='LINKED')
                            op.image_name = img_name
                            op.chosen_path = p
                    else:
                        sub_row = col_item.row()
                        sub_row.enabled = False
                        sub_row.label(text="  No match found nearby", icon='INFO')

        # ----- Safe Render button -----
        layout.separator()
        render_row = layout.row()
        render_row.scale_y = 1.3
        render_row.operator("srg.safe_render", text="🎬 SAFE RENDER", icon='RENDER_STILL')

        # ----- Settings -----
        layout.separator()
        settings_box = layout.box()
        settings_box.label(text="⚙ Settings", icon='PREFERENCES')
        settings_box.prop(srg, "auto_scan_on_render")
        settings_box.prop(srg, "block_render_on_critical")
        settings_box.prop(srg, "auto_purge_on_render")
        settings_box.prop(srg, "target_texture_size")

        # Auto Backup Setting (Basic+)
        from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        if prefs:
            if has_feature('auto_backup'):
                settings_box.prop(prefs, "create_auto_backup")
            else:
                row = settings_box.row()
                row.enabled = False
                row.prop(prefs, "create_auto_backup", text="🔒 Auto Backup — Basic+")
                hint = settings_box.row()
                hint.label(text="Upgrade to Basic", icon='URL')

        # ----- Scan errors -----
        if report and report.errors:
            layout.separator()
            err_box = layout.box()
            err_box.label(text="Scan Errors:", icon='INFO')
            for err in report.errors:
                err_box.label(text=f"  {err}")

        # SRG_TIER: Upgrade CTA at bottom of panel
        if CURRENT_TIER == 'LITE':
            layout.separator()
            box = layout.box()
            box.label(text="⬆ Unlock Full Suite", icon='FUND')
            box.operator("wm.url_open", text="Upgrade at novastrikes.com").url = "https://novastrikes.com"
        elif CURRENT_TIER == 'BASIC':
            layout.separator()
            box = layout.box()
            box.label(text="⬆ Unlock Pro Features", icon='FUND')
            box.operator("wm.url_open", text="Upgrade to Pro").url = "https://novastrikes.com"


class SRG_PT_RenderProperties(bpy.types.Panel):
    """Condensed Smart Render Guard panel in Render Properties."""
    bl_label = "Smart Render Guard"
    bl_idname = "SRG_PT_render_props"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        srg = context.scene.srg
        report = get_last_report()

        # Status row
        row = layout.row(align=True)
        status = srg.scan_status
        if status == 'SAFE':
            row.label(text="● SAFE", icon='CHECKMARK')
        elif status == 'WARNING':
            row.alert = True
            row.label(text="⚠ WARNING", icon='ERROR')
        elif status == 'CRITICAL':
            row.alert = True
            row.label(text="✖ CRITICAL", icon='CANCEL')
        else:
            row.label(text="Not scanned", icon='QUESTION')

        row.label(text=f"Last: {srg.last_scan_time}")

        # Buttons
        row = layout.row(align=True)
        row.operator("srg.scan_scene", text="Scan", icon='VIEWZOOM')
        row.operator("srg.safe_render", text="Safe Render", icon='RENDER_STILL')

        if report and report.fixes_available:
            layout.operator("srg.auto_fix", text="Auto-Fix", icon='SHADERFX')

        # Quick diagnostics
        if report:
            box = layout.box()
            meshes = report.meshes
            if meshes:
                box.label(
                    text=f"Tris: {format_number(meshes.get('total_tris', 0))}",
                    icon=risk_icon('safe' if meshes.get('total_tris', 0) < 5000000 else 'warning'),
                )
            textures = report.textures
            if textures:
                box.label(
                    text=f"Tex: {format_mb(textures.get('total_estimated_mb', 0))}",
                    icon=risk_icon(textures.get('risk_level', 'safe')),
                )
            particles = report.particles
            if particles:
                box.label(
                    text=f"Particles: {format_number(particles.get('total_particles', 0))}",
                    icon=risk_icon(particles.get('risk_level', 'safe')),
                )

        # Settings
        layout.prop(srg, "auto_scan_on_render")
        layout.prop(srg, "block_render_on_critical")


def register():
    bpy.utils.register_class(SRG_PT_MainPanel)
    bpy.utils.register_class(SRG_PT_RenderProperties)


def unregister():
    bpy.utils.unregister_class(SRG_PT_RenderProperties)
    bpy.utils.unregister_class(SRG_PT_MainPanel)
