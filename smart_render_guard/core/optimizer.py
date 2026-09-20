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

def purge_garbage(context) -> int:
    """Purge orphan data blocks recursively.

    Returns the number of purged data blocks.
    """
    purged = 0
    try:
        before = len(bpy.data.meshes) + len(bpy.data.images) + len(bpy.data.materials) + len(bpy.data.objects) + len(bpy.data.collections)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        after = len(bpy.data.meshes) + len(bpy.data.images) + len(bpy.data.materials) + len(bpy.data.objects) + len(bpy.data.collections)
        purged = before - after
    except Exception:
        pass
    return max(0, purged)