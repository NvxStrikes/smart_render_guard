"""Smart Render Guard — Texture Relink Helper.

Searches the .blend file's directory and subfolders for exact filename matches
to missing texture files and provides manual relinking capabilities.
"""

import os
import bpy
from .validator import find_missing_textures


def find_missing_texture_matches(context) -> dict:
    """For each image in the scene with a broken/missing filepath, search the
    .blend file's directory (recursively) for files with an EXACTLY matching
    filename (case-sensitive match on os.path.basename).

    Returns:
        {
            "image_name_in_blend": ["found/path/1.png", "found/path/2.png"],
            ...
        }
    Only includes images that have at least one match. Images with zero
    matches are omitted (nothing to offer the user for those).
    """
    if not bpy.data.filepath:
        return {}

    blend_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
    if not os.path.isdir(blend_dir):
        return {}

    missing_list = find_missing_textures(context)
    if not missing_list:
        return {}

    # Map target filenames to image datablock names
    target_basenames = {}
    matches = {}
    for item in missing_list:
        img_name = item['name']
        orig_fp = item['filepath']
        basename = os.path.basename(orig_fp)
        if not basename:
            continue
        target_basenames.setdefault(basename, []).append(img_name)
        matches[img_name] = []

    # Recursively traverse blend_dir
    for root, dirs, files in os.walk(blend_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for filename in files:
            if filename in target_basenames:
                full_path = os.path.normpath(os.path.join(root, filename))
                for img_name in target_basenames[filename]:
                    if full_path not in matches[img_name]:
                        matches[img_name].append(full_path)

    # Only include images with at least one match
    return {img_name: paths for img_name, paths in matches.items() if len(paths) > 0}


def relink_image(image_name: str, chosen_path: str) -> bool:
    """Relinks the given image datablock to chosen_path.
    Called only after the user has explicitly picked a path in the UI —
    never called automatically.
    Returns True on success, False if the image datablock or path is invalid.
    """
    img = bpy.data.images.get(image_name)
    if not img:
        return False

    if not chosen_path or not os.path.isfile(chosen_path):
        return False

    try:
        if bpy.data.filepath:
            img.filepath = bpy.path.relpath(chosen_path)
        else:
            img.filepath = chosen_path
        img.reload()
        return True
    except Exception:
        return False
