import os

from rofl_toolbox.file_manager.widgets.settings.api.settings import Settings
from rofl_toolbox.data_base_system.sid_interpreter import SidInterpreter, sid_generic

from rofl_toolbox.data_base_system.constants import BDD_DIR
from rofl_toolbox.generic_python.python_generic import Generic

class SidScenePaths(SidInterpreter):
    def __init__(self, sid=sid_generic()):
        SidInterpreter.__init__(self, sid)
        self.refresh_root()
        self.settings = Settings()

    @property
    def project_path(self):
        return os.path.join(BDD_DIR, "{0}.json".format(self.SID_projectAlias))

    @property
    def project_root(self):
        return self._root_project.replace("\\", "/")

    def refresh_root(self):
        if os.path.exists(self.project_path):
            datas = Generic().read_json(data_file=self.project_path)
            self._root_project = datas["path"]
            return True
        return False

    def SID_name_folder(self):
        self.refresh_root()
        namePath = os.path.join(self.project_root, self.SID_name)
        return namePath.replace("\\", "/")

    def SID_task_folder(self):
        taskPath = os.path.join(self.SID_name_folder(), self.SID_task)
        return taskPath.replace("\\", "/")

    def SID_scene_step_folder(self):
        stepPath = os.path.join(self.SID_task_folder(), self.SID_step)
        return stepPath.replace("\\", "/")

    def SID_scene_folder(self):
        scenePath = os.path.join(self.SID_scene_step_folder(), "work")
        return scenePath.replace("\\", "/")

    def SID_scene_folder_settings(self):
        settings_folder = self.settings.get_files_folder()
        scene_folder = self.SID_scene_folder()
        if not settings_folder == self.settings.default_files_folder:
            scene_folder = scene_folder.replace(self.project_root, settings_folder)

        return scene_folder

    def SID_complete_scene_path(self):
        completeScenePath = os.path.join(self.SID_scene_folder(), self.conform_sid_for_file())
        return completeScenePath.replace("\\", "/")

    def SID_images_path(self):
        scene_folder = self.SID_scene_folder_settings()

        imagePath = os.path.join(scene_folder, 'images')
        return imagePath.replace('\\', '/')

    def SID_release_scene_folder(self):
        scenePath = os.path.join(self.SID_scene_step_folder(), "release")
        return scenePath.replace("\\", "/")

    def SID_release_complete_scene_path(self):
        completeScenePath = os.path.join(self.SID_release_scene_folder(), self.conform_sid_for_file())
        return completeScenePath.replace("\\", "/")

    def SID_release_images_path(self):
        imagePath = os.path.join(self.SID_release_scene_folder(), 'images')
        return imagePath.replace('\\', '/')

    def SID_release_asset_folder(self):
        assetPath = os.path.join(self.SID_release_scene_folder(), 'assets')
        return assetPath.replace('\\', '/')

    def SID_release_asset_complete_path(self, file_name):
        extension = os.path.splitext(file_name)[-1]
        extension = ".bgeo" if extension == ".sc" else extension
        extension = extension[1:] if extension.startswith(".") else extension
        completeAssetPath = os.path.join(self.SID_release_asset_folder(), extension, file_name)
        return completeAssetPath.replace("\\", "/")

class SidCachePaths(SidScenePaths):
    def __init__(self, sid=sid_generic()):
        SidScenePaths.__init__(self, sid)

    def SID_cache_folder(self):
        scene_folder = self.SID_scene_folder_settings()

        cache_path = os.path.join(scene_folder, 'caches')
        return cache_path.replace('\\', '/')

    def SID_cache_folder_version(self):
        cache_folder_version = os.path.join(self.SID_cache_folder(), self.SID_version)
        return cache_folder_version.replace('\\', '/')

    def SID_cache_folder_format(self, format):
        cache_folder_format = os.path.join(self.SID_cache_folder_version(), format)
        return cache_folder_format.replace('\\', '/')

    def SID_cache_folder_filename(self, format):
        cache_folder_filename = os.path.join(self.SID_cache_folder_format(format), self.SID_filename)
        return cache_folder_filename.replace('\\', "/")

    def SID_complete_cache_path(self, geo_type="abc", abc_sequence=0):
        extension = geo_type
        if extension == "bgeo":
            extension = "bgeo.sc"

        if abc_sequence == 0 and extension == "abc":
            self.SID = self.sid_replace_frame("")

        filename = self.conform_sid_for_file()
        cache_file = os.path.join(self.SID_cache_folder_filename(geo_type), filename)
        cache_file += "." + extension
        return cache_file.replace('\\', '/')

    def SID_release_cache_folder(self):
        cache_path = os.path.join(self.SID_release_scene_folder(), 'caches')
        return cache_path.replace('\\', '/')

    def SID_release_cache_folder_version(self):
        cache_folder_version = os.path.join(self.SID_release_cache_folder(), self.SID_version)
        return cache_folder_version.replace('\\', '/')

    def SID_release_cache_folder_format(self, format):
        cache_folder_format = os.path.join(self.SID_release_cache_folder_version(), format)
        return cache_folder_format.replace('\\', '/')

    def SID_release_cache_folder_filename(self, format):
        cache_folder_filename = os.path.join(self.SID_release_cache_folder_format(format), self.SID_filename)
        return cache_folder_filename.replace('\\', "/")

    def SID_release_complete_cache_path(self, geo_type="abc", abc_sequence=0):
        extension = geo_type
        if extension == "bgeo":
            extension = "bgeo.sc"

        if abc_sequence == 0 and extension == "abc":
            self.SID = self.sid_replace_frame("")

        filename = self.conform_sid_for_file()
        cache_file = os.path.join(self.SID_release_cache_folder_filename(geo_type), filename)
        cache_file += "." + extension
        return cache_file.replace('\\', '/')

class SidFlipbookPaths(SidScenePaths):
    def __init__(self, sid=sid_generic()):
        SidScenePaths.__init__(self, sid)

    def SID_flipbook_folder(self):
        flipbook_path = os.path.join(self.SID_images_path(), 'flipbooks')
        return flipbook_path.replace('\\', '/')

    def SID_flipbook_folder_version(self):
        flipbook_folder_version = os.path.join(self.SID_flipbook_folder(), self.SID_version)
        return flipbook_folder_version.replace('\\', '/')

    def SID_flipbook_folder_format(self, format="jpg"):
        flipbook_folder_format = os.path.join(self.SID_flipbook_folder_version(), format)
        return flipbook_folder_format.replace('\\', '/')

    def SID_flipbook_folder_filename(self, format="jpg"):
        flipbook_folder_filename = os.path.join(self.SID_flipbook_folder_format(format), self.SID_filename)
        return flipbook_folder_filename.replace('\\', "/")

    def SID_complete_flipbook_path(self, format="jpg"):
        filename = self.conform_sid_for_file()
        flipbook_file = os.path.join(self.SID_flipbook_folder_filename(format), filename)
        flipbook_file += "." + format
        return flipbook_file.replace('\\', '/')

    def SID_complete_blast_path(self, format="jpg"):
        filename = self.conform_sid_for_file()
        flipbook_file = os.path.join(self.SID_flipbook_folder_filename(format), "blast", filename)
        flipbook_file += "." + format
        return flipbook_file.replace('\\', '/')

    def SID_complete_flipbook_mp4_path(self):
        filename = self.conform_sid_for_file()
        flipbook_file = os.path.join(self.SID_flipbook_folder_filename("mp4"), filename)
        flipbook_file += "." + "mp4"
        return flipbook_file.replace('\\', '/')

    def SID_release_flipbook_folder(self):
        flipbook_path = os.path.join(self.SID_release_images_path(), 'flipbooks')
        return flipbook_path.replace('\\', '/')

    def SID_release_flipbook_folder_version(self):
        flipbook_folder_version = os.path.join(self.SID_release_flipbook_folder(), self.SID_version)
        return flipbook_folder_version.replace('\\', '/')

    def SID_release_flipbook_folder_format(self, format="jpg"):
        flipbook_folder_format = os.path.join(self.SID_release_flipbook_folder_version(), format)
        return flipbook_folder_format.replace('\\', '/')

    def SID_release_flipbook_folder_filename(self, format="jpg"):
        flipbook_folder_filename = os.path.join(self.SID_release_flipbook_folder_format(format), self.SID_filename)
        return flipbook_folder_filename.replace('\\', "/")

    def SID_release_complete_flipbook_path(self, format="jpg"):
        filename = self.conform_sid_for_file()
        flipbook_file = os.path.join(self.SID_release_flipbook_folder_filename(format), filename)
        flipbook_file += "." + format
        return flipbook_file.replace('\\', '/')

    def SID_release_complete_flipbook_mp4_path(self):
        filename = self.conform_sid_for_file()
        flipbook_file = os.path.join(self.SID_release_flipbook_folder_filename("mp4"), filename)
        flipbook_file += "." + "mp4"
        return flipbook_file.replace('\\', '/')

class SidRenderPaths(SidScenePaths):
    def __init__(self, sid=sid_generic()):
        SidScenePaths.__init__(self, sid)

    def SID_render_folder(self):
        render_path = os.path.join(self.SID_images_path(), 'renders')
        return render_path.replace('\\', '/')

    def SID_render_folder_version(self):
        render_folder_version = os.path.join(self.SID_render_folder(), self.SID_version)
        return render_folder_version.replace('\\', '/')

    def SID_render_folder_format(self, format="exr"):
        render_folder_format = os.path.join(self.SID_render_folder_version(), format)
        return render_folder_format.replace('\\', '/')

    def SID_render_folder_filename(self, format="exr"):
        render_folder_filename = os.path.join(self.SID_render_folder_format(format), self.SID_filename)
        return render_folder_filename.replace('\\', "/")

    def SID_complete_render_path(self, format="exr"):
        filename = self.conform_sid_for_file()
        render_file = os.path.join(self.SID_render_folder_filename(format), filename)
        render_file += "." + format
        return render_file.replace('\\', '/')

    def SID_release_render_folder(self):
        render_path = os.path.join(self.SID_release_images_path(), 'renders')
        return render_path.replace('\\', '/')

    def SID_release_render_folder_version(self):
        render_folder_version = os.path.join(self.SID_release_render_folder(), self.SID_version)
        return render_folder_version.replace('\\', '/')

    def SID_release_render_folder_format(self, format="exr"):
        render_folder_format = os.path.join(self.SID_release_render_folder_version(), format)
        return render_folder_format.replace('\\', '/')

    def SID_release_render_folder_filename(self, format="exr"):
        render_folder_filename = os.path.join(self.SID_release_render_folder_format(format), self.SID_filename)
        return render_folder_filename.replace('\\', "/")

    def SID_release_complete_render_path(self, format="exr"):
        filename = self.conform_sid_for_file()
        render_file = os.path.join(self.SID_release_render_folder_filename(format=format), filename)
        render_file += "." + format
        return render_file.replace('\\', '/')

class SidWedgerPaths(SidScenePaths):
    def __init__(self, sid=sid_generic()):
        SidScenePaths.__init__(self, sid)

    def SID_wedger_folder(self):
        wedger_path = os.path.join(self.SID_images_path(), "wedges")
        return wedger_path.replace("\\", "/")

    def SID_wedger_folder_version(self):
        wedger_folder_version = os.path.join(self.SID_wedger_folder(), self.SID_version)
        return wedger_folder_version.replace("\\", "/")

    def SID_wedger_folder_session(self, session):
        wedger_session = os.path.join(self.SID_wedger_folder_version(), session)
        return wedger_session.replace("\\", "/")

    def SID_wedger_folder_name(self, session):
        wedger_name = os.path.join(self.SID_wedger_folder_session(session), self.SID_filename)
        return wedger_name.replace("\\", "/")

    def SID_wedger_folder_tmp(self, session):
        wedger_tmp = os.path.join(self.SID_wedger_folder_name(session), "blast")
        return wedger_tmp.replace("\\", "/")

    def SID_complete_wedger_path(self, session, format="jpg"):
        filename = self.conform_sid_for_file()
        wedger_file = os.path.join(self.SID_wedger_folder_name(session), filename)
        wedger_file += "." + format
        return wedger_file.replace("\\", "/")

    def SID_complete_wedger_tmp_path(self, session, format="jpg"):
        filename = self.conform_sid_for_file()
        wedger_file = os.path.join(self.SID_wedger_folder_tmp(session), filename)
        wedger_file += "." + format
        return wedger_file.replace("\\", "/")

    def SID_wedger_scene_complete(self, session):
        filename = self.conform_sid_for_file()
        scene_file = os.path.join(self.SID_wedger_folder_session(session), filename)
        return scene_file.replace("\\", "/")

    def SID_release_wedger_folder(self):
        wedger_path = os.path.join(self.SID_release_images_path(), "wedges")
        return wedger_path.replace("\\", "")

    def SID_release_wedger_folder_version(self):
        wedger_folder_version = os.path.join(self.SID_release_wedger_folder(), self.SID_version)
        return wedger_folder_version.replace("\\", "/")

    def SID_release_wedger_folder_session(self, session):
        wedger_session = os.path.join(self.SID_release_wedger_folder_version(), session)
        return wedger_session.replace("\\", "/")

    def SID_release_wedger_folder_name(self, session):
        wedger_name = os.path.join(self.SID_release_wedger_folder_session(session), self.SID_filename)
        return wedger_name.replace("\\", "/")

    def SID_release_complete_wedger_path(self, session, format="jpg"):
        filename = self.conform_sid_for_file()
        wedger_file = os.path.join(self.SID_release_wedger_folder_name(session), filename)
        wedger_file += "." + format
        return wedger_file.replace("\\", "/")

    def SID_release_wedger_scene_complete(self, session):
        filename = self.conform_sid_for_file()
        scene_file = os.path.join(self.SID_release_wedger_folder_name(session), filename)
        return scene_file.replace("\\", "/")

class SidDailliesPaths(SidWedgerPaths):
    def __init__(self, sid=sid_generic()):
        SidWedgerPaths.__init__(self, sid)

    def SID_daillies_folder(self, session):
        daillies_path = os.path.join(self.SID_wedger_folder_session(session=session), "daillies")
        return daillies_path.replace("\\", "/")

    def SID_complete_daillies_path(self, session):
        filename = self.conform_sid_for_file()
        scene_file = os.path.join(self.SID_daillies_folder(session=session), filename)
        scene_file += ".jpg"
        return scene_file.replace("\\", "/")

    def SID_daillies_folder_mp4(self, session):
        mp4_folder = os.path.join(self.SID_daillies_folder(session=session), "mp4")
        return mp4_folder.replace("\\", "/")

    def SID_complete_daillies_mp4_path(self, session):
        filename = self.conform_sid_for_file()
        mp4_file = os.path.join(self.SID_daillies_folder_mp4(session=session), filename)
        mp4_file += ".mp4"
        return mp4_file.replace("\\", "/")

    def SID_release_daillies_folder(self, session):
        daillies_path = os.path.join(self.SID_release_wedger_folder_session(session=session), "daillies")
        return daillies_path.replace("\\", "/")

    def SID_release_complete_daillies_path(self, session):
        filename = self.conform_sid_for_file()
        scene_file = os.path.join(self.SID_release_daillies_folder(session=session), filename)
        scene_file += ".jpg"
        return scene_file.replace("\\", "/")

    def SID_release_daillies_folder_mp4(self, session):
        mp4_folder = os.path.join(self.SID_release_daillies_folder(session=session), "mp4")
        return mp4_folder.replace("\\", "/")

    def SID_release_complete_daillies_mp4_path(self, session):
        filename = self.conform_sid_for_file()
        mp4_file = os.path.join(self.SID_release_daillies_folder_mp4(session=session), filename)
        mp4_file += ".mp4"
        return mp4_file.replace("\\", "/")

class SidPaths(SidCachePaths, SidFlipbookPaths, SidRenderPaths, SidDailliesPaths):
    def __init__(self, sid=sid_generic()):
        SidCachePaths.__init__(self, sid)
        SidFlipbookPaths.__init__(self, sid)
        SidRenderPaths.__init__(self, sid)
        SidDailliesPaths.__init__(self, sid)


if __name__ == '__main__':
    SID = "myProjects | projet1 | 001 | fx3d | main"
    sid_paths = SidPaths(SID)
    print(sid_paths)