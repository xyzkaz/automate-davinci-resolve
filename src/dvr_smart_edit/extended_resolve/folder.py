from ..resolve_types import PyRemoteFolder
from .media_pool_item import MediaPoolItem


class FolderPath:
    def __init__(self, _folders: list[PyRemoteFolder]):
        self._folders = _folders

    @property
    def depth(self):
        return len(self._folders)

    @property
    def bottom(self):
        return self._folders[-1]

    def get_names(self):
        return [_folder.GetName() for _folder in self._folders]


class Folder:
    def __init__(self, folder_path: FolderPath):
        self._folder = folder_path.bottom
        self.folder_path = folder_path

    def find_item(self, condition):
        return next(self.iter_items(condition), None)

    def find_items(self, condition):
        return list(self.iter_items(condition))

    def iter_items(self, condition=lambda _: True):
        for _item in self._folder.GetClipList():
            item = MediaPoolItem(_item, folder=self)

            if condition(item):
                yield item

    def iter_subfolders(self):
        for _subfolder in self._folder.GetSubFolderList():
            yield Folder(folder_path=FolderPath([*self.folder_path._folders, _subfolder]))
