from ..resolve_types import PyRemoteFolder
from .media_pool_item import MediaPoolItem


class Folder:
    def __init__(self, _folder: PyRemoteFolder):
        self._folder = _folder

    def find_item(self, condition):
        return next(self.iter_items(condition), None)

    def find_items(self, condition):
        return list(self.iter_items(condition))

    def iter_items(self, condition=lambda _: True):
        for _item in self._folder.GetClipList():
            item = MediaPoolItem(_item)

            if condition(item):
                yield item


class FolderPath:
    def __init__(self, _folders: list[PyRemoteFolder]):
        self._folders = _folders

    @property
    def depth(self):
        return len(self._folders)

    @property
    def bottom(self):
        return self._folders[-1]
