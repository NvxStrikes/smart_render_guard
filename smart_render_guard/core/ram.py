"""
Smart Render Guard - RAM Detection
====================================
Detects system RAM total and available memory.

Detection priority:
  1. psutil (imported at function level inside try/except)
  2. Windows fallback via PowerShell Get-CimInstance
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
    # Strategy 2: Windows fallback — PowerShell Get-CimInstance
    # ------------------------------------------------------------------
    if sys.platform == "win32":
        try:
            import json

            result = subprocess.run(
                [
                    "powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_OperatingSystem | "
                    "Select-Object FreePhysicalMemory,TotalVisibleMemorySize | "
                    "ConvertTo-Json"
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            data = json.loads(result.stdout)
            free_kb = int(data.get("FreePhysicalMemory", 0))
            total_kb = int(data.get("TotalVisibleMemorySize", 0))
            if total_kb > 0:
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
