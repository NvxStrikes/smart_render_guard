"""
Smart Render Guard - Scanner Orchestrator
===========================================
Runs all analyzers (VRAM, RAM, mesh, texture, particle) in
sequence, catches errors per-analyzer so one failure never
kills the entire scan, computes overall risk, and generates
available fix actions.

The last scan report is stored as a module-level variable
(not a scene property) and can be retrieved with get_last_report().
"""

import time
from typing import Optional

from .report import ScanReport, FixAction
from .vram import get_vram_info
from .ram import get_ram_info
from .mesh_analyzer import analyze_meshes
from .texture_analyzer import analyze_textures
from .particle_analyzer import analyze_particles


# Module-level storage for the last scan report
_last_report: Optional[ScanReport] = None


def run_full_scan(context) -> ScanReport:
    """Run all analyzers and produce a unified ScanReport.

    Each analyzer is wrapped in its own try/except so a single
    failure is recorded in report.errors without killing the scan.

    Args:
        context: The current Blender context.

    Returns:
        A fully populated ScanReport instance.
    """
    start = time.time()
    report = ScanReport()

    # ------------------------------------------------------------------
    # Run each analyzer independently
    # ------------------------------------------------------------------
    try:
        report.vram = get_vram_info()
    except Exception as e:
        report.errors.append(f"VRAM scan error: {e}")

    try:
        report.ram = get_ram_info()
    except Exception as e:
        report.errors.append(f"RAM scan error: {e}")

    try:
        report.meshes = analyze_meshes(context)
    except Exception as e:
        report.errors.append(f"Mesh scan error: {e}")

    try:
        report.textures = analyze_textures(context)
    except Exception as e:
        report.errors.append(f"Texture scan error: {e}")

    try:
        report.particles = analyze_particles(context)
    except Exception as e:
        report.errors.append(f"Particle scan error: {e}")

    # ------------------------------------------------------------------
    # Aggregate results
    # ------------------------------------------------------------------
    report.overall_risk = compute_overall_risk(report)
    report.fixes_available = compute_available_fixes(report)
    report.timestamp = time.time()
    report.scan_duration_ms = (time.time() - start) * 1000

    # Store as module-level last report
    global _last_report
    _last_report = report
    return report


def get_last_report() -> Optional[ScanReport]:
    """Retrieve the most recent scan report, or None if no scan has run."""
    return _last_report


def store_report(report: ScanReport):
    """Manually store a report as the last scan result.

    Useful for restoring a report from serialized data or
    updating the stored report after applying fixes.
    """
    global _last_report
    _last_report = report


# ======================================================================
# Risk computation
# ======================================================================

def compute_overall_risk(report: ScanReport) -> str:
    """Determine the overall risk level from all analyzer results.

    Logic:
      - Collect individual risk levels from meshes, textures, particles.
      - Derive VRAM risk from used_percent (default thresholds: 70% warn, 85% crit).
      - Derive RAM risk from used_percent (60% warn, 80% crit).
      - If ANY is critical → overall = critical.
      - If ANY is warning → overall = warning.
      - Otherwise → safe.

    Returns:
        "safe", "warning", or "critical".
    """
    risk_levels = []

    # --- Mesh risk ---
    if report.meshes:
        mesh_risk = _extract_risk(report.meshes)
        if mesh_risk:
            risk_levels.append(mesh_risk)
        # Also check individual objects for critical items
        for obj_info in report.meshes.get("objects", []):
            obj_risk = obj_info.get("risk_level")
            if obj_risk:
                risk_levels.append(obj_risk)

    # --- Texture risk ---
    if report.textures:
        tex_risk = _extract_risk(report.textures)
        if tex_risk:
            risk_levels.append(tex_risk)

    # --- Particle risk ---
    if report.particles:
        part_risk = _extract_risk(report.particles)
        if part_risk:
            risk_levels.append(part_risk)

    # --- VRAM risk (derived from used_percent) ---
    if report.vram and not report.vram.get("detection_failed", True):
        total = report.vram.get("total_mb", 0)
        used = report.vram.get("used_mb", 0)
        if total > 0:
            used_percent = (used / total) * 100.0
            # Default thresholds (could be overridden by preferences)
            if used_percent > 85:
                risk_levels.append("critical")
            elif used_percent > 70:
                risk_levels.append("warning")

    # --- RAM risk (derived from used_percent) ---
    if report.ram and not report.ram.get("detection_failed", True):
        used_percent = report.ram.get("used_percent", 0.0)
        if used_percent > 80:
            risk_levels.append("critical")
        elif used_percent > 60:
            risk_levels.append("warning")

    # --- Aggregate ---
    if "critical" in risk_levels:
        return "critical"
    if "warning" in risk_levels:
        return "warning"
    if risk_levels:
        return "safe"
    return "unknown"


# ======================================================================
# Fix action generation
# ======================================================================

def compute_available_fixes(report: ScanReport) -> list:
    """Generate a list of FixAction objects for auto-fixable issues.

    Currently supported fixes:
      - Reduce subdivision levels > max_level on mesh objects.

    Returns:
        List of FixAction instances.
    """
    fixes = []

    # Get max subsurf level from preferences
    from ..utils.helpers import get_addon_preferences
    prefs = get_addon_preferences()
    max_level = prefs.max_subsurf_autofix if prefs else 2

    # --- Subdivision fixes ---
    if report.meshes:
        for obj_info in report.meshes.get("objects", []):
            subsurf_level = obj_info.get("subdivision_levels", 0)
            if subsurf_level > max_level:
                obj_name = obj_info.get("name", "Unknown")
                fix = FixAction(
                    id=f"fix_subsurf_{obj_name}",
                    label=f"Reduce subdivision on {obj_name}",
                    description=(
                        f"{obj_name} has subdivision level {subsurf_level}. "
                        f"Reducing to level {max_level} will cut face count by "
                        f"{4 ** (subsurf_level - max_level)}x while keeping reasonable detail."
                    ),
                    is_safe=True,
                    operator_id="srg.auto_fix",
                )
                fixes.append(fix)

    return fixes


# ======================================================================
# Internal helpers
# ======================================================================

def _extract_risk(analyzer_result: dict) -> Optional[str]:
    """Safely extract the risk_level key from an analyzer result dict."""
    return analyzer_result.get("risk_level")
