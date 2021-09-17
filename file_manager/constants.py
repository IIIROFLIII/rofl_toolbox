import os

USER_HOME = os.path.expanduser("~")
FC_SETTINGS = os.path.join(USER_HOME, ".FC_settings.json")
SM_SETTINGS = os.path.join(USER_HOME, ".SM_settings.json")
SP_SETTINGS = os.path.join(USER_HOME, ".SP_settings.json")
MP4_FOLDER = os.path.join(USER_HOME, ".mp4_to_seq")

SOFTWARES = ["None", "Houdini"]

MSG = {
    "COMMENTARIES_NOT_GIVEN": "Commentaries were not provide",
    "ENTER_ALIAS": "Please, set an alias project label",
    "ENTER_COMMENTARY": "Please, set a commentary before saving",
    "ENTER_NAME": "Please, set a name scene info",
    "ENTER_PROJECT_PATH": "Please, set a valid project path",
    "ENTER_STEP": "Please, set a step scene info",
    "ENTER_TASK": "Please, set a task scene info",
    "FILE_FORMAT_NOT_MANAGE": "This type of file is not taking in charge",
    "INCREMENT_SCENE": "Increment current scene in a new project ?",
    "NO_EXTENSION": "The given file has no extension",
    "NO_SEQUENCE": "No sequence files found",
    "NO_PROJECT": "No project to delete",
    "NO_WORK_SID": "No Work SID found for",
    "NOT_ENOUGH_SOURCES": "Not Enough Sources Specified",
    "PROJECT_EXIST": "This project already exist",
    "PROJECT_NOT_EXIST": "The project doesn't exist",
    "RESTART": "Please, restart Ui / Software",
    "SAVE_CURRENT_SCENE": "Save current scene in an existing project ?",
    "SAVE_EXISTING_SCENE": "Increment current scene in an existing project ?",
    "SCENE_EXIST": "Scene already exist",
    "SOFTWARE_NOT_GIVEN": "Software were not provide",
    "SELECT_NAME": "Please, select a name first",
    "SELECT_PROJECT": "Please, select a project first",
    "SELECT_STEP": "Please, select a step first",
    "SELECT_SCENE": "Please, select a scene first",
    "SELECT_TASK": "Please, select a task first",
    "SET_ALIAS": "Please, set an alias project",
    "SET_PROJECT_PATH": "Please, set a path project",
    "SID_NOT_COMPLETE": "SID not complete",
    "SOFTWARE_NOT_CONFORM": "The selected scene can't be saved with the software used",
    "SOFTWARE_NOT_MANAGE": "The software used is not managed by the scene manager",
    "TOO_MUCH_SOURCES": "Too Much Sources Specified"
}

if __name__ == '__main__':
    print(SM_SETTINGS)