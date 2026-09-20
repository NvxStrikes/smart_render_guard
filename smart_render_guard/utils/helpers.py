"""Smart Render Guard - Shared formatting utilities.

Provides helper functions for formatting bytes, numbers, and risk indicators
used throughout the Smart Render Guard addon UI and reports.
"""


def format_bytes(size_bytes):
    """Format bytes into human-readable string (KB, MB, GB)."""
    if size_bytes <= 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.1f} {units[i]}"


def format_number(n):
    """Format large numbers with K/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_mb(mb):
    """Format megabytes into human-readable string."""
    if mb >= 1024:
        return f"{mb / 1024:.1f} GB"
    return f"{mb:.0f} MB"


def risk_icon(risk_level):
    """Return Blender icon name for risk level."""
    icons = {
        'safe': 'CHECKMARK',
        'warning': 'ERROR',
        'critical': 'CANCEL',
        'unknown': 'QUESTION',
    }
    return icons.get(risk_level, 'QUESTION')


def risk_label(risk_level):
    """Return display label for risk level."""
    labels = {
        'safe': '● SAFE',
        'warning': '⚠ WARNING',
        'critical': '✖ CRITICAL',
        'unknown': '? UNKNOWN',
    }
    return labels.get(risk_level, '? UNKNOWN')


def get_addon_preferences(context=None):
    """Safely retrieve Smart Render Guard addon preferences.

    Handles both legacy registrations ('smart_render_guard') and Blender 4.2+
    extension registrations (e.g. 'bl_ext.user_default.smart_render_guard').
    """
    import bpy
    if not context:
        context = bpy.context

    # Try using __package__ dynamically
    try:
        pkg = __package__.rpartition('.')[0]
        if pkg and pkg in context.preferences.addons:
            return context.preferences.addons[pkg].preferences
    except Exception:
        pass

    # Fallback to key matches
    for key in context.preferences.addons.keys():
        if "smart_render_guard" in key:
            prefs = context.preferences.addons[key].preferences
            if prefs:
                return prefs

    return None


def get_srg_data_dir(context=None) -> str:
    """Resolve and return the directory path where all SRG outputs should be stored.

    Creates a subfolder named [blend_name]_srg_data in the resolved base output folder.
    """
    import bpy
    import os
    if not context:
        context = bpy.context

    prefs = get_addon_preferences(context)
    blend_path = bpy.data.filepath

    if blend_path:
        dir_name, file_name = os.path.split(blend_path)
        base_name, _ = os.path.splitext(file_name)
        folder_name = f"{base_name}_srg_data"

        if prefs and prefs.output_location_type == 'CUSTOM' and prefs.custom_output_dir:
            base_dir = bpy.path.abspath(prefs.custom_output_dir)
        else:
            base_dir = dir_name

        target_dir = os.path.join(base_dir, folder_name)
        try:
            os.makedirs(target_dir, exist_ok=True)
            return target_dir
        except Exception as e:
            print(f"[SRG] Could not create SRG data directory at '{target_dir}': {e}")
            return None
    else:
        import tempfile
        target_dir = os.path.join(tempfile.gettempdir(), "unsaved_blend_srg_data")
        try:
            os.makedirs(target_dir, exist_ok=True)
            return target_dir
        except Exception as e:
            print(f"[SRG] Could not create temp SRG data directory at '{target_dir}': {e}")
            return None

