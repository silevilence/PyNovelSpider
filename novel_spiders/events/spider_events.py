from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Protocol, Union

class SpiderEventType(Enum):
    """爬虫事件类型枚举"""

    INFO_PAGE_START = "info_page_start"
    """开始爬取信息页。无数据。"""
    
    INFO_PAGE_COMPLETE = "info_page_complete"
    """信息页爬取完成。数据类型: NovelInfoData"""
    
    CHAPTERS_START = "chapters_start"
    """开始爬取章节。数据类型: int (总章节数)"""
    
    CHAPTER_COMPLETE = "chapter_complete"
    """单章爬取完成。数据类型: ChapterProgressData"""
    
    COMPLETE = "complete"
    """全部完成。无数据。"""
    
    ERROR = "error"
    """发生错误。数据类型: Exception"""

@dataclass
class ChapterProgressData:
    """章节进度数据"""

    current: int
    """当前已完成章节数"""

    total: int
    """总章节数"""

    latest_chapter: str
    """最新完成的章节标题"""

@dataclass
class NovelInfoData:
    """小说信息数据"""

    title: str
    """小说标题"""

    author: str
    """作者名"""

    chapter_count: int
    """章节总数"""

# 事件数据的联合类型
SpiderEventData = Union[NovelInfoData, ChapterProgressData, int, None]

@dataclass
class SpiderEvent:
    """爬虫事件"""

    type: SpiderEventType
    """事件类型"""

    data: SpiderEventData = None
    """事件数据。根据事件类型不同，数据类型也不同：
    - INFO_PAGE_START: None
    - INFO_PAGE_COMPLETE: NovelInfoData
    - CHAPTERS_START: int (总章节数)
    - CHAPTER_COMPLETE: ChapterProgressData
    - COMPLETE: None
    - ERROR: None 
    """

    error: Optional[Exception] = None
    """错误信息。仅在事件类型为ERROR时有效。"""

class SpiderEventListener(Protocol):
    """爬虫事件监听器协议

    实现此协议的类需要提供on_event方法来处理爬虫事件。
    """

    def on_event(self, event: SpiderEvent) -> None:
        """处理事件

        Args:
            event: 爬虫事件对象
        """
        ...

class SpiderEventDispatcher:
    """事件分发器，负责管理事件监听器和分发事件"""

    def __init__(self):
        self._listeners: list[SpiderEventListener] = []
        """事件监听器列表"""

    def add_listener(self, listener: SpiderEventListener) -> None:
        """添加事件监听器

        Args:
            listener: 实现了SpiderEventListener协议的监听器对象
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: SpiderEventListener) -> None:
        """移除事件监听器

        Args:
            listener: 要移除的监听器对象
        """
        if listener in self._listeners:
            self._listeners.remove(listener)

    def dispatch_event(self, event: SpiderEvent) -> None:
        """分发事件到所有注册的监听器

        Args:
            event: 要分发的事件对象

        Note:
            监听器的异常不会影响其他监听器或主程序的执行
        """
        for listener in self._listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                print(f"事件处理异常: {e}")