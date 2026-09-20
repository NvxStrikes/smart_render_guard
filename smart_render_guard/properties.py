"""Smart Render Guard - Scene Properties.

Defines the SRG_SceneProperties PropertyGroup that stores scan status,
timing, and user-configurable options at the scene level.
"""

import bpy
import time


def get_scan_status(self):
    """Retrieve scan status dynamically from in-memory ScanReport."""
    from .core.scanner import get_last_report
    report = get_last_report()
    if not report:
        return 0  # 'IDLE'
    status_keys = {
        'safe': 2,      # 'SAFE'
        'warning': 3,   # 'WARNING'
        'critical': 4,  # 'CRITICAL'
    }
    return status_keys.get(report.overall_risk, 0)


def get_last_scan_time(self):
    """Retrieve last scan time dynamically from in-memory ScanReport."""
    from .core.scanner import get_last_report
    report = get_last_report()
    if not report or not hasattr(report, 'timestamp') or report.timestamp is None:
        return "Never"
    return time.strftime("%H:%M:%S", time.localtime(report.timestamp))


def get_vram_pct(self):
    """Calculate VRAM percentage dynamically from in-memory ScanReport."""
    from .core.scanner import get_last_report
    report = get_last_report()
    if report and report.vram and not report.vram.get('detection_failed', False):
        total = report.vram.get('total_mb', 0)
        used = report.vram.get('used_mb', 0)
        if total > 0:
            return (used / total) * 100.0
    return 0.0


def get_ram_pct(self):
    """Calculate RAM percentage dynamically from in-memory ScanReport."""
    from .core.scanner import get_last_report
    report = get_last_report()
    if report and report.ram and not report.ram.get('detection_failed', False):
        return float(report.ram.get('used_percent', 0.0))
    return 0.0


class SRG_SceneProperties(bpy.types.PropertyGroup):
    """Scene-level properties for Smart Render Guard."""

    scan_status: bpy.props.EnumProperty(
        items=[
            ('IDLE', 'Idle', 'No scan has been performed'),
            ('SCANNING', 'Scanning...', 'Scan in progress'),
            ('SAFE', 'Safe', 'Scene is safe to render'),
            ('WARNING', 'Warning', 'Potential issues found'),
            ('CRITICAL', 'Critical', 'Critical issues detected'),
        ],
        get=get_scan_status,
        set=lambda self, value: None
    )
    last_scan_time: bpy.props.StringProperty(
        name="Last Scan Time",
        get=get_last_scan_time,
        set=lambda self, value: None
    )
    show_details: bpy.props.BoolProperty(
        name="Show Details",
        description="Show detailed scan results",
        default=False
    )
    auto_scan_on_render: bpy.props.BoolProperty(
        name="Auto-Scan Before Render",
        description="Run diagnostic scan automatically when you press F12",
        default=True
    )
    block_render_on_critical: bpy.props.BoolProperty(
        name="Block Render on Critical Risk",
        description="Prevent render from starting if critical issues are found",
        default=False
    )
    vram_pct: bpy.props.FloatProperty(
        name="VRAM Usage",
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        get=get_vram_pct,
        set=lambda self, value: None
    )
    ram_pct: bpy.props.FloatProperty(
        name="RAM Usage",
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        get=get_ram_pct,
        set=lambda self, value: None
    )
    target_texture_size: bpy.props.EnumProperty(
        name="Target Texture Size",
        description="Maximum resolution (width/height) textures are downscaled to",
        items=[
            ('128', "128px", "Downscale to 128×128 max"),
            ('256', "256px", "Downscale to 256×256 max"),
            ('512', "512px", "Downscale to 512×512 max"),
            ('1024', "1024px", "Downscale to 1024×1024 max"),
            ('2048', "2048px", "Downscale to 2048×2048 max"),
            ('4096', "4096px", "Downscale to 4096×4096 max"),
        ],
        default='2048',
    )
    missing_texture_matches: bpy.props.StringProperty(
        name="Missing Texture Matches",
        description="JSON-encoded search results for missing textures",
        default=""
    )
    auto_purge_on_render: bpy.props.BoolProperty(
        name="Auto-Purge on Render",
        description="Automatically purge unused cache and image buffers when rendering starts",
        default=True
    )


def register():
    bpy.utils.register_class(SRG_SceneProperties)
    bpy.types.Scene.srg = bpy.props.PointerProperty(type=SRG_SceneProperties)


def unregister():
    del bpy.types.Scene.srg
    bpy.utils.unregister_class(SRG_SceneProperties)
