"""
Smart Render Guard - Mesh Analyzer
====================================
Analyzes all visible mesh objects in the scene to estimate
render-time polygon counts, detect dangerous subdivision
levels, and flag high-risk geometry.

Risk thresholds (per-object final triangle count):
  - < 2,000,000        → safe
  - 2,000,000–5,000,000 → warning
  - > 5,000,000         → critical

Subdivision level thresholds:
  - Levels 1–2  → safe
  - Level 3     → warning
  - Levels 4+   → critical  (exponential memory cost)
"""


def analyze_meshes(context) -> dict:
    """Analyze all visible mesh objects for render-time polygon count.

    Args:
        context: The current Blender context (bpy.context or operator context).

    Returns:
        dict with keys:
            total_tris                    (int)  — Sum of final_tris across all objects.
            objects                       (list) — Per-object analysis dicts.
            subdivision_multiplier_warning (bool) — True if any subsurf render level >= 3.
            highest_risk_object           (str)  — Name of the riskiest object.
    """
    total_tris = 0
    objects_info = []
    subdivision_multiplier_warning = False
    highest_risk_object = ""
    highest_risk_tris = 0

    for obj in context.scene.objects:
        if obj.type != "MESH":
            continue

        # Only consider visible objects
        try:
            if not obj.visible_get():
                continue
        except Exception:
            # If visibility check fails, include the object anyway
            pass

        mesh = obj.data

        # ---------------------------------------------------------------
        # Base triangle count
        # Each polygon with N vertices produces (N - 2) triangles
        # ---------------------------------------------------------------
        base_tris = 0
        try:
            for poly in mesh.polygons:
                base_tris += poly.loop_total - 2
        except Exception:
            # Fallback: estimate from polygon count (assume quads → 2 tris each)
            try:
                base_tris = len(mesh.polygons) * 2
            except Exception:
                base_tris = 0

        # ---------------------------------------------------------------
        # Subdivision modifier detection
        # ---------------------------------------------------------------
        subdivision_levels = 0
        has_multires = False
        final_tris = base_tris

        try:
            for mod in obj.modifiers:
                if mod.type == "SUBSURF":
                    render_level = mod.render_levels
                    subdivision_levels = max(subdivision_levels, render_level)
                    # Each subdivision level quadruples the face count
                    # multiplier = 4^levels applied to base face count
                    multiplier = 4 ** render_level
                    final_tris = base_tris * multiplier

                    if render_level >= 3:
                        subdivision_multiplier_warning = True

                elif mod.type == "MULTIRES":
                    has_multires = True
                    # Multires render levels also multiply geometry
                    try:
                        render_level = mod.render_levels
                        subdivision_levels = max(subdivision_levels, render_level)
                        multiplier = 4 ** render_level
                        final_tris = base_tris * multiplier
                        if render_level >= 3:
                            subdivision_multiplier_warning = True
                    except Exception:
                        pass
        except Exception:
            # If modifier iteration fails, final_tris stays at base_tris
            pass

        # ---------------------------------------------------------------
        # Risk assessment for this object
        # ---------------------------------------------------------------
        if final_tris > 5_000_000:
            risk_level = "critical"
        elif final_tris > 2_000_000:
            risk_level = "warning"
        else:
            risk_level = "safe"

        # Also factor in subdivision level directly
        if subdivision_levels >= 4:
            risk_level = "critical"
        elif subdivision_levels == 3 and risk_level == "safe":
            risk_level = "warning"

        obj_info = {
            "name": obj.name,
            "base_tris": base_tris,
            "final_tris": final_tris,
            "subdivision_levels": subdivision_levels,
            "has_multires": has_multires,
            "risk_level": risk_level,
        }
        objects_info.append(obj_info)
        total_tris += final_tris

        # Track highest risk object
        if final_tris > highest_risk_tris:
            highest_risk_tris = final_tris
            highest_risk_object = obj.name

    return {
        "total_tris": total_tris,
        "objects": objects_info,
        "subdivision_multiplier_warning": subdivision_multiplier_warning,
        "highest_risk_object": highest_risk_object,
    }
