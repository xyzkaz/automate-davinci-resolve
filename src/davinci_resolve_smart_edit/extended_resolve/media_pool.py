from typing import Iterable

from ..extended_resolve.media_pool_item import MediaPoolItem
from ..resolve_types import PyRemoteFolder
from .folder import Folder, FolderPath


class MediaPool:
    def __init__(self, media_pool):
        self._media_pool = media_pool

    def get_root_folder(self):
        return Folder(self._media_pool.GetRootFolder())

    def import_bin(self, file_path, parent_folder: Folder):
        self._media_pool.SetCurrentFolder(parent_folder._folder)
        return self._media_pool.ImportFolderFromFile(str(file_path), "")

    def __iter_folder_paths(self, folders: list[PyRemoteFolder]):
        folder_path = FolderPath(folders)

        yield folder_path

        for subfolder in folder_path.bottom.GetSubFolderList():
            yield from self.__iter_folder_paths([*folders, subfolder])

    def _iter_folder_paths(self):
        yield from self.__iter_folder_paths([self._media_pool.GetRootFolder()])

    def find_folder(self, condition) -> Folder | None:
        return next((Folder(p.bottom) for p in self._iter_folder_paths() if condition(p)), None)

    def find_folders(self, condition) -> list[Folder]:
        return [Folder(p.bottom) for p in self._iter_folder_paths() if condition(p)]

    def _iter_items(self, folders):
        current_folder = folders[-1]

        for media_pool_item in current_folder.GetClipList():
            yield media_pool_item, folders

        for subfolder in current_folder.GetSubFolderList():
            yield from self._iter_items(folders + [subfolder])

    def iter_items(self):
        yield from self._iter_items([self._media_pool.GetRootFolder()])

    def find_item(self, condition):
        for item, folders in self.iter_items():
            if condition(item, folders):
                return item

        return None

    def find_items_with_folders(self, condition):
        return [(item, folders) for item, folders in self.iter_items() if condition(item)]

    def find_selected_item(self, condition):
        media_pool_items = self._media_pool.GetSelectedClips()

        if media_pool_items is None:
            return None

        media_pool_item = next((item for item in media_pool_items if condition(item)), None)

        return MediaPoolItem(media_pool_item) if media_pool_item is not None else None

    def move_items(self, items: Iterable[MediaPoolItem], target_folder: Folder):
        self._media_pool.MoveClips([item._item for item in items], target_folder._folder)
