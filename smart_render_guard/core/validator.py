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
