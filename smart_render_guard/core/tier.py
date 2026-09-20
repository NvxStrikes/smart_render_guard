# core/tier.py
# SRG_TIER: Central tier configuration — change CURRENT_TIER per build

# Valid values: 'LITE' | 'BASIC' | 'PRO'
CURRENT_TIER = 'LITE'  # This gets changed per build

TIER_LABELS = {
    'LITE':  'Smart Render Guard Lite (Free)',
    'BASIC': 'Smart Render Guard Basic',
    'PRO':   'Smart Render Guard Pro',
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
        'locate_missing_textures': False,
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
        'locate_missing_textures': True,
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
        'locate_missing_textures': True,
    },
}

def has_feature(feature_name: str) -> bool:
    """
    Call this anywhere in the codebase to check if a feature
    is available in the current tier.
    
    Usage:
        from .core.tier import has_feature
        if not has_feature('texture_downscaler'):
            self.report({'ERROR'}, "Upgrade to Basic to unlock this feature.")
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
                return f"⬆ Upgrade to Basic to unlock this feature. Get it at novastrikes.com"
            else:
                return f"⬆ Upgrade to Pro to unlock this feature. Get it at novastrikes.com"
    return "This feature is not available in your current tier."
