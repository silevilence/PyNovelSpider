from typing import Tuple, List

from bs4.element import Tag
from novel_spiders.entities.novel import Novel, Chapter, ChapterContent
from novel_spiders.interfaces.INovelSpider import INovelSpider
from novel_spiders.utils.requests_helper import get_webpage, download_image
from bs4 import BeautifulSoup
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os


class Syosetu18Spider(INovelSpider):
    """Syosetu18小说爬虫"""

    INFO_PAGE_URL = "https://novel18.syosetu.com/novelview/infotop/ncode/"
    CHAPTER_URL = "https://novel18.syosetu.com/"
    PROXY_URL = "socks5://127.0.0.1:8866"

    DEFAULT_EP = "小说正文"

    PREPEND_PATTERN = re.compile(r"Lp\d+")
    BODY_PATTERN = re.compile(r"L\d+")
    APPEND_PATTERN = re.compile(r"La\d+")

    def __init__(self):
        self._resource_name = "Syosetu18"
        self._headless = False
        self._asset_dir = "assets"
        self._current_proxy = ""
        self._data_root = "."

    def _get_nvoel_base_info(self, html: str) -> Tuple[str, str, str, int]:
        """获取小说基本信息
        :param html: 网页内容
        :return: 小说标题、作者、简介、章节数
        """
        soup = BeautifulSoup(html, "html.parser")
        # 标题：<div id="contents_main"> -> h1 -> a
        title_tag = soup.select_one("#contents_main > h1 > a")
        title = "" if title_tag is None else title_tag.text.strip()

        # 章节数：div id=pre_info，取最后一个a标签的href，根据url最后一层为最后一章
        chapter_tag = soup.select_one("#pre_info > a:last-child")
        chapter = 0
        if chapter_tag is not None:
            chapter_url_attr = chapter_tag.get("href")
            chapter_url = ""
            if isinstance(chapter_url_attr, str):
                chapter_url = chapter_url_attr
            elif isinstance(chapter_url_attr, list):
                chapter_url = chapter_url_attr[-1]
            chapter = int(chapter_url.strip("/").split("/")[-1])

        author = ""
        desc = ""

        table = soup.find("table", id="noveltable1")
        if not isinstance(table, Tag):
            return title, author, desc, chapter

        trs = table.find_all("tr")
        for tr in trs:
            th_tag = tr.find("th")
            td_tag = tr.find("td")
            if th_tag is None or td_tag is None:
                continue
            th = th_tag.text.strip()
            td = td_tag.text.strip()
            if "作者名" in th:
                author = td
            elif "あらすじ" in th:
                desc = td

        return title, author, desc, chapter

    def _parse_single_chapter(self, html: str, ch_num: int) -> Chapter:
        """解析单章内容
        :param html: 网页内容
        :return: 章节对象
        """
        soup = BeautifulSoup(html, "html.parser")

        # 大章节标题
        ep_span = soup.select_one(".c-announce > span:not([class])")
        ep = self.DEFAULT_EP

        if ep_span is not None:
            ep = ep_span.text.strip()

        article_tag = soup.find("article", class_="p-novel")
        if not isinstance(article_tag, Tag):
            raise Exception("Failed to get article tag")
        title_tag = article_tag.find("h1", class_="p-novel__title")
        title = "" if title_tag is None else title_tag.text.strip()

        pre_contents = self._get_chapter_body(soup, self.PREPEND_PATTERN, ch_num)
        body_contents = self._get_chapter_body(soup, self.BODY_PATTERN, ch_num)
        append_contents = self._get_chapter_body(soup, self.APPEND_PATTERN, ch_num)

        return Chapter(
            index=ch_num,
            title=title,
            ep_title=ep,
            prepend_contents=pre_contents,
            contents=body_contents,
            append_contents=append_contents,
        )

    def _get_chapter_body(
        self, soup: BeautifulSoup, pattern: re.Pattern[str], ch_num: int
    ) -> List[ChapterContent]:
        """获取章节中的指定内容（章前、本体、章后）
        :param soup: 网页内容
        :param pattern: 正则表达式，筛选内容用
        :param ch_num: 章节号
        """
        contents = soup.find_all("p", id=pattern)

        ccs = []

        for content in contents:
            img_tag_a = content.find("a")
            if img_tag_a and img_tag_a.find("img"):
                img_tag = img_tag_a.find("img")
                img_src = img_tag["src"]
                img_alt = img_tag["alt"]
                if not img_src.startswith("http"):
                    img_src = f"https:{img_src}"
                img_ext = "jpg"
                img_name = f"{self._resource_name}-ch{ch_num}-{content['id']}.{img_ext}"
                if not img_alt.strip():
                    img_alt = img_name
                img_path = os.path.join(
                    self.data_root, self.asset_dir, "imgs", img_name
                )
                relative_path = os.path.join(self.asset_dir, "imgs", img_name)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                # 图片存在时不重复下载
                if os.path.exists(img_path):
                    ccs.append(
                        ChapterContent(
                            key=content["id"],
                            content=f"img: ![{img_alt}]({relative_path})",
                        )
                    )
                elif download_image(
                    img_src, img_path, self._current_proxy, {"over18": "yes"}
                ):
                    ccs.append(
                        ChapterContent(
                            key=content["id"],
                            content=f"img: ![{img_alt}]({relative_path})",
                        )
                    )
                else:
                    # 下载失败时，保存图片的URL
                    ccs.append(
                        ChapterContent(
                            key=content["id"], content=f"img: ![{img_alt}]({img_src})"
                        )
                    )
            else:
                ccs.append(ChapterContent(key=content["id"], content=content.text))

        return ccs
        # return [ChapterContent(content["id"], content.text) for content in contents]

    def _get_chapter_by_index(self, index: int) -> Chapter:
        """根据章节索引获取章节内容
        :param index: 章节索引，1起
        """
        # 代理设置传入为空时，使用默认代理
        proxy = self._current_proxy
        # 完整网址
        url = f"{self.CHAPTER_URL}{self.resource_name}/{index}/"
        # print("url:", url)
        # 根据代理获取网页内容
        cookies = {"over18": "yes"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        html = get_webpage(url, proxy, cookies, headers)
        if html is None:
            raise Exception("Failed to get webpage")
        return self._parse_single_chapter(html, index)

    async def _get_chapter_async(
        self, executor: ThreadPoolExecutor, index: int
    ) -> Tuple[int, Chapter]:
        """获取章节内容，异步包装一下
        :param executor: 线程池
        :param index: 章节索引
        :return: 章节索引、章节对象
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self._get_chapter_by_index, index)
        return index, result

    async def get_novel(self, proxy: str = "") -> Novel:
        """获取小说信息"""

        proxy = proxy.strip()
        self._current_proxy = proxy

        # 完整网址
        url = f"{self.INFO_PAGE_URL}{self.resource_name}/"
        # print("url:", url)
        # 根据代理获取网页内容
        cookies = {"over18": "yes"}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        html = get_webpage(url, proxy, cookies, headers)
        if html is None:
            raise Exception("Failed to get webpage")
        title, author, description, chapter_num = self._get_nvoel_base_info(html)

        # 从1到最后一章异步并行获取章节内容
        executor = ThreadPoolExecutor(max_workers=5)
        tasks = [
            self._get_chapter_async(executor, i) for i in range(1, chapter_num + 1)
        ]
        ch_results = await asyncio.gather(*tasks)
        sorted_ch_results = sorted(ch_results, key=lambda x: x[0])

        return Novel(
            title=title,
            description=description,
            author=author,
            chapters=[ch for _, ch in sorted_ch_results],
        )
