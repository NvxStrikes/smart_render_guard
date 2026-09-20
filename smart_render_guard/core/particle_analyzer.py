"""
Smart Render Guard - Particle Analyzer
========================================
Detects heavy particle and hair systems in the scene.

Risk thresholds (total particle count across all systems):
  - < 500,000    → safe
  - 500K–2,000,000 → warning
  - > 2,000,000   → critical
"""


def analyze_particles(context) -> dict:
    """Analyze all particle systems in the current scene.

    Args:
        context: The current Blender context.

    Returns:
        dict with keys:
            total_particles (int)  — Sum of particle counts across all systems.
            systems         (list) — Per-system info dicts.
            risk_level      (str)  — "safe", "warning", or "critical".
    """
    total_particles = 0
    systems_info = []

    try:
        for obj in context.scene.objects:
            try:
                if not obj.particle_systems:
                    continue
            except Exception:
                continue

            for ps in obj.particle_systems:
                try:
                    settings = ps.settings
                    count = settings.count
                    ptype = settings.type  # 'EMITTER' or 'HAIR'

                    systems_info.append({
                        "object": obj.name,
                        "name": ps.name,
                        "count": count,
                        "type": ptype,
                    })
                    total_particles += count
                except Exception:
                    # Skip this particle system if we can't read its settings
                    continue
    except Exception:
        # If scene object iteration fails entirely, return safe defaults
        pass

    # ---------------------------------------------------------------
    # Overall risk level
    # ---------------------------------------------------------------
    if total_particles > 2_000_000:
        risk_level = "critical"
    elif total_particles > 500_000:
        risk_level = "warning"
    else:
        risk_level = "safe"

    return {
        "total_particles": total_particles,
        "systems": systems_info,
        "risk_level": risk_level,
    }
