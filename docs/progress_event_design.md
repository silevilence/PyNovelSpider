# 小说爬虫进度事件设计

## 1. 事件类型设计

### 1.1 基础事件接口
```python
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

class SpiderEventType(Enum):
    """爬虫事件类型"""
    INFO_PAGE_START = "info_page_start"          # 开始爬取信息页
    INFO_PAGE_COMPLETE = "info_page_complete"    # 信息页爬取完成
    CHAPTERS_START = "chapters_start"            # 开始爬取章节
    CHAPTER_COMPLETE = "chapter_complete"        # 单章爬取完成
    COMPLETE = "complete"                        # 全部完成
    ERROR = "error"                             # 发生错误

@dataclass
class SpiderEvent:
    """爬虫事件基类"""
    type: SpiderEventType
    data: Any = None
    error: Optional[Exception] = None
```

### 1.2 具体事件数据结构
```python
@dataclass
class ChapterProgressData:
    """章节进度数据"""
    current: int            # 当前完成数
    total: int             # 总章节数
    latest_chapter: str    # 最新完成的章节标题

@dataclass
class NovelInfoData:
    """小说信息数据"""
    title: str
    author: str
    chapter_count: int
```

## 2. 事件处理机制

### 2.1 事件监听器接口
```python
from typing import Protocol

class SpiderEventListener(Protocol):
    """爬虫事件监听器"""
    def on_event(self, event: SpiderEvent) -> None:
        """处理事件"""
        pass
```

### 2.2 事件分发器
```python
class SpiderEventDispatcher:
    """事件分发器"""
    def __init__(self):
        self._listeners: list[SpiderEventListener] = []
    
    def add_listener(self, listener: SpiderEventListener) -> None:
        """添加监听器"""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: SpiderEventListener) -> None:
        """移除监听器"""
        self._listeners.remove(listener)
    
    def dispatch_event(self, event: SpiderEvent) -> None:
        """分发事件"""
        for listener in self._listeners:
            listener.on_event(event)
```

## 3. INovelSpider接口改造

### 3.1 接口变更
```python
class INovelSpider(ABC):
    def __init__(self):
        self._event_dispatcher = SpiderEventDispatcher()
    
    def add_event_listener(self, listener: SpiderEventListener) -> None:
        """添加事件监听器"""
        self._event_dispatcher.add_listener(listener)
    
    def remove_event_listener(self, listener: SpiderEventListener) -> None:
        """移除事件监听器"""
        self._event_dispatcher.remove_listener(listener)
```

## 4. 事件触发流程

### 4.1 信息页爬取
```plaintext
1. 开始爬取信息页
   - 触发 INFO_PAGE_START 事件

2. 信息页爬取完成
   - 触发 INFO_PAGE_COMPLETE 事件
   - 携带 NovelInfoData 数据
```

### 4.2 章节爬取
```plaintext
1. 开始爬取章节
   - 触发 CHAPTERS_START 事件
   - 携带总章节数信息

2. 每完成一个章节
   - 触发 CHAPTER_COMPLETE 事件
   - 携带 ChapterProgressData 数据

3. 全部完成
   - 触发 COMPLETE 事件
```

## 5. 使用示例

### 5.1 进度监听器实现
```python
class ProgressListener(SpiderEventListener):
    def on_event(self, event: SpiderEvent) -> None:
        if event.type == SpiderEventType.INFO_PAGE_START:
            print("开始获取小说信息...")
        elif event.type == SpiderEventType.INFO_PAGE_COMPLETE:
            info: NovelInfoData = event.data
            print(f"获取到小说信息: {info.title} by {info.author}")
        elif event.type == SpiderEventType.CHAPTERS_START:
            print(f"开始下载章节，共{event.data}章...")
        elif event.type == SpiderEventType.CHAPTER_COMPLETE:
            progress: ChapterProgressData = event.data
            print(f"进度: {progress.current}/{progress.total} - {progress.latest_chapter}")
        elif event.type == SpiderEventType.COMPLETE:
            print("小说下载完成！")
        elif event.type == SpiderEventType.ERROR:
            print(f"发生错误: {event.error}")
```

### 5.2 爬虫使用
```python
async def main():
    spider = SyosetuSpider()
    progress_listener = ProgressListener()
    spider.add_event_listener(progress_listener)
    
    try:
        novel = await spider.get_novel()
        print(f"下载完成: {novel.title}")
    except Exception as e:
        print(f"下载失败: {e}")
```

## 6. 实现注意事项

1. 异步考虑
   - 事件处理需要考虑异步监听器的情况
   - 可以让监听器自行选择同步/异步处理

2. 错误处理
   - 监听器的错误不应影响爬虫主流程
   - 关键错误通过ERROR事件通知

3. 性能影响
   - 事件分发应尽量轻量
   - 考虑在监听器过多时的性能影响

4. 线程安全
   - 并发章节下载时确保事件分发的线程安全
   - 考虑使用线程安全的容器存储监听器列表