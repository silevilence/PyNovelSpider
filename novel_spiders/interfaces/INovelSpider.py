from abc import ABC, abstractmethod
from novel_spiders.entities.novel import Novel


class INovelSpider(ABC):
    @property
    def resource_name(self) -> str:
        """资源名称"""
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value: str) -> None:
        """设置资源名称"""
        self._resource_name = value

    @property
    def headless(self) -> bool:
        """是否使用无头模式"""
        return self._headless

    @headless.setter
    def headless(self, value: bool) -> None:
        """设置是否使用无头模式"""
        self._headless = value

    @property
    def asset_dir(self) -> str:
        """Aeest文件夹路径"""
        return self._aeest_dir

    @asset_dir.setter
    def asset_dir(self, value: str) -> None:
        """设置Aeest文件夹路径"""
        self._aeest_dir = value

    @property
    def data_root(self) -> str:
        """数据根目录"""
        return self._data_root

    @data_root.setter
    def data_root(self, value: str) -> None:
        """设置数据根目录"""
        self._data_root = value

    @abstractmethod
    async def get_novel(self, proxy: str = "") -> Novel:
        """获取小说内容"""
        pass
