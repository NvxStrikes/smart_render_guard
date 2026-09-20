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

        # Utility Buttons (Header)
        row = layout.row(align=True)
        row.operator("srg.open_docs", text="Documentation & Guide", icon='HELP')
        row.operator("srg.reset_preferences", text="Reset to Defaults", icon='LOOP_BACK')

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


def register():
    bpy.utils.register_class(SRG_AddonPreferences)


def unregister():
    bpy.utils.unregister_class(SRG_AddonPreferences)
