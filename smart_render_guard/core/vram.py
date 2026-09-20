"""
Smart Render Guard - VRAM Detection
=====================================
Detects GPU VRAM total and estimates current usage.

Detection priority:
  1. NVIDIA CUDA via pynvml (imported at function level)
  2. Windows fallback via PowerShell Get-CimInstance
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
            "usage_trackable": True,
        }
    except Exception:
        pass

    # ------------------------------------------------------------------
    # Strategy 2: Windows fallback — PowerShell Get-CimInstance
    # ------------------------------------------------------------------
    if sys.platform == "win32":
        try:
            import json

            result = subprocess.run(
                [
                    "powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_VideoController | "
                    "Select-Object Name,AdapterRAM | ConvertTo-Json"
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            data = json.loads(result.stdout)

            # Handle both single object and list of objects (multiple GPUs)
            controllers = [data] if isinstance(data, dict) else (data if isinstance(data, list) else [])

            # Pick the entry with the highest AdapterRAM (discrete GPU over iGPU)
            best_controller = None
            best_ram = -1
            for c in controllers:
                if isinstance(c, dict):
                    ram = c.get("AdapterRAM")
                    if ram is not None:
                        try:
                            ram_val = int(ram)
                            if ram_val > best_ram:
                                best_ram = ram_val
                                best_controller = c
                        except (ValueError, TypeError):
                            pass

            if best_controller and best_ram > 0:
                total_mb = best_ram // (1024 * 1024)
                if total_mb <= 0 or total_mb < 256:  # implausible for a real discrete GPU
                    raise ValueError("Implausible AdapterRAM value, falling through")

                gpu_name = best_controller.get("Name") or _get_gpu_name_blender()
                return {
                    "total_mb": total_mb,
                    "used_mb": 0,  # CIM cannot report used VRAM
                    "available_mb": total_mb,
                    "gpu_name": gpu_name,
                    "detection_failed": False,
                    "usage_trackable": False,
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
                usage_trackable = False
                used_path = "/sys/class/drm/card0/device/mem_info_vram_used"
                if os.path.exists(used_path):
                    try:
                        with open(used_path, "r") as fh:
                            used_mb = int(fh.read().strip()) // (1024 * 1024)
                            usage_trackable = True
                    except Exception:
                        pass
                return {
                    "total_mb": total_mb,
                    "used_mb": used_mb,
                    "available_mb": total_mb - used_mb,
                    "gpu_name": _get_gpu_name_blender(),
                    "detection_failed": False,
                    "usage_trackable": usage_trackable,
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
                    "usage_trackable": False,
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
            "usage_trackable": False,
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
        "usage_trackable": False,
    }


# ======================================================================
# Internal helpers
# ======================================================================

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
