# Smart Render Guard - User Interface
from . import panel
from . import popup
from . import icons


def register():
    icons.register()
    panel.register()
    popup.register()


def unregister():
    popup.unregister()
    panel.unregister()
    icons.unregister()
