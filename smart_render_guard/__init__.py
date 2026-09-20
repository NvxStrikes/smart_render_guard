"""Smart Render Guard — Main Addon Entry Point.

Pre-render diagnostics, crash forensics, and automation for Blender.
"""

bl_info = {
    "name": "Smart Render Guard Lite",
    "author": "NovaStrikes",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Properties > Render > Smart Render Guard | N-Panel > Render Guard",
    "description": "Free scene optimizer and crash scanner. Upgrade for full features.",
    "category": "Render",
    "doc_url": "https://novastrikes.com/smart-render-guard",
    "tracker_url": "https://novastrikes.com/support",
}

import bpy
from . import properties
from . import preferences
from . import operators
from . import ui
from .core.scanner import run_full_scan, store_report, get_last_report


def _invoke_warning_popup():
    """Safely invoke the warning popup from a timer context."""
    try:
        bpy.ops.srg.show_render_warning('INVOKE_DEFAULT')
    except Exception:
        pass
    return None


def pre_render_check(scene, depsgraph=None):
    """Called by Blender's render_pre handler before each render."""
    if scene.srg.auto_purge_on_render:
        try:
            from .core.optimizer import purge_garbage
            purge_garbage(bpy.context)
        except Exception:
            pass

    if not scene.srg.auto_scan_on_render:
        return

    try:
        report = run_full_scan(bpy.context)
        store_report(report)
    except Exception:
        return

    from .utils.helpers import get_addon_preferences
    prefs = get_addon_preferences(bpy.context)
    if prefs:
        show_on_warn = prefs.show_popup_on_warning
        show_on_crit = prefs.show_popup_on_critical
    else:
        show_on_warn = True
        show_on_crit = True

    if report.overall_risk == 'critical' and show_on_crit:
        bpy.app.timers.register(_invoke_warning_popup, first_interval=0.1)
    elif report.overall_risk == 'warning' and show_on_warn:
        bpy.app.timers.register(_invoke_warning_popup, first_interval=0.1)


def render_started_handler(scene, *args):
    """Write the forensic log when the render starts."""
    from .core.tier import has_feature
    if not has_feature('forensics_logger'):
        return
    try:
        from .core.forensics import write_forensic_log
        write_forensic_log(bpy.context)
    except Exception:
        pass


def render_ended_handler(scene, *args):
    """Delete the forensic log when the render successfully completes."""
    try:
        from .core.forensics import delete_forensic_log
        delete_forensic_log()
    except Exception:
        pass


# SRG_FIX_2: Define render_cancelled_handler wrapper
def render_cancelled_handler(scene, *args):
    """Write cancellation message when render is cancelled."""
    try:
        from .core.forensics import render_cancelled_handler as _handler
        _handler(scene, *args)
    except Exception:
        pass


# SRG_VALIDATOR: Auto-run validation before every render job
def srg_pre_render_validator(scene, *args):
    """Runs scene validation once at render job start and warns if critical."""
    from .core.tier import has_feature
    if not has_feature('pre_render_auto_validate'):
        return
    import bpy
    from .core.validator import validate_scene
    
    context = bpy.context
    results = validate_scene(context)
    
    if results['severity'] == 'CRITICAL':
        print("[SRG] 🔴 CRITICAL pre-render issues detected:")
        for lib in results['missing_libraries']:
            print(f"[SRG]   Missing library: {lib['name']} → {lib['filepath']}")
        for d in results['broken_drivers']:
            print(f"[SRG]   Broken driver: {d['owner']} → {d['path']}")
        print("[SRG]   Render may crash. Check SRG panel for details.")
    elif results['severity'] == 'WARNING':
        print(f"[SRG] ⚠ {results['total_issues']} pre-render warning(s). Monitor render closely.")
    else:
        print("[SRG] ✓ Pre-render validation passed.")


# SRG_FIX_4: CLI Auto-Pilot with explicit stdout confirmation messages and safety aborts
def check_cli_args():
    """CLI Auto-Pilot is only available in Smart Render Guard Pro."""
    return None


def register():
    """Register all Smart Render Guard classes and handlers."""
    properties.register()
    preferences.register()
    operators.register()
    ui.register()

    # Attach pre-render handlers
    if pre_render_check not in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.append(pre_render_check)

    # SRG_FIX_2: Use render_init (fires once per job) not render_pre (fires per frame)
    if render_started_handler not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(render_started_handler)

    # SRG_VALIDATOR: Register auto-validator on render_init
    if srg_pre_render_validator not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(srg_pre_render_validator)

    # Attach post-render and cancel handlers
    if render_ended_handler not in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.append(render_ended_handler)

    # SRG_FIX_2b: Also handle manual cancellation
    if render_cancelled_handler not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(render_cancelled_handler)

    # Register the CLI check timer
    bpy.app.timers.register(check_cli_args, first_interval=0.5)


def unregister():
    """Unregister all Smart Render Guard classes and handlers."""
    # Remove render handlers
    if pre_render_check in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(pre_render_check)

    # SRG_FIX_2: Match the render_init removal
    if render_started_handler in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.remove(render_started_handler)

    # SRG_VALIDATOR: Match the render_init removal
    if srg_pre_render_validator in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.remove(srg_pre_render_validator)

    if render_ended_handler in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.remove(render_ended_handler)

    # SRG_FIX_2b: Match the render_cancel removal
    if render_cancelled_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(render_cancelled_handler)

    ui.unregister()
    operators.unregister()
    preferences.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
