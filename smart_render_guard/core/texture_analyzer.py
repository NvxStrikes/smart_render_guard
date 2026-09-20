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
