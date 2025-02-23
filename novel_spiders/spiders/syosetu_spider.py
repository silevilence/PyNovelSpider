from novel_spiders.spiders.syosetu_18_spider import Syosetu18Spider


class SyosetuSpider(Syosetu18Spider):
    """Syosetu小说爬虫"""

    INFO_PAGE_URL = "https://ncode.syosetu.com/novelview/infotop/ncode/"
    CHAPTER_URL = "https://ncode.syosetu.com/"

    def __init__(self):
        super().__init__()
        self._resource_name = "Syosetu"