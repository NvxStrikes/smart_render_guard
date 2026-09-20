"""Icon loading infrastructure for Smart Render Guard.

Currently uses Blender's built-in icons. Custom icon loading
can be added here in future versions.
"""

import os
import bpy

# Placeholder for custom icon preview collection
_icon_collection = None


def get_icon(name):
    """Get a custom icon ID by name.
    
    Currently returns 0 (no custom icon) — using Blender built-in icons.
    In future, this will return custom icon IDs from the preview collection.
    """
    return 0


def register():
    global _icon_collection
    # Future: load custom icons here
    # import bpy.utils.previews
    # _icon_collection = bpy.utils.previews.new()
    # icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")
    # _icon_collection.load("shield", os.path.join(icon_dir, "shield.png"), 'IMAGE')
    pass


def unregister():
    global _icon_collection
    # Future: remove custom icons here
    # if _icon_collection:
    #     bpy.utils.previews.remove(_icon_collection)
    _icon_collection = None
