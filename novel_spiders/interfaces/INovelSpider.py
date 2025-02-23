from abc import ABC, abstractmethod
from novel_spiders.entities.novel import Novel
from novel_spiders.events.spider_events import SpiderEventListener, SpiderEventDispatcher


class INovelSpider(ABC):
    def __init__(self):
        self._event_dispatcher = SpiderEventDispatcher()

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
        """Asset文件夹路径"""
        return self._asset_dir

    @asset_dir.setter
    def asset_dir(self, value: str) -> None:
        """设置Asset文件夹路径"""
        self._asset_dir = value

    @property
    def data_root(self) -> str:
        """数据根目录"""
        return self._data_root

    @data_root.setter
    def data_root(self, value: str) -> None:
        """设置数据根目录"""
        self._data_root = value

    def add_event_listener(self, listener: SpiderEventListener) -> None:
        """添加事件监听器"""
        self._event_dispatcher.add_listener(listener)

    def remove_event_listener(self, listener: SpiderEventListener) -> None:
        """移除事件监听器"""
        self._event_dispatcher.remove_listener(listener)

    @abstractmethod
    async def get_novel(self, proxy: str = "") -> Novel:
        """获取小说内容"""
        pass
