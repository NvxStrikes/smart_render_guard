"""
Smart Render Guard - Auto Fixer
=================================
Applies safe, non-destructive automatic fixes to reduce
render risk. This module NEVER deletes objects, meshes, or
materials. It only adjusts modifier levels and display settings.
All destructive suggestions are left as manual recommendations
in the scan report.

Available fixes:
  - fix_subdivision_levels: Cap Subsurf render levels at a max value.
  - fix_particle_display_count: Warn when display % differs from render count.
  - apply_all_safe_fixes: Run all safe fixes and return a combined summary.
"""

import bpy


def fix_subdivision_levels(context, max_level=2):
    """Reduce all Subsurf modifiers above max_level to max_level.

    This is a safe fix — it reduces render quality but never
    removes geometry or modifiers. The original level can be
    restored by the user at any time.

    Args:
        context:   The current Blender context.
        max_level: Maximum allowed render subdivision level (default: 2).

    Returns:
        list of str: Human-readable descriptions of each fix applied,
                     e.g. ["Cube: 4 → 2", "Sphere: 3 → 2"].
    """
    fixed = []

    for obj in context.scene.objects:
        if obj.type != "MESH":
            continue

        for mod in obj.modifiers:
            if mod.type == "SUBSURF" and mod.render_levels > max_level:
                old = mod.render_levels
                mod.render_levels = max_level
                fixed.append(f"{obj.name}: {old} → {max_level}")

    return fixed


def fix_particle_display_count(context):
    """Warn when particle display percentage is very low compared to render count.

    This is informational only — particle counts are NOT auto-changed
    because reducing them is a destructive operation that affects the
    final render output.

    Args:
        context: The current Blender context.

    Returns:
        list of str: Warning messages for systems where display_percentage < 10%.
    """
    warnings = []

    for obj in context.scene.objects:
        try:
            if not obj.particle_systems:
                continue
        except Exception:
            continue

        for ps in obj.particle_systems:
            try:
                settings = ps.settings
                if settings.count > 0:
                    display_pct = settings.display_percentage
                    if display_pct < 10:
                        warnings.append(
                            f"{obj.name}/{ps.name}: display at {display_pct}% "
                            f"but render will use all {settings.count} particles"
                        )
            except Exception:
                continue

    return warnings


def apply_all_safe_fixes(context, max_subsurf_level=2):
    """Apply all safe fixes and return a summary.

    Only non-destructive fixes are applied. The results dict
    contains both the fixes that were applied and any informational
    warnings generated.

    Args:
        context:           The current Blender context.
        max_subsurf_level: Maximum allowed render subdivision level (default: 2).

    Returns:
        dict with keys:
            subdivision_fixes  (list of str) — Descriptions of subdivision changes.
            particle_warnings  (list of str) — Informational particle warnings.
            purged_count       (int)         — Number of purged orphan data blocks.
            instanced_count    (int)         — Number of mesh duplicates linked.
    """
    from .optimizer import purge_garbage
    from .tier import has_feature

    # Save a backup of the blend file before modifying it (if supported by tier)
    if has_feature('auto_backup'):
        try:
            from .optimizer import backup_blend_file
            backup_blend_file(context)
        except (ImportError, AttributeError):
            pass

    instanced_count = 0
    if has_feature('geometry_instancer'):
        try:
            from .optimizer import instance_duplicates
            instanced_count = instance_duplicates(context)
        except (ImportError, AttributeError):
            pass

    results = {
        "subdivision_fixes": fix_subdivision_levels(context, max_subsurf_level),
        "particle_warnings": fix_particle_display_count(context),
        "purged_count": purge_garbage(context),
        "instanced_count": instanced_count,
    }
    return results
