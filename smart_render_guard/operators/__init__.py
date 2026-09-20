"""Smart Render Guard - Operators package.

Registers and unregisters all operator modules:
  - scan_operator:        Scene diagnostic scan
  - fix_operator:         Auto-fix safe issues
  - render_operator:      Safe render with pre-scan
  - preferences_operator: Documentation & preference reset
"""

from . import scan_operator
from . import fix_operator
from . import render_operator
from . import preferences_operator
from . import validate_operator  # SRG_VALIDATOR


def register():
    scan_operator.register()
    fix_operator.register()
    render_operator.register()
    preferences_operator.register()
    validate_operator.register()  # SRG_VALIDATOR


def unregister():
    validate_operator.unregister()  # SRG_VALIDATOR
    preferences_operator.unregister()
    render_operator.unregister()
    fix_operator.unregister()
    scan_operator.unregister()
