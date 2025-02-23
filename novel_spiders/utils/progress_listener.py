from novel_spiders.events.spider_events import (
    SpiderEventListener,
    SpiderEvent,
    SpiderEventType,
    NovelInfoData,
    ChapterProgressData
)


class ConsoleProgressListener(SpiderEventListener):
    """控制台进度显示监听器"""

    def on_event(self, event: SpiderEvent) -> None:
        """处理事件
        Args:
            event: 事件对象
        """
        if event.type == SpiderEventType.INFO_PAGE_START:
            print("开始获取小说信息...")
            
        elif event.type == SpiderEventType.INFO_PAGE_COMPLETE:
            assert isinstance(event.data, NovelInfoData)
            info = event.data
            print(f"获取到小说信息: {info.title} (作者: {info.author}), 共{info.chapter_count}章")
            
        elif event.type == SpiderEventType.CHAPTERS_START:
            assert isinstance(event.data, int)
            total_chapters = event.data
            print(f"开始下载章节，共{total_chapters}章...")
            
        elif event.type == SpiderEventType.CHAPTER_COMPLETE:
            assert isinstance(event.data, ChapterProgressData)
            progress = event.data
            print(f"进度: {progress.current}/{progress.total} - {progress.latest_chapter}")
            
        elif event.type == SpiderEventType.COMPLETE:
            print("小说下载完成！")
            
        elif event.type == SpiderEventType.ERROR:
            print(f"发生错误: {event.error}")