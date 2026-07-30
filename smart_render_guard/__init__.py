"""Smart Render Guard — Beta Build with Time-Lock."""

bl_info = {
    "name": "Smart Render Guard Beta",
    "author": "NovaStrikes",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Properties > Render > Smart Render Guard | N-Panel > Render Guard",
    "description": "Beta testing version of Smart Render Guard with time-limited license.",
    "category": "Render",
    "doc_url": "https://novastrikes.com",
}

# ========================================================
# SRG_BETA: Expiration & Review Settings
BETA_EXPIRATION_DATE = (2026, 8, 29)  # (Year, Month, Day)
BETA_FEEDBACK_URL = "https://forms.gle/v9u5ptPkaWd2V5Qc6"

import datetime
def is_beta_expired() -> bool:
    expiration = datetime.date(*BETA_EXPIRATION_DATE)
    return datetime.date.today() > expiration
# ========================================================


# --- START OF FILE: core/tier.py ---
# core/tier.py
# SRG_TIER: Central tier configuration — change CURRENT_TIER per build

# Valid values: 'LITE' | 'BASIC' | 'PRO'
CURRENT_TIER = 'PRO'  # This gets changed per build

TIER_LABELS = {
    'LITE':  'Smart Render Guard Lite (Free)',
    'BASIC': 'Smart Render Guard Basic ($49)',
    'PRO':   'Smart Render Guard Pro ($99)',
}

TIER_FEATURES = {
    'LITE': {
        'memory_purger':          True,
        'basic_diagnostics':      True,
        'scene_validator_ui':     True,   # Shows results in panel
        'scene_validator_log':    False,  # Does NOT write to forensics log
        'auto_backup':            False,
        'texture_downscaler':     False,
        'geometry_instancer':     False,
        'light_path_throttler':   False,
        'visual_dashboard':       False,
        'forensics_logger':       False,
        'shader_simplifier':      False,
        'shader_restorer':        False,
        'cli_autopilot':          False,
        'pre_render_auto_validate': False,
    },
    'BASIC': {
        'memory_purger':          True,
        'basic_diagnostics':      True,
        'scene_validator_ui':     True,
        'scene_validator_log':    True,   # Writes to forensics log
        'auto_backup':            True,
        'texture_downscaler':     True,
        'geometry_instancer':     True,
        'light_path_throttler':   True,
        'visual_dashboard':       True,
        'forensics_logger':       False,  # No black box logger
        'shader_simplifier':      False,
        'shader_restorer':        False,
        'cli_autopilot':          False,
        'pre_render_auto_validate': False,
    },
    'PRO': {
        'memory_purger':          True,
        'basic_diagnostics':      True,
        'scene_validator_ui':     True,
        'scene_validator_log':    True,
        'auto_backup':            True,
        'texture_downscaler':     True,
        'geometry_instancer':     True,
        'light_path_throttler':   True,
        'visual_dashboard':       True,
        'forensics_logger':       True,
        'shader_simplifier':      True,
        'shader_restorer':        True,
        'cli_autopilot':          True,
        'pre_render_auto_validate': True,
    },
}

def has_feature(feature_name: str) -> bool:
    """
    Call this anywhere in the codebase to check if a feature
    is available in the current tier.
    
    Usage:
        pass # [relative import commented out]: from .core.tier import has_feature
        if not has_feature('texture_downscaler'):
            self.report({'ERROR'}, "Upgrade to Basic ($49) to unlock this feature.")
            return {'CANCELLED'}
    """
    return TIER_FEATURES.get(CURRENT_TIER, {}).get(feature_name, False)

def get_tier_label() -> str:
    """Returns the human-readable tier name for display in UI."""
    return TIER_LABELS.get(CURRENT_TIER, 'Unknown')

def get_upgrade_message(feature_name: str) -> str:
    """
    Returns the correct upgrade message for a locked feature.
    Shows which tier unlocks it.
    """
    # Find the lowest tier that has this feature
    for tier in ['BASIC', 'PRO']:
        if TIER_FEATURES[tier].get(feature_name, False):
            if tier == 'BASIC':
                return f"⬆ Upgrade to Basic ($49) to unlock this feature. Get it at novastrikes.com"
            else:
                return f"⬆ Upgrade to Pro ($99) to unlock this feature. Get it at novastrikes.com"
    return "This feature is not available in your current tier."

# --- END OF FILE: core/tier.py ---


# --- START OF FILE: utils/helpers.py ---
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


# --- END OF FILE: utils/helpers.py ---


# --- START OF FILE: core/ram.py ---
"""
Smart Render Guard - RAM Detection
====================================
Detects system RAM total and available memory.

Detection priority:
  1. psutil (imported at function level inside try/except)
  2. Windows fallback via wmic
  3. Linux fallback via /proc/meminfo
  4. macOS fallback via vm_stat + sysctl
  5. Safe defaults on total failure

Every detection method is individually wrapped in try/except
so RAM detection can never crash the addon.
"""

import subprocess
import sys


def get_ram_info() -> dict:
    """Detect system RAM total and available memory.

    Returns:
        dict with keys:
            total_mb         (int)   — Total physical RAM in megabytes.
            available_mb     (int)   — Available RAM in megabytes.
            used_percent     (float) — Percentage of RAM currently in use.
            detection_failed (bool)  — True if all methods failed.
    """

    # ------------------------------------------------------------------
    # Strategy 1: psutil (imported at function level)
    # ------------------------------------------------------------------
    try:
        import psutil  # noqa: F811 — intentionally imported at function level

        mem = psutil.virtual_memory()
        total_mb = int(mem.total / (1024 * 1024))
        available_mb = int(mem.available / (1024 * 1024))
        used_percent = mem.percent
        return {
            "total_mb": total_mb,
            "available_mb": available_mb,
            "used_percent": float(used_percent),
            "detection_failed": False,
        }
    except Exception:
        pass

    # ------------------------------------------------------------------
    # Strategy 2: Windows fallback — wmic
    # ------------------------------------------------------------------
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            lines = [
                ln.strip() for ln in result.stdout.strip().splitlines() if ln.strip()
            ]
            # Output format:
            #   FreePhysicalMemory  TotalVisibleMemorySize
            #   12345678            16777216
            # Values are in kilobytes
            for line in lines:
                parts = line.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    free_kb = int(parts[0])
                    total_kb = int(parts[1])
                    total_mb = total_kb // 1024
                    available_mb = free_kb // 1024
                    used_mb = total_mb - available_mb
                    used_percent = (used_mb / total_mb * 100.0) if total_mb > 0 else 0.0
                    return {
                        "total_mb": total_mb,
                        "available_mb": available_mb,
                        "used_percent": round(used_percent, 1),
                        "detection_failed": False,
                    }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 3: Linux fallback — /proc/meminfo
    # ------------------------------------------------------------------
    if sys.platform.startswith("linux"):
        try:
            meminfo = {}
            with open("/proc/meminfo", "r") as fh:
                for line in fh:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        # Value is typically in kB, e.g. "16384000 kB"
                        val_str = parts[1].strip().split()[0]
                        if val_str.isdigit():
                            meminfo[key] = int(val_str)

            total_kb = meminfo.get("MemTotal", 0)
            available_kb = meminfo.get("MemAvailable", 0)
            # MemAvailable may not exist on very old kernels; fall back to MemFree
            if available_kb == 0:
                available_kb = meminfo.get("MemFree", 0)

            total_mb = total_kb // 1024
            available_mb = available_kb // 1024
            used_mb = total_mb - available_mb
            used_percent = (used_mb / total_mb * 100.0) if total_mb > 0 else 0.0

            if total_mb > 0:
                return {
                    "total_mb": total_mb,
                    "available_mb": available_mb,
                    "used_percent": round(used_percent, 1),
                    "detection_failed": False,
                }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 4: macOS fallback — sysctl + vm_stat
    # ------------------------------------------------------------------
    if sys.platform == "darwin":
        try:
            # Get total RAM via sysctl
            total_result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            total_bytes = int(total_result.stdout.strip())
            total_mb = total_bytes // (1024 * 1024)

            # Get free pages via vm_stat
            available_mb = 0
            try:
                vm_result = subprocess.run(
                    ["vm_stat"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                page_size = 4096  # default macOS page size
                free_pages = 0
                inactive_pages = 0
                for line in vm_result.stdout.splitlines():
                    # Parse "Pages free:   123456."
                    if "page size of" in line:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                page_size = int(part)
                                break
                    if "Pages free" in line:
                        val = line.split(":")[1].strip().rstrip(".")
                        if val.isdigit():
                            free_pages = int(val)
                    if "Pages inactive" in line:
                        val = line.split(":")[1].strip().rstrip(".")
                        if val.isdigit():
                            inactive_pages = int(val)
                available_mb = ((free_pages + inactive_pages) * page_size) // (1024 * 1024)
            except Exception:
                available_mb = 0

            used_mb = total_mb - available_mb
            used_percent = (used_mb / total_mb * 100.0) if total_mb > 0 else 0.0

            if total_mb > 0:
                return {
                    "total_mb": total_mb,
                    "available_mb": available_mb,
                    "used_percent": round(used_percent, 1),
                    "detection_failed": False,
                }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 5: Safe defaults on total failure
    # ------------------------------------------------------------------
    return {
        "total_mb": 0,
        "available_mb": 0,
        "used_percent": 0.0,
        "detection_failed": True,
    }

# --- END OF FILE: core/ram.py ---


# --- START OF FILE: core/vram.py ---
"""
Smart Render Guard - VRAM Detection
=====================================
Detects GPU VRAM total and estimates current usage.

Detection priority:
  1. NVIDIA CUDA via pynvml (imported at function level)
  2. Windows fallback via wmic
  3. Linux fallback via sysfs
  4. macOS fallback via system_profiler
  5. Blender gpu module for GPU name
  6. Safe defaults on total failure

Every detection method is wrapped in its own try/except
so VRAM detection can never crash the addon.
"""

import subprocess
import sys
import os


def get_vram_info() -> dict:
    """Detect GPU VRAM total and estimate current usage.

    Returns:
        dict with keys:
            total_mb        (int)  — Total VRAM in megabytes.
            used_mb         (int)  — Estimated used VRAM in megabytes.
            available_mb    (int)  — Estimated available VRAM in megabytes.
            gpu_name        (str)  — GPU name string.
            detection_failed (bool) — True if all methods failed.
    """

    # ------------------------------------------------------------------
    # Strategy 1: NVIDIA CUDA via pynvml
    # ------------------------------------------------------------------
    try:
        import pynvml  # noqa: F811  — intentionally imported at function level

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(gpu_name, bytes):
            gpu_name = gpu_name.decode("utf-8", errors="replace")

        total_mb = int(mem_info.total / (1024 * 1024))
        used_mb = int(mem_info.used / (1024 * 1024))
        available_mb = total_mb - used_mb

        pynvml.nvmlShutdown()
        return {
            "total_mb": total_mb,
            "used_mb": used_mb,
            "available_mb": available_mb,
            "gpu_name": gpu_name,
            "detection_failed": False,
        }
    except Exception:
        pass

    # ------------------------------------------------------------------
    # Strategy 2: Windows fallback — wmic
    # ------------------------------------------------------------------
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "AdapterRAM"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            lines = [
                ln.strip() for ln in result.stdout.strip().splitlines() if ln.strip()
            ]
            # First line is the header "AdapterRAM", remaining are values
            for line in lines:
                if line.isdigit():
                    total_bytes = int(line)
                    total_mb = total_bytes // (1024 * 1024)
                    gpu_name = _get_gpu_name_wmic()
                    return {
                        "total_mb": total_mb,
                        "used_mb": 0,  # wmic cannot report used VRAM
                        "available_mb": total_mb,
                        "gpu_name": gpu_name,
                        "detection_failed": False,
                    }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 3: Linux fallback — sysfs
    # ------------------------------------------------------------------
    if sys.platform.startswith("linux"):
        try:
            sysfs_path = "/sys/class/drm/card0/device/mem_info_vram_total"
            if os.path.exists(sysfs_path):
                with open(sysfs_path, "r") as fh:
                    total_bytes = int(fh.read().strip())
                total_mb = total_bytes // (1024 * 1024)
                # Try to read used VRAM as well
                used_mb = 0
                used_path = "/sys/class/drm/card0/device/mem_info_vram_used"
                if os.path.exists(used_path):
                    try:
                        with open(used_path, "r") as fh:
                            used_mb = int(fh.read().strip()) // (1024 * 1024)
                    except Exception:
                        pass
                return {
                    "total_mb": total_mb,
                    "used_mb": used_mb,
                    "available_mb": total_mb - used_mb,
                    "gpu_name": _get_gpu_name_blender(),
                    "detection_failed": False,
                }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 4: macOS fallback — system_profiler
    # ------------------------------------------------------------------
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            total_mb = 0
            gpu_name = "Unknown"
            for line in result.stdout.splitlines():
                stripped = line.strip()
                # Parse VRAM line, e.g. "VRAM (Total):  8 GB"
                if "VRAM" in stripped and ("GB" in stripped or "MB" in stripped):
                    parts = stripped.split(":")
                    if len(parts) >= 2:
                        value_str = parts[1].strip()
                        if "GB" in value_str:
                            num = "".join(c for c in value_str if c.isdigit() or c == ".")
                            if num:
                                total_mb = int(float(num) * 1024)
                        elif "MB" in value_str:
                            num = "".join(c for c in value_str if c.isdigit() or c == ".")
                            if num:
                                total_mb = int(float(num))
                # Parse chipset/model line
                if "Chipset Model" in stripped or "Chip" in stripped:
                    parts = stripped.split(":")
                    if len(parts) >= 2:
                        gpu_name = parts[1].strip()

            if total_mb > 0:
                return {
                    "total_mb": total_mb,
                    "used_mb": 0,
                    "available_mb": total_mb,
                    "gpu_name": gpu_name,
                    "detection_failed": False,
                }
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Strategy 5: Blender gpu module for GPU name at minimum
    # ------------------------------------------------------------------
    gpu_name = _get_gpu_name_blender()
    if gpu_name != "Unknown":
        return {
            "total_mb": 0,
            "used_mb": 0,
            "available_mb": 0,
            "gpu_name": gpu_name,
            "detection_failed": True,
        }

    # ------------------------------------------------------------------
    # Strategy 6: Last resort — safe defaults
    # ------------------------------------------------------------------
    return {
        "total_mb": 0,
        "used_mb": 0,
        "available_mb": 0,
        "gpu_name": "Unknown",
        "detection_failed": True,
    }


# ======================================================================
# Internal helpers
# ======================================================================

def _get_gpu_name_wmic() -> str:
    """Try to get GPU name via wmic on Windows."""
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        lines = [
            ln.strip() for ln in result.stdout.strip().splitlines() if ln.strip()
        ]
        for line in lines:
            if line.lower() != "name":
                return line
    except Exception:
        pass
    return _get_gpu_name_blender()


def _get_gpu_name_blender() -> str:
    """Try to get GPU name from Blender's gpu module."""
    try:
        import gpu  # Blender built-in module

        platform_info = gpu.platform
        # Blender 3.x+: gpu.platform.renderer_get()
        if hasattr(platform_info, "renderer_get"):
            return platform_info.renderer_get()
        # Older Blender: gpu.platform.renderer
        if hasattr(platform_info, "renderer"):
            return platform_info.renderer
    except Exception:
        pass
    return "Unknown"

# --- END OF FILE: core/vram.py ---


# --- START OF FILE: core/report.py ---
"""
Smart Render Guard - Report Data Structures
============================================
Defines the dataclasses used to represent scan results
throughout the addon. ScanReport is the primary container
returned by the scanner orchestrator.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FixAction:
    """Represents a single auto-fixable issue.

    Attributes:
        id:          Unique identifier for the fix (e.g. 'fix_subsurf_Cube').
        label:       Human-readable label shown in the UI.
        description: Detailed explanation of what this fix does.
        is_safe:     True if the fix causes no destructive changes.
        operator_id: The bpy operator idname to invoke (e.g. 'srg.auto_fix').
    """
    id: str
    label: str
    description: str
    is_safe: bool  # True = no destructive changes
    operator_id: str  # bpy operator to call


@dataclass
class ScanReport:
    """Complete scan result from Smart Render Guard.

    Each analyser populates its own dict field. The scanner
    orchestrator fills in the aggregate fields (overall_risk,
    fixes_available, timing info).

    Attributes:
        vram:              VRAM detection results from core.vram.
        ram:               RAM detection results from core.ram.
        meshes:            Mesh analysis results from core.mesh_analyzer.
        textures:          Texture analysis results from core.texture_analyzer.
        particles:         Particle analysis results from core.particle_analyzer.
        overall_risk:      Aggregate risk: "safe", "warning", "critical", or "unknown".
        fixes_available:   List of FixAction objects the user can apply.
        timestamp:         Unix timestamp when the scan completed.
        scan_duration_ms:  How long the scan took in milliseconds.
        errors:            Non-fatal errors encountered during the scan.
    """
    vram: dict = field(default_factory=dict)
    ram: dict = field(default_factory=dict)
    meshes: dict = field(default_factory=dict)
    textures: dict = field(default_factory=dict)
    particles: dict = field(default_factory=dict)
    overall_risk: str = "unknown"  # "safe", "warning", "critical", "unknown"
    fixes_available: List[FixAction] = field(default_factory=list)
    timestamp: float = 0.0
    scan_duration_ms: float = 0.0
    errors: List[str] = field(default_factory=list)  # non-fatal scan errors

# --- END OF FILE: core/report.py ---


# --- START OF FILE: core/mesh_analyzer.py ---
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

# --- END OF FILE: core/mesh_analyzer.py ---


# --- START OF FILE: core/texture_analyzer.py ---
"""
Smart Render Guard - Texture Analyzer
=======================================
Estimates total texture memory the render will consume by
walking all materials' node trees and examining TEX_IMAGE nodes.

Memory estimation formula:
  memory_bytes = width × height × 4 channels × (4 bytes if float, else 1 byte)
  memory_mb    = memory_bytes / (1024 × 1024)

Images used in multiple materials are counted only once.

Risk thresholds (total estimated texture memory):
  - < 2048 MB (2 GB)   → safe
  - 2048–4096 MB (2–4 GB) → warning
  - > 4096 MB (4 GB)   → critical

Large texture threshold:
  - Single texture > 100 MB → added to large_textures list
"""

import bpy


def analyze_textures(context) -> dict:
    """Estimate total texture memory consumption for the current scene.

    Args:
        context: The current Blender context.

    Returns:
        dict with keys:
            total_estimated_mb (float) — Total estimated texture memory in MB.
            texture_count      (int)   — Number of unique textures found.
            large_textures     (list)  — List of dicts for textures > 100 MB.
            risk_level         (str)   — "safe", "warning", or "critical".
    """
    total_estimated_mb = 0.0
    texture_count = 0
    large_textures = []
    counted_images = set()  # Track already-counted image names to avoid duplicates

    try:
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            if mat.node_tree is None:
                continue

            for node in mat.node_tree.nodes:
                if node.type != "TEX_IMAGE":
                    continue
                if node.image is None:
                    continue

                img = node.image

                # Avoid double-counting the same image used in multiple materials
                if img.name in counted_images:
                    continue
                counted_images.add(img.name)

                # Get image dimensions
                try:
                    w = img.size[0]
                    h = img.size[1]
                except Exception:
                    continue

                if w == 0 or h == 0:
                    continue

                # Determine bytes per channel based on image data type
                # Float images (HDR, EXR) use 4 bytes per channel
                # Standard images (PNG, JPG) use 1 byte per channel
                is_float = img.is_float
                bytes_per_channel = 4 if is_float else 1
                channels = 4  # Assume RGBA

                memory_bytes = w * h * channels * bytes_per_channel
                memory_mb = memory_bytes / (1024 * 1024)

                total_estimated_mb += memory_mb
                texture_count += 1

                # Build resolution string for reporting
                resolution_str = f"{w}x{h}"

                # Flag large textures (> 100 MB)
                if memory_mb > 100:
                    large_textures.append({
                        "name": img.name,
                        "size_mb": round(memory_mb, 2),
                        "resolution": resolution_str,
                    })
    except Exception:
        # If material/node iteration fails entirely, return safe defaults
        pass

    # ---------------------------------------------------------------
    # Overall risk level
    # ---------------------------------------------------------------
    if total_estimated_mb > 4096:
        risk_level = "critical"
    elif total_estimated_mb > 2048:
        risk_level = "warning"
    else:
        risk_level = "safe"

    return {
        "total_estimated_mb": round(total_estimated_mb, 2),
        "texture_count": texture_count,
        "large_textures": large_textures,
        "risk_level": risk_level,
    }

# --- END OF FILE: core/texture_analyzer.py ---


# --- START OF FILE: core/particle_analyzer.py ---
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

# --- END OF FILE: core/particle_analyzer.py ---


# --- START OF FILE: core/scanner.py ---
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

pass # [relative import commented out]: from .report import ScanReport, FixAction
pass # [relative import commented out]: from .vram import get_vram_info
pass # [relative import commented out]: from .ram import get_ram_info
pass # [relative import commented out]: from .mesh_analyzer import analyze_meshes
pass # [relative import commented out]: from .texture_analyzer import analyze_textures
pass # [relative import commented out]: from .particle_analyzer import analyze_particles


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
    pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences
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

# --- END OF FILE: core/scanner.py ---


# --- START OF FILE: core/optimizer.py ---
"""
Smart Render Guard - Scene Optimization Engine
================================================
Provides core routines to purge unused memory cache,
convert duplicate mesh objects to linked instances,
downscale large textures non-destructively,
throttle Cycles light path bounces, and simplify shader graphs.
"""

import bpy
import os
import json


def backup_blend_file(context) -> str:
    """Save a backup copy of the current .blend file.
    
    Returns the backup path if created, or None.
    """
    # SRG_TIER: Check feature availability
    pass # [relative import commented out]: from .tier import has_feature
    if not has_feature('auto_backup'):
        return None
    pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences, get_srg_data_dir
    prefs = get_addon_preferences(context)
    if prefs and not prefs.create_auto_backup:
        return None

    blend_path = bpy.data.filepath
    if not blend_path:
        # File is unsaved, no backup to make
        return None
    
    import shutil
    data_dir = get_srg_data_dir(context)
    if not data_dir:
        print("Smart Render Guard: Backup failed — Could not create SRG data directory.")
        return None

    _, file_name = os.path.split(blend_path)
    base_name, ext = os.path.splitext(file_name)
    backup_path = os.path.join(data_dir, f"{base_name}_srg_backup{ext}")
    
    try:
        # First save current state
        bpy.ops.wm.save_mainfile()
        # Then copy
        shutil.copy2(blend_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Smart Render Guard: Backup failed: {e}")
        return None


def purge_garbage(context) -> int:
    """Purge orphan data blocks recursively.

    Returns the number of purged data blocks.
    """
    purged = 0
    try:
        # Calculate before count
        before = (
            len(bpy.data.meshes)
            + len(bpy.data.images)
            + len(bpy.data.materials)
            + len(bpy.data.objects)
            + len(bpy.data.collections)
        )
        
        # Call recursive orphans purge
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True
        )
        
        # Calculate after count
        after = (
            len(bpy.data.meshes)
            + len(bpy.data.images)
            + len(bpy.data.materials)
            + len(bpy.data.objects)
            + len(bpy.data.collections)
        )
        purged = before - after
    except Exception:
        pass
    return max(0, purged)


def get_mesh_signature(mesh) -> tuple:
    """Generate a geometric signature tuple for comparing meshes."""
    vert_count = len(mesh.vertices)
    poly_count = len(mesh.polygons)
    if vert_count == 0:
        return None

    # Fast bounds and coordinate summing to detect similarity
    # We round coordinate sums to 4 decimal places to avoid precision errors
    co_sum_x = sum(v.co.x for v in mesh.vertices)
    co_sum_y = sum(v.co.y for v in mesh.vertices)
    co_sum_z = sum(v.co.z for v in mesh.vertices)

    return (
        vert_count,
        poly_count,
        round(co_sum_x, 4),
        round(co_sum_y, 4),
        round(co_sum_z, 4)
    )


def instance_duplicates(context) -> int:
    """Find mesh objects with duplicate geometry and link them as instances.

    Returns the number of objects linked.
    """
    linked_count = 0
    mesh_by_signature = {}

    # Gather mesh objects
    mesh_objects = [
        obj for obj in context.scene.objects
        if obj.type == 'MESH'
        and obj.data
        and not obj.data.shape_keys  # SRG_FIX_1: Skip objects with shape keys to prevent data corruption
    ]

    for obj in mesh_objects:
        # Ignore linked libraries and overrides
        if obj.library or obj.data.library:
            continue

        # SRG_FIX_1b: Skip objects parented to armatures
        if obj.parent and obj.parent.type == 'ARMATURE':
            continue

        sig = get_mesh_signature(obj.data)
        if not sig:
            continue

        if sig not in mesh_by_signature:
            mesh_by_signature[sig] = obj.data
        else:
            target_mesh = mesh_by_signature[sig]
            if obj.data != target_mesh:
                old_mesh = obj.data
                obj.data = target_mesh
                linked_count += 1
                
                # If old mesh now has no users, remove it to free memory
                if old_mesh.users == 0:
                    try:
                        bpy.data.meshes.remove(old_mesh)
                    except Exception:
                        pass

    return linked_count


def downscale_textures(context, max_size=2048) -> list:
    """Downscale all textures that exceed max_size.

    Returns list of str descriptions of resized images.
    """
    # SRG_FIX_3: Collect all images used in World/environment shaders to exclude
    world_images = set()
    for world in bpy.data.worlds:
        if world.node_tree:
            for node in world.node_tree.nodes:
                if node.type == 'TEX_ENVIRONMENT' and node.image:
                    world_images.add(node.image.name)
                if node.type == 'TEX_IMAGE' and node.image:
                    world_images.add(node.image.name)

    resized_images = []

    for img in bpy.data.images:
        # SRG_FIX_3b: Skip Blender internal images that should never be touched
        if img.type in {'RENDER_RESULT', 'COMPOSITING'}:
            continue

        if img.type != 'IMAGE' or img.source != 'FILE':
            continue

        # SRG_FIX_3: Skip World/HDRI environment textures
        if img.name in world_images:
            print(f"[SRG] Skipping World/HDRI texture: {img.name}")
            continue

        w, h = img.size[0], img.size[1]
        if w <= max_size and h <= max_size:
            continue

        # Ignore generated color grids or empty images
        if w == 0 or h == 0:
            continue

        # Calculate new scale
        if w > h:
            new_w = max_size
            new_h = int(h * (max_size / w))
        else:
            new_h = max_size
            new_w = int(w * (max_size / h))

        old_size_str = f"{w}x{h}"
        new_size_str = f"{new_w}x{new_h}"
        filepath = bpy.path.abspath(img.filepath)

        try:
            if filepath and os.path.exists(os.path.dirname(filepath)):
                dir_name, file_name = os.path.split(filepath)
                base_name, ext = os.path.splitext(file_name)

                # Save next to original: wood_srg2048.png
                new_filename = f"{base_name}_srg{max_size}{ext}"
                new_filepath = os.path.join(dir_name, new_filename)

                # SRG_FIX_3: Check if downscaled file already exists to avoid overwriting or redundant work
                if os.path.exists(new_filepath):
                    print(f"[SRG] Skipping downscale for '{img.name}': Downscaled texture '{new_filename}' already exists.")
                    resized_images.append(
                        f"{img.name}: Already downscaled ({new_filename})"
                    )
                    continue

                # Resize in-memory
                img.scale(new_w, new_h)

                if img.packed_file:
                    img.pack()
                    resized_images.append(f"{img.name} (packed): {old_size_str} → {new_size_str}")
                else:
                    img.filepath_raw = new_filepath
                    img.save()
                    img.reload()
                    resized_images.append(
                        f"{img.name}: {old_size_str} → {new_size_str} ({new_filename})"
                    )
            else:
                img.scale(new_w, new_h)
                resized_images.append(f"{img.name} (in-memory): {old_size_str} → {new_size_str}")
        except Exception as e:
            print(f"[SRG] Downscale failed for {img.name}: {e}")

    return resized_images


def throttle_cycles_light_paths(context) -> dict:
    """Throttle Cycles render light path bounces to reduce memory and speed up render.

    Returns a dict with changed settings and their old/new values.
    """
    scene = context.scene
    changes = {}
    if scene.render.engine != 'CYCLES':
        return changes

    cycles = scene.cycles

    # Max bounce caps
    settings_to_cap = {
        "max_bounces": 6,
        "diffuse_bounces": 4,
        "glossy_bounces": 4,
        "transmission_bounces": 6,
        "transparent_max_bounces": 8,
        "volume_bounces": 2,
    }

    for prop, cap in settings_to_cap.items():
        if hasattr(cycles, prop):
            old_val = getattr(cycles, prop)
            if old_val > cap:
                setattr(cycles, prop, cap)
                changes[prop] = f"{old_val} → {cap}"

    # Disable caustics (handles legacy use_caustics and modern caustics_reflective/refractive)
    for prop in ["use_caustics", "caustics_reflective", "caustics_refractive"]:
        if hasattr(cycles, prop) and getattr(cycles, prop):
            setattr(cycles, prop, False)
            changes[prop] = "True → False"

    return changes


def is_flat_image(img, sample_count=100) -> bool:
    """Sample image pixels to determine if it is a single flat color."""
    if not img.pixels:
        return False
    p_len = len(img.pixels)
    if p_len < 4:
        return True

    # Sample pixels at intervals
    step = max(4, p_len // (sample_count * 4)) * 4
    first_pixel = tuple(img.pixels[0:4])

    for i in range(0, p_len, step):
        pixel = tuple(img.pixels[i:i+4])
        # Compare RGBA differences with small tolerance
        if sum(abs(a - b) for a, b in zip(first_pixel, pixel)) > 0.02:
            return False

    return True


def get_average_pixel_value(img, sample_count=100) -> tuple:
    """Return average RGBA tuple of a flat image."""
    if not img.pixels:
        return (1.0, 1.0, 1.0, 1.0)
    p_len = len(img.pixels)
    step = max(4, p_len // (sample_count * 4)) * 4

    r_sum, g_sum, b_sum, a_sum = 0.0, 0.0, 0.0, 0.0
    count = 0
    for i in range(0, p_len, step):
        r_sum += img.pixels[i]
        g_sum += img.pixels[i+1]
        b_sum += img.pixels[i+2]
        a_sum += img.pixels[i+3]
        count += 1

    if count == 0:
        return (1.0, 1.0, 1.0, 1.0)
    return (r_sum/count, g_sum/count, b_sum/count, a_sum/count)


def preview_shader_simplification(context) -> list:
    """Scan all materials and return a preview list of dicts describing what WOULD be simplified, without modifying anything."""
    previews = []
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue
        tree = mat.node_tree
        tex_nodes = [n for n in tree.nodes if n.type == 'TEX_IMAGE' and n.image]
        for node in tex_nodes:
            img = node.image
            if not is_flat_image(img):
                continue
            for out in node.outputs:
                out_links = [l for l in tree.links if l.from_socket == out]
                for link in out_links:
                    img_users = getattr(img, 'users', 1)
                    warning = f" (Shared across {img_users} users)" if img_users > 1 else ""
                    previews.append({
                        "material": mat.name,
                        "image": img.name,
                        "node_name": node.name,
                        "to_node_name": link.to_node.name,
                        "to_socket_name": link.to_socket.name,
                        "location_x": float(node.location.x),
                        "location_y": float(node.location.y),
                        "img_users": img_users,
                        "description": f"{mat.name}: Flat texture '{img.name}' -> '{link.to_node.name} -> {link.to_socket.name}'{warning}"
                    })
    return previews


def simplify_shaders(context) -> list:
    """Scan all materials, find flat image textures, backup if needed, disconnect them, and set BSDF values.

    Saves restoration metadata in material["srg_simplified_textures"].
    """
    simplified = []
    pass # [relative import commented out]: from ..utils.helpers import get_srg_data_dir
    data_dir = get_srg_data_dir(context)
    backup_dir = os.path.join(data_dir, "textures") if data_dir else None

    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue

        tree = mat.node_tree
        # Find all Image Texture nodes that have an image
        tex_nodes = [n for n in tree.nodes if n.type == 'TEX_IMAGE' and n.image]

        for node in tex_nodes:
            img = node.image
            if not is_flat_image(img):
                continue

            avg_color = get_average_pixel_value(img)
            avg_val = (avg_color[0] + avg_color[1] + avg_color[2]) / 3.0

            img_users = getattr(img, 'users', 1)
            if img_users > 1:
                print(f"[SRG] WARNING: Texture '{img.name}' in material '{mat.name}' is shared across {img_users} users.")

            # Find all links outgoing from this node
            links_to_restore = []
            for out in node.outputs:
                # Find links that target this output
                out_links = [l for l in tree.links if l.from_socket == out]
                for link in out_links:
                    links_to_restore.append({
                        "node_name": node.name,
                        "output_name": out.name,
                        "to_node_name": link.to_node.name,
                        "to_socket_name": link.to_socket.name,
                        "image_name": img.name,
                        "image_filepath": img.filepath,
                        "image_is_packed": bool(img.packed_file or img.type == 'COMPOSITING'),
                        "location_x": float(node.location.x),
                        "location_y": float(node.location.y),
                    })

            if not links_to_restore:
                continue

            # Backup the image physically if it is packed or generated (so we can restore it later)
            if img.packed_file or not img.filepath:
                if backup_dir:
                    try:
                        os.makedirs(backup_dir, exist_ok=True)
                        backup_filename = f"{img.name}.png"
                        backup_path = os.path.join(backup_dir, backup_filename)
                        img.file_format = 'PNG'
                        old_filepath = img.filepath_raw
                        img.filepath_raw = backup_path
                        img.save()
                        img.filepath_raw = old_filepath
                        for item in links_to_restore:
                            item["backup_filepath"] = backup_path
                    except Exception as e:
                        print(f"SRG: Failed to save image backup for {img.name}: {e}")
                else:
                    print(f"SRG: Failed to save image backup for {img.name}: SRG data folder unavailable.")

            # Store restoration metadata on the material
            existing_metadata = []
            if "srg_simplified_textures" in mat:
                try:
                    existing_metadata = json.loads(mat["srg_simplified_textures"])
                except Exception:
                    existing_metadata = []

            # Add new links to restore
            existing_metadata.extend(links_to_restore)
            mat["srg_simplified_textures"] = json.dumps(existing_metadata)

            # Apply simplification (disconnect links and set BSDF defaults)
            for item in links_to_restore:
                to_node = tree.nodes.get(item["to_node_name"])
                if to_node:
                    to_socket = to_node.inputs.get(item["to_socket_name"])
                    if to_socket:
                        # Remove existing links to this socket first
                        socket_links = [l for l in tree.links if l.to_socket == to_socket]
                        for l in socket_links:
                            tree.links.remove(l)

                        # Set default value
                        if to_socket.type == 'VALUE':
                            to_socket.default_value = avg_val
                        elif to_socket.type == 'RGBA':
                            to_socket.default_value = avg_color
                            
                        warning_note = f" (Warning: image shared across {img_users} users)" if img_users > 1 else ""
                        simplified.append(
                            f"{mat.name}: Flat texture '{img.name}' replaced on '{to_node.name} -> {to_socket.name}'{warning_note}"
                        )

            # Delete the image node from node tree to free memory
            tree.nodes.remove(node)

    # Force a garbage collection to purge the unused flat image blocks
    if simplified:
        purge_garbage(context)

    return simplified


def restore_simplified_shaders(context) -> list:
    """Read metadata from materials, reload textures, recreate nodes, and restore links."""
    restored = []
    
    for mat in bpy.data.materials:
        if "srg_simplified_textures" not in mat:
            continue
            
        try:
            metadata = json.loads(mat["srg_simplified_textures"])
        except Exception:
            continue
            
        if not metadata or not mat.use_nodes or not mat.node_tree:
            continue
            
        tree = mat.node_tree
        
        for item in metadata:
            node_name = item["node_name"]
            output_name = item["output_name"]
            to_node_name = item["to_node_name"]
            to_socket_name = item["to_socket_name"]
            img_name = item["image_name"]
            img_path = item["image_filepath"]
            backup_path = item.get("backup_filepath")
            
            # Find or reload the image
            img = bpy.data.images.get(img_name)
            if not img:
                # Try reloading from original path or backup path
                path_to_load = img_path
                if backup_path and os.path.exists(backup_path):
                    path_to_load = backup_path
                elif img_path and os.path.exists(bpy.path.abspath(img_path)):
                    path_to_load = img_path
                    
                if path_to_load and os.path.exists(bpy.path.abspath(path_to_load)):
                    try:
                        img = bpy.data.images.load(bpy.path.abspath(path_to_load))
                        img.name = img_name
                        if item.get("image_is_packed") and os.path.exists(bpy.path.abspath(path_to_load)):
                            img.pack()
                    except Exception as e:
                        print(f"SRG: Failed to reload image {img_name}: {e}")
                        
            if not img:
                img = bpy.data.images.new(img_name, width=64, height=64)
                
            # Find or create the Texture node in the shader tree
            tex_node = tree.nodes.get(node_name)
            if not tex_node:
                tex_node = tree.nodes.new("ShaderNodeTexImage")
                tex_node.name = node_name
                tex_node.label = node_name
                
            tex_node.image = img

            # Restore node location in graph layout
            if "location_x" in item and "location_y" in item:
                tex_node.location = (item["location_x"], item["location_y"])
            
            to_node = tree.nodes.get(to_node_name)
            if to_node:
                to_socket = to_node.inputs.get(to_socket_name)
                if to_socket:
                    socket_links = [l for l in tree.links if l.to_socket == to_socket]
                    for l in socket_links:
                        tree.links.remove(l)
                        
                    try:
                        tree.links.new(tex_node.outputs[output_name], to_socket)
                        restored.append(f"{mat.name}: Restored '{img_name}' on '{to_node_name} -> {to_socket_name}'")
                    except Exception as e:
                        print(f"SRG: Link creation failed: {e}")
                        
        del mat["srg_simplified_textures"]
        
    return restored


# --- END OF FILE: core/optimizer.py ---


# --- START OF FILE: core/auto_fixer.py ---
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
    pass # [relative import commented out]: from .optimizer import purge_garbage, instance_duplicates, backup_blend_file

    # Save a backup of the blend file before modifying it
    backup_blend_file(context)

    results = {
        "subdivision_fixes": fix_subdivision_levels(context, max_subsurf_level),
        "particle_warnings": fix_particle_display_count(context),
        "purged_count": purge_garbage(context),
        "instanced_count": instance_duplicates(context),
    }
    return results

# --- END OF FILE: core/auto_fixer.py ---


# --- START OF FILE: core/forensics.py ---
"""
Smart Render Guard - Crash Forensics Engine
================================================
Writes a live scene diagnostics log before rendering starts,
and deletes it upon successful completion. If Blender crashes (OOM),
the file remains on disk to identify the heavy assets.
"""

import bpy
import os
import sys
import time
pass # [relative import commented out]: from .scanner import run_full_scan
pass # [relative import commented out]: from ..utils.helpers import format_number, format_mb


def get_log_filepath() -> str:
    """Determine the filepath for the forensic crash log inside the srg_data folder."""
    pass # [relative import commented out]: from ..utils.helpers import get_srg_data_dir
    data_dir = get_srg_data_dir(bpy.context)
    if not data_dir:
        return None
    blend_path = bpy.data.filepath
    if blend_path:
        _, file_name = os.path.split(blend_path)
        base_name, _ = os.path.splitext(file_name)
        return os.path.join(data_dir, f"{base_name}_srg_crash.log")
    else:
        return os.path.join(data_dir, "unsaved_blend_srg_crash.log")


def write_forensic_log(context) -> str:
    """Generate and write a detailed forensic scan report to disk.

    Returns the path where the log was written.
    """
    filepath = get_log_filepath()
    if not filepath:
        print("[SRG] Failed to write forensic log: SRG data folder unavailable.")
        return None
    
    # Run a full scan to get latest stats
    try:
        report = run_full_scan(context)
    except Exception as e:
        report = None
        scan_error = str(e)
    else:
        scan_error = None

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("             SMART RENDER GUARD - CRASH FORENSIC REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Timestamp:          {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Blender Version:    {bpy.app.version_string}\n")
        f.write(f"OS Platform:        {sys.platform}\n")
        
        blend_file = bpy.data.filepath
        f.write(f"Blend File:         {blend_file if blend_file else 'Unsaved Blend'}\n")
        
        if report:
            f.write("\n" + "-" * 40 + "\n")
            f.write(" SYSTEM RESOURCE DIAGNOSTICS\n")
            f.write("-" * 40 + "\n")
            
            # VRAM
            vram = report.vram
            if vram and not vram.get('detection_failed', False):
                gpu_name = vram.get('gpu_name', 'Unknown')
                total = vram.get('total_mb', 0)
                used = vram.get('used_mb', 0)
                f.write(f"GPU Name:           {gpu_name}\n")
                f.write(f"VRAM Usage:         {format_mb(used)} / {format_mb(total)} ({int(used/total*100) if total > 0 else 0}%)\n")
            else:
                f.write("GPU/VRAM:           Detection failed or hardware not supported\n")

            # RAM
            ram = report.ram
            if ram and not ram.get('detection_failed', False):
                total = ram.get('total_mb', 0)
                avail = ram.get('available_mb', 0)
                used = total - avail
                f.write(f"System RAM Usage:   {format_mb(used)} / {format_mb(total)} ({ram.get('used_percent', 0.0):.1f}%)\n")
            else:
                f.write("System RAM:         Detection failed\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write(" SCENE COMPLEXITY ANALYSIS\n")
            f.write("-" * 40 + "\n")
            
            # Polycount
            meshes = report.meshes
            if meshes:
                f.write(f"Total Triangles:    {format_number(meshes.get('total_tris', 0))} (Render-time estimate)\n")
            
            # Textures
            textures = report.textures
            if textures:
                f.write(f"Texture Memory:     {format_mb(textures.get('total_estimated_mb', 0))} (Est. uncompressed)\n")
                
            # Particles
            particles = report.particles
            if particles:
                f.write(f"Total Particles:    {format_number(particles.get('total_particles', 0))}\n")

            # Top heaviest meshes
            if meshes and meshes.get('objects'):
                f.write("\nTop 5 Heaviest Mesh Objects:\n")
                sorted_meshes = sorted(meshes['objects'], key=lambda x: x.get('final_tris', 0), reverse=True)[:5]
                for i, m in enumerate(sorted_meshes, 1):
                    sub = m.get('subdivision_levels', 0)
                    sub_str = f" [Subsurf L{sub}]" if sub > 0 else ""
                    f.write(f"  {i}. {m['name']}: {format_number(m['final_tris'])} tris{sub_str}\n")

            # Top heaviest textures
            if textures and textures.get('large_textures'):
                f.write("\nTop 5 Largest Textures:\n")
                for i, t in enumerate(textures['large_textures'][:5], 1):
                    f.write(f"  {i}. {t['name']}: {format_mb(t['size_mb'])} ({t['resolution']})\n")

            # SRG_VALIDATOR: Write pre-render validation findings to forensics log
            f.write("\n")
            f.write("-" * 40 + "\n")
            f.write(" PRE-RENDER SCENE VALIDATION\n")
            f.write("-" * 40 + "\n")

            pass # [relative import commented out]: from .tier import has_feature
            if has_feature('scene_validator_log'):
                # Import and run validator
                pass # [relative import commented out]: from .validator import validate_scene
                validation = validate_scene(context)

                f.write(f"Validation Severity:  {validation['severity']}\n")
                f.write(f"Total Issues Found:   {validation['total_issues']}\n")
                f.write("\n")

                # Broken Drivers
                if validation['broken_drivers']:
                    f.write(f"⚠ BROKEN DRIVERS ({len(validation['broken_drivers'])} found):\n")
                    for d in validation['broken_drivers']:
                        muted = " [MUTED]" if d['is_muted'] else ""
                        f.write(f"  • {d['owner']} → {d['path']}{muted}\n")
                    f.write("  ACTION: Open Graph Editor → Drivers tab → delete or fix these.\n")
                    f.write("\n")
                else:
                    f.write("✓ Drivers: No broken drivers found.\n\n")

                # Missing Libraries
                if validation['missing_libraries']:
                    f.write(f"🔴 MISSING LINKED LIBRARIES ({len(validation['missing_libraries'])} found):\n")
                    for lib in validation['missing_libraries']:
                        indirect = " (indirect)" if lib['is_indirect'] else ""
                        f.write(f"  • {lib['name']}{indirect}\n")
                        f.write(f"    Expected at: {lib['filepath']}\n")
                    f.write("  ACTION: File → External Data → Find Missing Files\n")
                    f.write("  or remove the linked objects if no longer needed.\n")
                    f.write("\n")
                else:
                    f.write("✓ Libraries: All linked libraries resolved.\n\n")

                # Missing Textures
                if validation['missing_textures']:
                    f.write(f"⚠ MISSING TEXTURES ({len(validation['missing_textures'])} found):\n")
                    for tex in validation['missing_textures']:
                        f.write(f"  • {tex['name']}\n")
                        f.write(f"    Expected at: {tex['filepath']}\n")
                    f.write("  ACTION: Image Editor → Image → Find Missing Files\n")
                    f.write("\n")
                else:
                    f.write("✓ Textures: All texture files found on disk.\n\n")

                # Heavy Modifiers
                if validation['heavy_modifiers']:
                    f.write(f"⚠ HIGH-RISK MODIFIERS ({len(validation['heavy_modifiers'])} found):\n")
                    for mod in validation['heavy_modifiers']:
                        f.write(f"  • [{mod['risk']}] {mod['object']} → {mod['modifier']} ({mod['type']})\n")
                        f.write(f"    Reason: {mod['reason']}\n")
                    f.write("\n")
                else:
                    f.write("✓ Modifiers: No high-risk modifier combinations detected.\n\n")

                if validation['severity'] == 'SAFE':
                    f.write("✓ Scene passed all pre-render validation checks.\n")
                elif validation['severity'] == 'WARNING':
                    f.write("⚠ Scene has warnings. Render may succeed but monitor closely.\n")
                else:
                    f.write("🔴 CRITICAL issues detected. Render is likely to crash.\n")
                    f.write("   Fix missing libraries and broken drivers BEFORE rendering.\n")
            else:
                f.write("Validation logging is locked in this tier.\n")
                f.write("Upgrade to Basic or Pro to enable pre-render validation logging.\n")

            f.write("\n")

            # Overall Risk
            f.write(f"\nOverall Scan Risk:  {report.overall_risk.upper()}\n")
            
            # Scan errors
            if report.errors:
                f.write("\nScan Warnings/Errors:\n")
                for err in report.errors:
                    f.write(f"  - {err}\n")
        else:
            f.write("\n[ERROR] Full scene diagnostics scan failed during log generation.\n")
            if scan_error:
                f.write(f"Error Message: {scan_error}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write(" END OF REPORT. IF BLENDER CRASHED, CHECK THE HEAVIEST ASSETS LISTED ABOVE.\n")
        f.write("=" * 80 + "\n")

    return filepath


def delete_forensic_log():
    """Delete the forensic log file if it exists."""
    try:
        filepath = get_log_filepath()
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


# SRG_FIX_2: Define render_cancelled_handler to handle manual cancellation
def render_cancelled_handler(scene, *args):
    """Called when the render is cancelled by the user. Preserves the forensic log."""
    print("[SRG] Render cancelled by user. Forensics log preserved.")

# --- END OF FILE: core/forensics.py ---


# --- START OF FILE: core/validator.py ---
# SRG_VALIDATOR
"""Smart Render Guard - Pre-Render Scene Validator.

Scans the scene for common issues that lead to render-time crashes or errors:
1. Broken drivers
2. Missing linked library files
3. Missing external textures
4. High-risk modifier configurations
"""

import os
import bpy
import bmesh


# SRG_VALIDATOR
def validate_scene(context):
    """Runs all scene validation checks and returns a combined report dict.
    
    Returns:
        dict: {
            'has_issues': bool,
            'severity': 'SAFE' | 'WARNING' | 'CRITICAL',
            'broken_drivers': list of dicts,
            'missing_libraries': list of dicts,
            'missing_textures': list of dicts,
            'heavy_modifiers': list of dicts,
            'total_issues': int
        }
    """
    broken_drivers = find_broken_drivers(context)
    missing_libraries = find_missing_libraries(context)
    missing_textures = find_missing_textures(context)
    heavy_modifiers = find_heavy_modifiers(context)

    total_issues = len(broken_drivers) + len(missing_libraries) + len(missing_textures) + len(heavy_modifiers)
    has_issues = total_issues > 0

    # Severity logic
    if len(missing_libraries) > 0 or len(broken_drivers) > 3:
        severity = 'CRITICAL'
    elif len(broken_drivers) > 0 or len(missing_textures) > 0 or len(heavy_modifiers) > 0:
        severity = 'WARNING'
    else:
        severity = 'SAFE'

    return {
        'has_issues': has_issues,
        'severity': severity,
        'broken_drivers': broken_drivers,
        'missing_libraries': missing_libraries,
        'missing_textures': missing_textures,
        'heavy_modifiers': heavy_modifiers,
        'total_issues': total_issues
    }


# SRG_VALIDATOR
def find_broken_drivers(context):
    """Scans all objects, materials, and scene datablocks for broken drivers.
    
    Returns:
        list of dicts: [
            {
                'owner': str,        # Name of the object/datablock owner
                'path': str,         # The broken driver path
                'type': str,         # 'OBJECT' | 'MATERIAL' | 'SCENE' | 'OTHER'
                'is_muted': bool     # Whether driver is muted
            }
        ]
    """
    broken = []

    # 1. Objects
    for obj in bpy.data.objects:
        if obj.animation_data:
            for fcurve in obj.animation_data.drivers:
                if fcurve.driver and not fcurve.driver.is_valid:
                    broken.append({
                        'owner': obj.name,
                        'path': fcurve.data_path,
                        'type': 'OBJECT',
                        'is_muted': fcurve.mute
                    })

    # 2. Materials
    for mat in bpy.data.materials:
        # Material block properties
        if mat.animation_data:
            for fcurve in mat.animation_data.drivers:
                if fcurve.driver and not fcurve.driver.is_valid:
                    broken.append({
                        'owner': mat.name,
                        'path': fcurve.data_path,
                        'type': 'MATERIAL',
                        'is_muted': fcurve.mute
                    })
        # Material node tree properties
        if mat.node_tree and mat.node_tree.animation_data:
            for fcurve in mat.node_tree.animation_data.drivers:
                if fcurve.driver and not fcurve.driver.is_valid:
                    broken.append({
                        'owner': mat.name,
                        'path': fcurve.data_path,
                        'type': 'MATERIAL',
                        'is_muted': fcurve.mute
                    })

    # 3. Worlds
    for world in bpy.data.worlds:
        # World block properties
        if world.animation_data:
            for fcurve in world.animation_data.drivers:
                if fcurve.driver and not fcurve.driver.is_valid:
                    broken.append({
                        'owner': world.name,
                        'path': fcurve.data_path,
                        'type': 'OTHER',
                        'is_muted': fcurve.mute
                    })
        # World node tree properties
        if world.node_tree and world.node_tree.animation_data:
            for fcurve in world.node_tree.animation_data.drivers:
                if fcurve.driver and not fcurve.driver.is_valid:
                    broken.append({
                        'owner': world.name,
                        'path': fcurve.data_path,
                        'type': 'OTHER',
                        'is_muted': fcurve.mute
                    })

    # 4. Scene
    scene = context.scene
    if scene.animation_data:
        for fcurve in scene.animation_data.drivers:
            if fcurve.driver and not fcurve.driver.is_valid:
                broken.append({
                    'owner': scene.name,
                    'path': fcurve.data_path,
                    'type': 'SCENE',
                    'is_muted': fcurve.mute
                })

    return broken


# SRG_VALIDATOR
def find_missing_libraries(context):
    """Checks all linked .blend library files for missing or unresolvable paths.
    
    Returns:
        list of dicts: [
            {
                'name': str,         # Library name in Blender
                'filepath': str,     # The filepath Blender has stored
                'resolved': bool,    # Whether the path resolves to a real file
                'is_indirect': bool  # Whether it's a direct or indirect link
            }
        ]
    """
    missing = []

    for lib in bpy.data.libraries:
        abs_path = bpy.path.abspath(lib.filepath)
        if not os.path.exists(abs_path):
            # Check if any object directly references this library filepath
            is_direct = False
            for obj in bpy.data.objects:
                if obj.library and bpy.path.abspath(obj.library.filepath) == abs_path:
                    is_direct = True
                    break
                if obj.data and hasattr(obj.data, 'library') and obj.data.library:
                    if bpy.path.abspath(obj.data.library.filepath) == abs_path:
                        is_direct = True
                        break
                if obj.instance_type == 'COLLECTION' and obj.instance_collection and obj.instance_collection.library:
                    if bpy.path.abspath(obj.instance_collection.library.filepath) == abs_path:
                        is_direct = True
                        break
            
            missing.append({
                'name': lib.name,
                'filepath': abs_path,
                'resolved': False,
                'is_indirect': not is_direct
            })

    return missing


# SRG_VALIDATOR
def find_missing_textures(context):
    """Finds image textures with broken/missing file paths. Skips packed files.
    
    Returns:
        list of dicts: [
            {
                'name': str,         # Image datablock name
                'filepath': str,     # The stored filepath
                'is_packed': bool    # Always False here
            }
        ]
    """
    missing = []

    for img in bpy.data.images:
        if img.packed_file is not None:
            continue
        if img.source not in {'FILE', 'SEQUENCE', 'MOVIE'}:
            continue
        if not img.filepath:
            continue

        abs_path = bpy.path.abspath(img.filepath)
        if not os.path.exists(abs_path):
            missing.append({
                'name': img.name,
                'filepath': abs_path,
                'is_packed': False
            })

    return missing


# SRG_VALIDATOR
def find_heavy_modifiers(context):
    """Finds objects with modifier stacks known to cause VRAM/RAM spikes.
    
    Returns:
        list of dicts: [
            {
                'object': str,       # Object name
                'modifier': str,     # Modifier name
                'type': str,         # Modifier type
                'risk': str,         # 'HIGH' | 'MEDIUM'
                'reason': str        # Human-readable explanation
            }
        ]
    """
    heavy = []

    for obj in context.scene.objects:
        if obj.type != 'MESH':
            continue

        for mod in obj.modifiers:
            # --- HIGH RISK ---
            
            # SUBSURF render_levels >= 4 on mesh with > 50,000 base tris
            if mod.type == 'SUBSURF' and mod.render_levels >= 4:
                # Candidate-only triangulate logic
                try:
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)
                    bmesh.ops.triangulate(bm, faces=bm.faces)
                    tri_count = len(bm.faces)
                    bm.free()
                except Exception:
                    tri_count = 0

                if tri_count > 50000:
                    multiplier = 4 ** mod.render_levels
                    heavy.append({
                        'object': obj.name,
                        'modifier': mod.name,
                        'type': 'SUBSURF',
                        'risk': 'HIGH',
                        'reason': f"Subdivision level {mod.render_levels} on heavy mesh will multiply geometry {multiplier}x at render time"
                    })

            # DISPLACE with unconnected/missing texture
            elif mod.type == 'DISPLACE' and not mod.texture:
                heavy.append({
                    'object': obj.name,
                    'modifier': mod.name,
                    'type': 'DISPLACE',
                    'risk': 'HIGH',
                    'reason': "Displace modifier has no texture assigned — may cause evaluation error"
                })

            # MULTIRES render_levels >= 4
            elif mod.type == 'MULTIRES' and mod.render_levels >= 4:
                heavy.append({
                    'object': obj.name,
                    'modifier': mod.name,
                    'type': 'MULTIRES',
                    'risk': 'HIGH',
                    'reason': f"Multires level {mod.render_levels} will exponentially increase memory at render time"
                })

            # --- MEDIUM RISK ---

            # ARRAY with count > 100
            elif mod.type == 'ARRAY' and mod.count > 100:
                heavy.append({
                    'object': obj.name,
                    'modifier': mod.name,
                    'type': 'ARRAY',
                    'risk': 'MEDIUM',
                    'reason': f"Large array ({mod.count} instances) increases scene evaluation time"
                })

            # BOOLEAN where cutter object is hidden
            elif mod.type == 'BOOLEAN' and mod.object:
                cutter = mod.object
                # Check if hidden in viewport, hide_render, or hide_get()
                is_hidden = cutter.hide_viewport or cutter.hide_render or cutter.hide_get()
                if is_hidden:
                    heavy.append({
                        'object': obj.name,
                        'modifier': mod.name,
                        'type': 'BOOLEAN',
                        'risk': 'MEDIUM',
                        'reason': "Boolean cutter object is hidden — may cause geometry errors"
                    })

            # PARTICLE_SYSTEM display >= 100% and count > 50,000
            elif mod.type == 'PARTICLE_SYSTEM' and mod.particle_system:
                ps = mod.particle_system
                if ps.settings and ps.settings.display_percentage >= 100 and ps.settings.count > 50000:
                    heavy.append({
                        'object': obj.name,
                        'modifier': mod.name,
                        'type': 'PARTICLE_SYSTEM',
                        'risk': 'MEDIUM',
                        'reason': "Particle system at full display density may spike RAM"
                    })

    return heavy

# --- END OF FILE: core/validator.py ---


# --- START OF FILE: properties.py ---
"""Smart Render Guard - Scene Properties.

Defines the SRG_SceneProperties PropertyGroup that stores scan status,
timing, and user-configurable options at the scene level.
"""

import bpy
import time


def get_scan_status(self):
    """Retrieve scan status dynamically from in-memory ScanReport."""
    pass # [relative import commented out]: from .core.scanner import get_last_report
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
    pass # [relative import commented out]: from .core.scanner import get_last_report
    report = get_last_report()
    if not report or not hasattr(report, 'timestamp') or report.timestamp is None:
        return "Never"
    return time.strftime("%H:%M:%S", time.localtime(report.timestamp))


def get_vram_pct(self):
    """Calculate VRAM percentage dynamically from in-memory ScanReport."""
    pass # [relative import commented out]: from .core.scanner import get_last_report
    report = get_last_report()
    if report and report.vram and not report.vram.get('detection_failed', False):
        total = report.vram.get('total_mb', 0)
        used = report.vram.get('used_mb', 0)
        if total > 0:
            return (used / total) * 100.0
    return 0.0


def get_ram_pct(self):
    """Calculate RAM percentage dynamically from in-memory ScanReport."""
    pass # [relative import commented out]: from .core.scanner import get_last_report
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
    target_texture_size: bpy.props.IntProperty(
        name="Target Texture Size",
        description="Maximum resolution (width/height) of downscaled textures",
        default=2048,
        min=512,
        max=8192
    )
    auto_purge_on_render: bpy.props.BoolProperty(
        name="Auto-Purge on Render",
        description="Automatically purge unused cache and image buffers when rendering starts",
        default=True
    )


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: properties.py ---


# --- START OF FILE: preferences.py ---
"""Smart Render Guard - Addon Preferences.

Defines the SRG_AddonPreferences panel that appears in Edit > Preferences > Add-ons.
Contains threshold settings for VRAM, RAM, triangles, textures, particles,
notification toggles, and auto-fix configuration.
"""

import bpy


class SRG_AddonPreferences(bpy.types.AddonPreferences):
    """Addon preferences for Smart Render Guard."""
    bl_idname = __package__


    # --- VRAM Thresholds ---
    vram_warning_threshold: bpy.props.IntProperty(
        name="VRAM Warning Threshold (%)",
        description="VRAM usage percentage to trigger a warning",
        default=70,
        min=50,
        max=95
    )
    vram_critical_threshold: bpy.props.IntProperty(
        name="VRAM Critical Threshold (%)",
        description="VRAM usage percentage to trigger a critical alert",
        default=85,
        min=70,
        max=100
    )

    # --- RAM Thresholds ---
    ram_warning_threshold: bpy.props.IntProperty(
        name="RAM Warning Threshold (%)",
        description="RAM usage percentage to trigger a warning",
        default=60,
        min=30,
        max=90
    )
    ram_critical_threshold: bpy.props.IntProperty(
        name="RAM Critical Threshold (%)",
        description="RAM usage percentage to trigger a critical alert",
        default=80,
        min=60,
        max=100
    )

    # --- Mesh Thresholds ---
    total_tris_warning: bpy.props.IntProperty(
        name="Triangle Warning (millions)",
        description="Total triangle count (in millions) to trigger a warning",
        default=5,
        min=1
    )
    total_tris_critical: bpy.props.IntProperty(
        name="Triangle Critical (millions)",
        description="Total triangle count (in millions) to trigger a critical alert",
        default=15,
        min=5
    )

    # --- Texture Thresholds ---
    texture_warning_mb: bpy.props.IntProperty(
        name="Texture Warning (MB)",
        description="Total texture memory in MB to trigger a warning",
        default=2048,
        min=512
    )
    texture_critical_mb: bpy.props.IntProperty(
        name="Texture Critical (MB)",
        description="Total texture memory in MB to trigger a critical alert",
        default=4096,
        min=1024
    )

    # --- Particle Thresholds ---
    particle_warning: bpy.props.IntProperty(
        name="Particle Warning Count",
        description="Total particle count to trigger a warning",
        default=500000,
        min=100000
    )
    particle_critical: bpy.props.IntProperty(
        name="Particle Critical Count",
        description="Total particle count to trigger a critical alert",
        default=2000000,
        min=500000
    )

    # --- Notification Settings ---
    show_popup_on_warning: bpy.props.BoolProperty(
        name="Show Popup on Warning",
        description="Display a popup dialog when warnings are found before render",
        default=True
    )
    show_popup_on_critical: bpy.props.BoolProperty(
        name="Show Popup on Critical",
        description="Display a popup dialog when critical issues are found before render",
        default=True
    )

    # --- Auto-Fix Settings ---
    max_subsurf_autofix: bpy.props.IntProperty(
        name="Max Subsurf Level (Auto-Fix)",
        description="Maximum subdivision level to set when auto-fixing",
        default=2,
        min=0,
        max=4
    )

    # --- File Output and Backup Settings ---
    create_auto_backup: bpy.props.BoolProperty(
        name="Create Auto-Backup File",
        description="Create a backup .blend file before applying optimizations",
        default=True
    )
    output_location_type: bpy.props.EnumProperty(
        name="Output Path Mode",
        description="Where to save backups, logs, and texture backups",
        items=[
            ('SAME_DIR', "Next to .blend File", "Create a folder next to the open blend file"),
            ('CUSTOM', "Custom Directory", "Store all backups and crash logs in a specific custom folder")
        ],
        default='SAME_DIR'
    )
    custom_output_dir: bpy.props.StringProperty(
        name="Custom Directory Path",
        description="Path to the custom folder where backups and reports should be stored",
        subtype='DIR_PATH',
        default=""
    )

    def draw(self, context):
        layout = self.layout

        # SRG_BETA: Feedback / review button
        feedback_box = layout.box()
        feedback_box.alert = True
        feedback_box.label(text="🛡 Smart Render Guard Beta Test", icon='QUESTION')
        feedback_box.label(text="Thank you for participating in the beta! Please help us improve the addon by leaving a review.")
        feedback_box.operator("wm.url_open", text="📝 Submit Beta Feedback & Review", icon='URL').url = "https://forms.gle/v9u5ptPkaWd2V5Qc6"

        # VRAM Thresholds
        box = layout.box()
        box.label(text="VRAM Thresholds", icon='INFO')
        row = box.row()
        row.prop(self, "vram_warning_threshold")
        row.prop(self, "vram_critical_threshold")

        # RAM Thresholds
        box = layout.box()
        box.label(text="RAM Thresholds", icon='INFO')
        row = box.row()
        row.prop(self, "ram_warning_threshold")
        row.prop(self, "ram_critical_threshold")

        # Mesh Thresholds
        box = layout.box()
        box.label(text="Mesh Thresholds", icon='MESH_DATA')
        row = box.row()
        row.prop(self, "total_tris_warning")
        row.prop(self, "total_tris_critical")

        # Texture Thresholds
        box = layout.box()
        box.label(text="Texture Thresholds", icon='TEXTURE')
        row = box.row()
        row.prop(self, "texture_warning_mb")
        row.prop(self, "texture_critical_mb")

        # Particle Thresholds
        box = layout.box()
        box.label(text="Particle Thresholds", icon='PARTICLES')
        row = box.row()
        row.prop(self, "particle_warning")
        row.prop(self, "particle_critical")

        # Popup Settings
        box = layout.box()
        box.label(text="Notification Settings", icon='INFO')
        box.prop(self, "show_popup_on_warning")
        box.prop(self, "show_popup_on_critical")

        # Auto-Fix Settings
        box = layout.box()
        box.label(text="Auto-Fix Settings", icon='MODIFIER')
        box.prop(self, "max_subsurf_autofix")

        # File Backup & Output Settings
        box = layout.box()
        box.label(text="File Backup & Output Settings", icon='FILE_FOLDER')
        box.prop(self, "create_auto_backup")
        box.prop(self, "output_location_type")
        if self.output_location_type == 'CUSTOM':
            box.prop(self, "custom_output_dir")


pass # [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: preferences.py ---


# --- START OF FILE: operators/scan_operator.py ---
"""Smart Render Guard - Scan Operator.

Provides SRG_OT_ScanScene which runs the full diagnostic scan on the
current scene, updates the scene properties with results, and tags
all areas for redraw.
"""

import bpy
import time
pass # [relative import commented out]: from ..core.scanner import run_full_scan, store_report


class SRG_OT_ScanScene(bpy.types.Operator):
    """Run Smart Render Guard diagnostic scan on the current scene."""
    bl_idname = "srg.scan_scene"
    bl_label = "Scan Scene"
    bl_description = "Run Smart Render Guard diagnostic scan"

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

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


pass # [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: operators/scan_operator.py ---


# --- START OF FILE: operators/fix_operator.py ---
"""Smart Render Guard - Optimization and Fix Operators.

Provides operators to apply safe automatic fixes, purge memory cache,
instance duplicates, downscale large textures, throttle Cycles bounces,
simplify material shaders, and restore simplified shaders.
"""

import bpy
pass # [relative import commented out]: from ..core.auto_fixer import apply_all_safe_fixes
pass # [relative import commented out]: from ..core.scanner import run_full_scan, store_report


class SRG_OT_AutoFix(bpy.types.Operator):
    """Apply all safe auto-fixes identified by Smart Render Guard."""
    bl_idname = "srg.auto_fix"
    bl_label = "Auto-Fix Safe Issues"
    bl_description = "Apply safe automatic fixes (subdivision reduction)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        max_level = prefs.max_subsurf_autofix if prefs else 2

        results = apply_all_safe_fixes(context, max_subsurf_level=max_level)
        bpy.context.view_layer.update()

        sub_fixes = results.get('subdivision_fixes', [])
        if sub_fixes:
            for fix in sub_fixes:
                self.report({'INFO'}, f"Fixed: {fix}")
            self.report(
                {'INFO'},
                f"Smart Render Guard: {len(sub_fixes)} subdivision(s) reduced"
            )
        else:
            has_subsurf_above_default = False
            for obj in context.scene.objects:
                if obj.type == "MESH":
                    for mod in obj.modifiers:
                        if mod.type == "SUBSURF" and mod.render_levels > 2:
                            has_subsurf_above_default = True
                            break
            
            if has_subsurf_above_default and max_level > 2:
                self.report(
                    {'WARNING'},
                    f"No subdivisions reduced. Max Subsurf Level is set to {max_level} in preferences. "
                    "Set it to 2 or lower under Edit > Preferences > Add-ons > Smart Render Guard to fix L3+ subdivisions."
                )
            else:
                self.report({'INFO'}, "Smart Render Guard: No subdivision fixes needed")

        purged = results.get('purged_count', 0)
        if purged > 0:
            self.report({'INFO'}, f"Smart Render Guard: Purged {purged} orphan data block(s)")

        instanced = results.get('instanced_count', 0)
        if instanced > 0:
            self.report({'INFO'}, f"Smart Render Guard: Linked {instanced} duplicate object(s)")

        p_warnings = results.get('particle_warnings', [])
        for warn in p_warnings:
            self.report({'WARNING'}, f"SRG: {warn}")

        # Re-run scan to update status after a short delay to allow Blender to stabilize
        def _run_scan():
            try:
                report = run_full_scan(context)
                store_report(report)
                for area in context.screen.areas:
                    area.tag_redraw()
            except Exception:
                pass
            return None

        bpy.app.timers.register(_run_scan, first_interval=0.2)
        return {'FINISHED'}


class SRG_OT_PurgeCache(bpy.types.Operator):
    """Purge all unused cache, images, and orphan data blocks from Blender memory."""
    bl_idname = "srg.purge_cache"
    bl_label = "Purge Memory Cache"
    bl_description = "Purge orphan data blocks and clear unused cache/images"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import purge_garbage
        purged = purge_garbage(context)
        self.report({'INFO'}, f"Smart Render Guard: Purged {purged} orphan data block(s)")
        
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class SRG_OT_InstanceMeshes(bpy.types.Operator):
    """Find duplicate mesh objects and link their data to save memory."""
    bl_idname = "srg.instance_meshes"
    bl_label = "Instance Duplicate Objects"
    bl_description = "Convert duplicate meshes to linked instances to save memory"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('geometry_instancer'):
            self.report({'ERROR'}, get_upgrade_message('geometry_instancer'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import instance_duplicates
        linked = instance_duplicates(context)
        if linked > 0:
            self.report({'INFO'}, f"Smart Render Guard: Linked {linked} duplicate object(s)")
        else:
            self.report({'INFO'}, "Smart Render Guard: No duplicate geometry found")
        
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class SRG_OT_DownscaleTextures(bpy.types.Operator):
    """Downscale large textures to save VRAM and prevent render crashes."""
    bl_idname = "srg.downscale_textures"
    bl_label = "Downscale Large Textures"
    bl_description = "Downscale large textures based on target size settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('texture_downscaler'):
            self.report({'ERROR'}, get_upgrade_message('texture_downscaler'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import downscale_textures, backup_blend_file
        srg = context.scene.srg
        max_size = srg.target_texture_size

        # Create auto-backup first before modifying files
        backup_path = backup_blend_file(context)
        if backup_path:
            import os
            self.report({'INFO'}, f"Smart Render Guard: Created scene backup at {os.path.basename(backup_path)}")

        resized = downscale_textures(context, max_size=max_size)
        if resized:
            for item in resized:
                self.report({'INFO'}, f"Resized: {item}")
            self.report({'INFO'}, f"Smart Render Guard: Downscaled {len(resized)} texture(s)")
        else:
            self.report({'INFO'}, f"Smart Render Guard: No textures exceed target size {max_size}px")
        
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}


class SRG_OT_ThrottleBounces(bpy.types.Operator):
    """Throttle Cycles render light path bounces to save VRAM and rendering time."""
    bl_idname = "srg.throttle_bounces"
    bl_label = "Throttle Cycles Bounces"
    bl_description = "Throttle Cycles render light path bounces to save VRAM and rendering time"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('light_path_throttler'):
            self.report({'ERROR'}, get_upgrade_message('light_path_throttler'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import throttle_cycles_light_paths
        changes = throttle_cycles_light_paths(context)
        if changes:
            for prop, val in changes.items():
                self.report({'INFO'}, f"Cycles: {prop} set to {val}")
            self.report({'INFO'}, "Smart Render Guard: Render bounces throttled")
        else:
            self.report({'INFO'}, "Smart Render Guard: Bounces already optimized or scene not using Cycles")
        return {'FINISHED'}


class SRG_OT_SimplifyShaders(bpy.types.Operator):
    """Scan all materials and replace flat-colored textures with direct slider values."""
    bl_idname = "srg.simplify_shaders"
    bl_label = "Simplify Material Shaders"
    bl_description = "Replace flat-colored textures in materials with direct BSDF inputs"
    bl_options = {'REGISTER', 'UNDO'}

    preview_items = []

    def invoke(self, context, event):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('shader_simplifier'):
            self.report({'ERROR'}, get_upgrade_message('shader_simplifier'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import preview_shader_simplification
        previews = preview_shader_simplification(context)
        if not previews:
            self.report({'INFO'}, "Smart Render Guard: No flat textures found to simplify")
            return {'CANCELLED'}

        SRG_OT_SimplifyShaders.preview_items = [p['description'] for p in previews]
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Preview: The following items will be simplified:", icon='INFO')
        for item_desc in SRG_OT_SimplifyShaders.preview_items[:10]:
            box.label(text=f"• {item_desc}")
        if len(SRG_OT_SimplifyShaders.preview_items) > 10:
            box.label(text=f"... and {len(SRG_OT_SimplifyShaders.preview_items) - 10} more items.")
        layout.label(text="Click OK to confirm and simplify shaders.")

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('shader_simplifier'):
            self.report({'ERROR'}, get_upgrade_message('shader_simplifier'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import simplify_shaders, backup_blend_file
        import os

        # Save an auto-backup before destructive shader graph edits
        backup_path = backup_blend_file(context)
        if backup_path:
            self.report({'INFO'}, f"Smart Render Guard: Created scene backup at {os.path.basename(backup_path)}")

        simplified = simplify_shaders(context)
        if simplified:
            for item in simplified:
                if "Warning:" in item or "shared across" in item:
                    self.report({'WARNING'}, item)
                else:
                    self.report({'INFO'}, f"Simplified: {item}")
            self.report({'INFO'}, f"Smart Render Guard: Simplified {len(simplified)} material input(s)")
        else:
            self.report({'INFO'}, "Smart Render Guard: No flat textures found to simplify")
        return {'FINISHED'}


class SRG_OT_RestoreShaders(bpy.types.Operator):
    """Restore previously simplified shaders from material metadata."""
    bl_idname = "srg.restore_shaders"
    bl_label = "Restore Simplified Shaders"
    bl_description = "Reload textures and restore connections for simplified materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('shader_restorer'):
            self.report({'ERROR'}, get_upgrade_message('shader_restorer'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.optimizer import restore_simplified_shaders
        restored = restore_simplified_shaders(context)
        if restored:
            for item in restored:
                self.report({'INFO'}, f"Restored: {item}")
            self.report({'INFO'}, f"Smart Render Guard: Restored {len(restored)} shader input(s)")
        else:
            self.report({'INFO'}, "Smart Render Guard: No simplified shaders to restore")
        return {'FINISHED'}


class SRG_OT_GenerateCrashLog(bpy.types.Operator):
    """Generate a detailed crash forensic report log next to the .blend file."""
    bl_idname = "srg.generate_crash_log"
    bl_label = "Generate Forensic Log"
    bl_description = "Generate a crash forensic diagnostic log next to the blend file"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        # SRG_TIER: Check feature availability
        pass # [relative import commented out]: from ..core.tier import has_feature, get_upgrade_message
        if not has_feature('forensics_logger'):
            self.report({'ERROR'}, get_upgrade_message('forensics_logger'))
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.forensics import write_forensic_log
        import os
        try:
            path = write_forensic_log(context)
            self.report({'INFO'}, f"Smart Render Guard: Forensic report written to: {os.path.basename(path)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate forensic log: {e}")
        return {'FINISHED'}


pass # [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]
# [classes stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: operators/fix_operator.py ---


# --- START OF FILE: operators/render_operator.py ---
"""Smart Render Guard - Safe Render Operator.

Provides SRG_OT_SafeRender which runs a diagnostic scan before starting
the render. If critical issues are found and blocking is enabled, the
render is cancelled. Warning popups are invoked via bpy.app.timers to
ensure they run safely outside the operator context.
"""

import bpy
pass # [relative import commented out]: from ..core.scanner import run_full_scan, store_report


class SRG_OT_SafeRender(bpy.types.Operator):
    """Run Smart Render Guard scan, then start render if safe."""
    bl_idname = "srg.safe_render"
    bl_label = "Safe Render"
    bl_description = "Scan scene for issues before starting render"

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        import time

        # Run full scan
        report = run_full_scan(context)
        store_report(report)



        # If critical and blocking is enabled, show warning instead of rendering
        if (
            report.overall_risk == 'critical'
            and context.scene.srg.block_render_on_critical
        ):
            self.report(
                {'WARNING'},
                "Smart Render Guard: CRITICAL issues found — render blocked"
            )
            # Show popup via timer (safe from operator context)
            bpy.app.timers.register(
                lambda: _invoke_warning_popup() or None,
                first_interval=0.1
            )
            return {'CANCELLED'}

        # If warning/critical, show popup but continue
        if report.overall_risk in ('warning', 'critical'):
            pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences
            prefs = get_addon_preferences(context)
            if prefs:
                show_on_warn = prefs.show_popup_on_warning
                show_on_crit = prefs.show_popup_on_critical
            else:
                show_on_warn = True
                show_on_crit = True

            should_show = (
                (report.overall_risk == 'warning' and show_on_warn)
                or (report.overall_risk == 'critical' and show_on_crit)
            )
            if should_show:
                bpy.app.timers.register(
                    lambda: _invoke_warning_popup() or None,
                    first_interval=0.1
                )
                # Continue to render after showing warning

        # Safe — start render
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}


def _invoke_warning_popup():
    """Helper to invoke the warning popup from a timer."""
    try:
        bpy.ops.srg.show_render_warning('INVOKE_DEFAULT')
    except Exception:
        pass
    return None


pass # [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: operators/render_operator.py ---


# --- START OF FILE: operators/preferences_operator.py ---
"""Smart Render Guard - Preferences Operators.

Provides utility operators for the addon preferences:
  - SRG_OT_OpenDocs:         Opens documentation in a web browser
  - SRG_OT_ResetPreferences: Resets all preferences to default values
    (uses REGISTER + UNDO since it modifies addon state)
"""

import bpy
import webbrowser


class SRG_OT_OpenDocs(bpy.types.Operator):
    """Open the Smart Render Guard documentation in a web browser."""
    bl_idname = "srg.open_docs"
    bl_label = "Open Documentation"
    bl_description = "Open Smart Render Guard documentation"

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        webbrowser.open("https://novastrikes.com/smart-render-guard")
        return {'FINISHED'}


class SRG_OT_ResetPreferences(bpy.types.Operator):
    """Reset Smart Render Guard preferences to default values."""
    bl_idname = "srg.reset_preferences"
    bl_label = "Reset Preferences"
    bl_description = "Reset all Smart Render Guard settings to defaults"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        if prefs:
            prefs.vram_warning_threshold = 70
            prefs.vram_critical_threshold = 85
            prefs.ram_warning_threshold = 60
            prefs.ram_critical_threshold = 80
            prefs.total_tris_warning = 5
            prefs.total_tris_critical = 15
            prefs.texture_warning_mb = 2048
            prefs.texture_critical_mb = 4096
            prefs.particle_warning = 500000
            prefs.particle_critical = 2000000
            prefs.show_popup_on_warning = True
            prefs.show_popup_on_critical = True
            prefs.max_subsurf_autofix = 2
            self.report({'INFO'}, "Smart Render Guard: Preferences reset to defaults")
        else:
            self.report({'ERROR'}, "Could not reset preferences: Preferences object not found")
            return {'CANCELLED'}

        return {'FINISHED'}


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: operators/preferences_operator.py ---


# --- START OF FILE: operators/validate_operator.py ---
# SRG_VALIDATOR
"""Smart Render Guard - Validate Operator.

Provides SRG_OT_RunValidation operator to scan the scene for crash-prone configurations
and cache the results in custom scene properties.
"""

import bpy


# SRG_VALIDATOR
class SRG_OT_RunValidation(bpy.types.Operator):
    bl_idname = "srg.run_validation"
    bl_label = "Run Scene Validation"
    bl_description = "Scan scene for broken drivers, missing files, and high-risk modifiers"
    
    def execute(self, context):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}

        pass # [relative import commented out]: from ..core.validator import validate_scene
        
        results = validate_scene(context)
        
        # Store results in scene custom properties for UI display
        # SRG_VALIDATOR: Cache results in scene props
        context.scene['srg_validation_severity'] = results['severity']
        context.scene['srg_validation_total_issues'] = results['total_issues']
        context.scene['srg_val_broken_drivers'] = len(results['broken_drivers'])
        context.scene['srg_val_missing_libs'] = len(results['missing_libraries'])
        context.scene['srg_val_missing_tex'] = len(results['missing_textures'])
        context.scene['srg_val_heavy_mods'] = len(results['heavy_modifiers'])
        
        # Print summary to console
        print(f"[SRG] Validation complete — Severity: {results['severity']}")
        print(f"[SRG] Broken drivers: {len(results['broken_drivers'])}")
        print(f"[SRG] Missing libraries: {len(results['missing_libraries'])}")
        print(f"[SRG] Missing textures: {len(results['missing_textures'])}")
        print(f"[SRG] High-risk modifiers: {len(results['heavy_modifiers'])}")
        
        # Show popup if CRITICAL
        if results['severity'] == 'CRITICAL':
            self.report({'ERROR'}, 
                f"CRITICAL: {results['total_issues']} issue(s) found. "
                f"Check SRG panel for details. "
                f"Fix before rendering to prevent crashes."
            )
        elif results['severity'] == 'WARNING':
            self.report({'WARNING'}, 
                f"WARNING: {results['total_issues']} issue(s) found. "
                f"Check SRG panel for details."
            )
        else:
            self.report({'INFO'}, "Scene validation passed. Safe to render.")
        
        return {'FINISHED'}


pass # [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: operators/validate_operator.py ---


# --- START OF FILE: ui/popup.py ---
"""Smart Render Guard — Pre-Render Warning Popup.

Displays a modal dialog with scan issues before rendering.
Invoked via bpy.app.timers.register() from the render_pre handler
(never called directly inside the handler).
"""

import bpy
pass # [relative import commented out]: from ..core.scanner import get_last_report
pass # [relative import commented out]: from ..utils.helpers import format_number, format_mb


class SRG_OT_ShowRenderWarning(bpy.types.Operator):
    """Pre-render warning popup for Smart Render Guard."""
    bl_idname = "srg.show_render_warning"
    bl_label = "Smart Render Guard — Pre-Render Warning"

    def invoke(self, context, event):
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}
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
        if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
            self.report({'ERROR'}, "Beta testing period has ended. Please submit feedback.")
            return {'CANCELLED'}
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


pass # [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: ui/popup.py ---


# --- START OF FILE: ui/panel.py ---
"""Smart Render Guard — UI Panels.

Provides two panels:
  1. SRG_PT_MainPanel: Full diagnostics panel in the N-panel sidebar (VIEW_3D).
  2. SRG_PT_RenderProperties: Condensed panel in Render Properties.
"""

import bpy
pass # [relative import commented out]: from ..core.scanner import get_last_report
pass # [relative import commented out]: from ..utils.helpers import format_number, format_mb, risk_icon, risk_label
pass # [relative import commented out]: from ..core.tier import has_feature, CURRENT_TIER


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
        
        # SRG_BETA: Time-lock check
        is_expired = False
        feedback_url = "https://forms.gle/v9u5ptPkaWd2V5Qc6"
        if 'is_beta_expired' in globals():
            is_expired = globals()['is_beta_expired']()
            if 'BETA_FEEDBACK_URL' in globals():
                feedback_url = globals()['BETA_FEEDBACK_URL']
                
        if is_expired:
            box = layout.box()
            box.alert = True
            box.label(text="🔴 BETA PERIOD EXPIRED", icon='CANCEL')
            box.label(text="This beta build has ended. Please submit feedback.")
            box.operator("wm.url_open", text="📝 Submit Beta Feedback & Review", icon='URL').url = feedback_url
            layout = layout.column()
            layout.enabled = False

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

        # Short tips / messages for active Beta users
        if not is_expired:
            tip_box = layout.box()
            tip_box.label(text="💡 Tip: Click SCAN SCENE to analyze risks,", icon='LIGHT')
            tip_box.label(text="   then click SAFE RENDER to validate and run.", icon='NONE')
            
            feedback_row = tip_box.row()
            feedback_row.label(text="📝 Help us improve the final release!")
            feedback_row.operator("wm.url_open", text="Submit Feedback", icon='URL').url = feedback_url

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
                        diag_box.label(text=f"GPU: {gpu_name}", icon='DESKTOP')
                        
                        col = diag_box.column(align=True)
                        col.prop(srg, "vram_pct", text="VRAM Usage", slider=True)
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
                hint.label(text="Upgrade to Basic ($49)", icon='URL')

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
                hint.label(text="Upgrade to Basic ($49)", icon='URL')
            
            # Texture Downscaler
            if has_feature('texture_downscaler'):
                row = opt_box.row(align=True)
                row.operator("srg.downscale_textures", text="Downscale Textures", icon='IMAGE_DATA')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.downscale_textures", text="🔒 Downscale Textures — Basic+", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Basic ($49)", icon='URL')

            # Light Path Throttler
            if has_feature('light_path_throttler'):
                row = opt_box.row(align=True)
                row.operator("srg.throttle_bounces", text="Throttle Cycles Bounces", icon='LIGHT')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.throttle_bounces", text="🔒 Light Path Throttler — Basic+", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Basic ($49)", icon='URL')

            # Shader Simplifier
            if has_feature('shader_simplifier'):
                row = opt_box.row(align=True)
                row.operator("srg.simplify_shaders", text="Simplify Material Shaders", icon='NODE')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.simplify_shaders", text="🔒 Shader Simplifier — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro ($99)", icon='URL')

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
                    hint.label(text="Upgrade to Pro ($99)", icon='URL')

            # Forensics Logger
            if has_feature('forensics_logger'):
                row = opt_box.row(align=True)
                row.operator("srg.generate_crash_log", text="Generate Forensic Log", icon='TEXT')
            else:
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.generate_crash_log", text="🔒 Black Box Logger — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro ($99)", icon='URL')

            # CLI Autopilot placeholder
            if not has_feature('cli_autopilot'):
                row = opt_box.row(align=True)
                row.enabled = False
                row.operator("srg.purge_cache", text="🔒 CLI Autopilot — Pro Only", icon='LOCKED')
                hint = opt_box.row()
                hint.label(text="Upgrade to Pro ($99)", icon='URL')

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
            hint.label(text="Upgrade to Pro ($99)", icon='URL')

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
        pass # [relative import commented out]: from ..utils.helpers import get_addon_preferences
        prefs = get_addon_preferences(context)
        if prefs:
            if has_feature('auto_backup'):
                settings_box.prop(prefs, "create_auto_backup")
            else:
                row = settings_box.row()
                row.enabled = False
                row.prop(prefs, "create_auto_backup", text="🔒 Auto Backup — Basic+")
                hint = settings_box.row()
                hint.label(text="Upgrade to Basic ($49)", icon='URL')

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
            box.label(text="⬆ Unlock Full Suite — from $49", icon='FUND')
            box.operator("wm.url_open", text="Upgrade at novastrikes.com").url = "https://novastrikes.com"
        elif CURRENT_TIER == 'BASIC':
            layout.separator()
            box = layout.box()
            box.label(text="⬆ Unlock Pro Features — $99", icon='FUND')
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
        
        # SRG_BETA: Time-lock check
        is_expired = False
        feedback_url = "https://forms.gle/v9u5ptPkaWd2V5Qc6"
        if 'is_beta_expired' in globals():
            is_expired = globals()['is_beta_expired']()
            if 'BETA_FEEDBACK_URL' in globals():
                feedback_url = globals()['BETA_FEEDBACK_URL']
                
        if is_expired:
            box = layout.box()
            box.alert = True
            box.label(text="🔴 BETA EXPIRED", icon='CANCEL')
            box.operator("wm.url_open", text="📝 Feedback", icon='URL').url = feedback_url
            layout = layout.column()
            layout.enabled = False

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


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# --- END OF FILE: ui/panel.py ---


# --- START OF FILE: __init__.py ---
"""Smart Render Guard — Main Addon Entry Point.

Pre-render diagnostics, crash forensics, and automation for Blender.
"""

# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]
# [bl_info stripped]

import bpy
pass # [relative import commented out]: from . import properties
pass # [relative import commented out]: from . import preferences
pass # [relative import commented out]: from . import operators
pass # [relative import commented out]: from . import ui
pass # [relative import commented out]: from .core.scanner import run_full_scan, store_report, get_last_report


def _invoke_warning_popup():
    """Safely invoke the warning popup from a timer context."""
    try:
        bpy.ops.srg.show_render_warning('INVOKE_DEFAULT')
    except Exception:
        pass
    return None


def pre_render_check(scene, depsgraph=None):
    """Called by Blender's render_pre handler before each render."""
    if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
        print("[SRG] ERROR: Beta testing period has ended. Render blocked.")
        raise RuntimeError("Smart Render Guard: Beta testing period has ended. Please submit feedback.")

    if scene.srg.auto_purge_on_render:
        try:
            pass # [relative import commented out]: from .core.optimizer import purge_garbage
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

    pass # [relative import commented out]: from .utils.helpers import get_addon_preferences
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
    if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
        return
    pass # [relative import commented out]: from .core.tier import has_feature
    if not has_feature('forensics_logger'):
        return
    try:
        pass # [relative import commented out]: from .core.forensics import write_forensic_log
        write_forensic_log(bpy.context)
    except Exception:
        pass


def render_ended_handler(scene, *args):
    """Delete the forensic log when the render successfully completes."""
    try:
        pass # [relative import commented out]: from .core.forensics import delete_forensic_log
        delete_forensic_log()
    except Exception:
        pass


# SRG_FIX_2: Define render_cancelled_handler wrapper
def render_cancelled_handler(scene, *args):
    """Write cancellation message when render is cancelled."""
    try:
        pass # [relative import commented out]: from .core.forensics import render_cancelled_handler as _handler
        _handler(scene, *args)
    except Exception:
        pass


# SRG_VALIDATOR: Auto-run validation before every render job
def srg_pre_render_validator(scene, *args):
    """Runs scene validation once at render job start and warns if critical."""
    if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
        print("[SRG] ERROR: Beta testing period has ended. Render blocked.")
        raise RuntimeError("Smart Render Guard: Beta testing period has ended. Please submit feedback.")

    pass # [relative import commented out]: from .core.tier import has_feature
    if not has_feature('pre_render_auto_validate'):
        return
    import bpy
    pass # [relative import commented out]: from .core.validator import validate_scene
    
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


BETA_DISABLE_CLI_AUTOPILOT = True

# SRG_FIX_4: CLI Auto-Pilot with explicit stdout confirmation messages and safety aborts
def check_cli_args():
    """Check sys.argv for CLI optimization commands."""
    import sys
    import os

    has_auto_optimize = "--srg-auto-optimize" in sys.argv
    has_dry_run = "--srg-dry-run" in sys.argv

    if not (has_auto_optimize or has_dry_run):
        return None

    if 'is_beta_expired' in globals() and globals()['is_beta_expired']():
        print("[SRG] ERROR: Beta testing period has ended.")
        print("[SRG] Please submit feedback and request the latest version.")
        sys.exit(1)

    pass # [relative import commented out]: from .core.tier import has_feature
    if not has_feature('cli_autopilot'):
        print("[SRG] ERROR: CLI Autopilot is a Pro-only feature.")
        print("[SRG] Upgrade to Smart Render Guard Pro ($99) at novastrikes.com")
        print("[SRG] Exiting without modifying the scene.")
        return None

    is_dry_run = has_dry_run

    if not is_dry_run and BETA_DISABLE_CLI_AUTOPILOT:
        print("[SRG] ============================================")
        print("[SRG] Smart Render Guard — CLI Auto-Pilot")
        print("[SRG] NOTICE: Full unattended CLI Autopilot is disabled during beta testing.")
        print("[SRG] Use '--srg-dry-run' to inspect what changes would be made safely.")
        print("[SRG] ============================================")
        return None

    if is_dry_run:
        try:
            blend_filepath = bpy.data.filepath if bpy.data.filepath else "Unsaved Blend"
            print("[SRG] ============================================")
            print("[SRG] Smart Render Guard — CLI Auto-Pilot (DRY RUN)")
            print(f"[SRG] Target file: {blend_filepath}")
            print("[SRG] ============================================")

            print("[SRG] [DRY RUN] Step 1/6 — Scene Backup (Skipped in Dry Run)")

            print("[SRG] [DRY RUN] Step 2/6 — Geometry Instancer Preview...")
            pass # [relative import commented out]: from .core.optimizer import get_mesh_signature
            mesh_objects = [
                obj for obj in bpy.context.scene.objects
                if obj.type == 'MESH' and obj.data and not obj.data.shape_keys and not (obj.parent and obj.parent.type == 'ARMATURE')
            ]
            sigs = {}
            dup_count = 0
            for obj in mesh_objects:
                if obj.library or obj.data.library:
                    continue
                sig = get_mesh_signature(obj.data)
                if sig:
                    if sig in sigs:
                        dup_count += 1
                    else:
                        sigs[sig] = obj.data
            print(f"[SRG] [DRY RUN] Geometry Instancer: Would link {dup_count} duplicate mesh object(s).")

            print("[SRG] [DRY RUN] Step 3/6 — Texture Downscaler Preview...")
            target_size = bpy.context.scene.srg.target_texture_size
            world_images = set()
            for world in bpy.data.worlds:
                if world.node_tree:
                    for node in world.node_tree.nodes:
                        if node.type in {'TEX_ENVIRONMENT', 'TEX_IMAGE'} and node.image:
                            world_images.add(node.image.name)
            oversized_tex = []
            for img in bpy.data.images:
                if img.type == 'IMAGE' and img.source == 'FILE' and img.name not in world_images and img.type not in {'RENDER_RESULT', 'COMPOSITING'}:
                    w, h = img.size[0], img.size[1]
                    if (w > target_size or h > target_size) and w > 0 and h > 0:
                        oversized_tex.append(f"{img.name} ({w}x{h} -> max {target_size}px)")
            if oversized_tex:
                print(f"[SRG] [DRY RUN] Texture Downscaler: Would downscale {len(oversized_tex)} texture(s): {', '.join(oversized_tex)}")
            else:
                print(f"[SRG] [DRY RUN] Texture Downscaler: No textures exceed target size {target_size}px.")

            print("[SRG] [DRY RUN] Step 4/6 — Cycles Light Paths Preview...")
            if bpy.context.scene.render.engine == 'CYCLES':
                cycles = bpy.context.scene.cycles
                settings_to_cap = {
                    "max_bounces": 6,
                    "diffuse_bounces": 4,
                    "glossy_bounces": 4,
                    "transmission_bounces": 6,
                    "transparent_max_bounces": 8,
                    "volume_bounces": 2
                }
                would_change = [
                    f"{prop} ({getattr(cycles, prop)} -> {cap})"
                    for prop, cap in settings_to_cap.items()
                    if hasattr(cycles, prop) and getattr(cycles, prop) > cap
                ]
                if would_change:
                    print(f"[SRG] [DRY RUN] Cycles Light Paths: Would throttle {len(would_change)} setting(s): {', '.join(would_change)}")
                else:
                    print("[SRG] [DRY RUN] Cycles Light Paths: Already optimized.")
            else:
                print("[SRG] [DRY RUN] Cycles Light Paths: Scene not using Cycles.")

            print("[SRG] [DRY RUN] Step 5/6 — Shader Graph Simplifier Preview...")
            pass # [relative import commented out]: from .core.optimizer import preview_shader_simplification
            shader_previews = preview_shader_simplification(bpy.context)
            if shader_previews:
                print(f"[SRG] [DRY RUN] Shader Simplifier: Would simplify {len(shader_previews)} shader input(s):")
                for prev in shader_previews:
                    print(f"[SRG]   - {prev['description']}")
            else:
                print("[SRG] [DRY RUN] Shader Simplifier: No flat textures found to simplify.")

            print("[SRG] [DRY RUN] Step 6/6 — Memory Purger Preview...")
            orphans = len([m for m in bpy.data.meshes if m.users == 0]) + len([i for i in bpy.data.images if i.users == 0]) + len([mat for mat in bpy.data.materials if mat.users == 0])
            print(f"[SRG] [DRY RUN] Memory Purger: Estimated orphan data blocks to purge: {orphans}")

            print("[SRG] ============================================")
            print("[SRG] Smart Render Guard — CLI Auto-Pilot (DRY RUN) COMPLETE")
            print("[SRG] NO CHANGES WERE SAVED TO DISK.")
            print("[SRG] ============================================")
        except Exception as e:
            print(f"[SRG] ✗ Smart Render Guard: CLI dry-run preview failed: {e}")
        return None

    try:
        blend_filepath = bpy.data.filepath if bpy.data.filepath else "Unsaved Blend"
        
        print("[SRG] ============================================")
        print("[SRG] Smart Render Guard — CLI Auto-Pilot STARTED")
        print(f"[SRG] Target file: {blend_filepath}")
        print("[SRG] ============================================")

        # Step 1 — Backup
        print("[SRG] Step 1/6 — Creating scene backup...")
        pass # [relative import commented out]: from .core.optimizer import backup_blend_file
        backup_path = backup_blend_file(bpy.context)
        if backup_path:
            print(f"[SRG] ✓ Backup saved to: {backup_path}")
            print(f"[SRG]   (Your original is SAFE. Restore from backup if needed.)")
        else:
            print("[SRG] ✗ BACKUP FAILED — Aborting pipeline for safety.")
            return None  # SRG_FIX_4: Never proceed without a confirmed backup

        # Step 2 — Geometry Instancer
        print("[SRG] Step 2/6 — Running Geometry Instancer...")
        pass # [relative import commented out]: from .core.optimizer import instance_duplicates
        pass # [relative import commented out]: from .core.auto_fixer import fix_subdivision_levels
        sub_fixes = fix_subdivision_levels(bpy.context)
        if sub_fixes:
            print(f"[SRG] Subdivision fixes applied: {sub_fixes}")
        result = instance_duplicates(bpy.context)
        print(f"[SRG] ✓ Instancer complete: {result}")

        # Step 3 — Texture Downscaler
        print("[SRG] Step 3/6 — Running Texture Downscaler...")
        pass # [relative import commented out]: from .core.optimizer import downscale_textures
        target_size = bpy.context.scene.srg.target_texture_size
        result = downscale_textures(bpy.context, max_size=target_size)
        print(f"[SRG] ✓ Downscaler complete: {result}")

        # Step 4 — Cycles Light Path Throttler
        print("[SRG] Step 4/6 — Throttling Cycles Light Paths...")
        pass # [relative import commented out]: from .core.optimizer import throttle_cycles_light_paths
        result = throttle_cycles_light_paths(bpy.context)
        print(f"[SRG] ✓ Light path throttle complete: {result}")

        # Step 5 — Shader Simplifier
        print("[SRG] Step 5/6 — Running Shader Graph Simplifier...")
        pass # [relative import commented out]: from .core.optimizer import simplify_shaders
        result = simplify_shaders(bpy.context)
        print(f"[SRG] ✓ Shader simplifier complete: {result}")

        # Step 6 — Memory Purger
        print("[SRG] Step 6/6 — Purging orphan data and memory cache...")
        pass # [relative import commented out]: from .core.optimizer import purge_garbage
        result = purge_garbage(bpy.context)
        print(f"[SRG] ✓ Memory purge complete: {result}")

        # Final Save
        print("[SRG] Saving optimized scene...")
        bpy.ops.wm.save_mainfile()
        print(f"[SRG] ✓ Optimized scene saved to: {blend_filepath}")
        print("[SRG] ============================================")
        print("[SRG] Smart Render Guard — CLI Auto-Pilot COMPLETE")
        print(f"[SRG] BACKUP LOCATION: {backup_path}")
        print("[SRG] ============================================")
    except Exception as e:
        print(f"[SRG] ✗ Smart Render Guard: CLI auto-optimization failed: {e}")
    return None


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]


pass # [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]

# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]
# [register/unregister stripped]


if __name__ == "__main__":
    register()

# --- END OF FILE: __init__.py ---


# ========================================================
# SRG_BETA: Compiled registration logic
# ========================================================
import bpy
CLASSES = [
    SRG_SceneProperties,
    SRG_AddonPreferences,
    SRG_OT_ScanScene,
    SRG_OT_AutoFix,
    SRG_OT_PurgeCache,
    SRG_OT_InstanceMeshes,
    SRG_OT_DownscaleTextures,
    SRG_OT_ThrottleBounces,
    SRG_OT_SimplifyShaders,
    SRG_OT_RestoreShaders,
    SRG_OT_GenerateCrashLog,
    SRG_OT_SafeRender,
    SRG_OT_OpenDocs,
    SRG_OT_ResetPreferences,
    SRG_OT_RunValidation,
    SRG_OT_ShowRenderWarning,
    SRG_PT_MainPanel,
    SRG_PT_RenderProperties,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    
    # Initialize scene properties
    bpy.types.Scene.srg = bpy.props.PointerProperty(type=SRG_SceneProperties)

    # Attach handlers
    if pre_render_check not in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.append(pre_render_check)

    if render_started_handler not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(render_started_handler)

    if srg_pre_render_validator not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(srg_pre_render_validator)

    if render_ended_handler not in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.append(render_ended_handler)

    if render_cancelled_handler not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(render_cancelled_handler)

    # CLI check timer
    bpy.app.timers.register(check_cli_args, first_interval=0.5)

def unregister():
    if render_cancelled_handler in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(render_cancelled_handler)
        
    if render_ended_handler in bpy.app.handlers.render_post:
        bpy.app.handlers.render_post.remove(render_ended_handler)
        
    if srg_pre_render_validator in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.remove(srg_pre_render_validator)
        
    if render_started_handler in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.remove(render_started_handler)
        
    if pre_render_check in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(pre_render_check)
        
    if hasattr(bpy.types.Scene, "srg"):
        del bpy.types.Scene.srg
        
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
