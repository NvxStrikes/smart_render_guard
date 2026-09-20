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
