import os

SID_SEPARATOR = " | "
SID_FILE_SEPARATOR = "__"

USER_HOME = os.path.expanduser("~")
from rofl_toolbox.file_manager.widgets.settings.api.settings import Settings
BDD_DIR = os.path.join(Settings().get_bdd_dir(), ".rofl_toolbox_bdd")

CACHES = "caches"
FLIPBOOKS = "flipbooks"
RENDERS = "renders"
WEDGES = "wedges"