import asyncio
import os
import io
import sys
from typing import Dict
from novel_spiders.spiders.syosetu_spider import SyosetuSpider
from novel_spiders.utils.novel_save_load import (
    load_json_dict,
    novel_to_json,
    load_novel_from_json,
    novel_to_translatable_json,
    novel_to_markdown,
)
from novel_spiders.entities.novel import Novel
from novel_spiders.utils.progress_listener import ConsoleProgressListener


async def _test_syosetu(code: str):
    """测试小说家网站爬虫
    Args:
        code: 小说ID，如n3828fz
    """
    spider = SyosetuSpider()
    spider.resource_name = code
    spider.data_root = f"./data/syosetu/{code}"
    spider.asset_dir = "assets"

    # 添加进度监听器
    progress_listener = ConsoleProgressListener()
    spider.add_event_listener(progress_listener)

    novel_path = os.path.join(spider.data_root, f"{code}.json")
    novel: Novel | None = None

    # 目录不存在则创建
    if not os.path.exists(spider.data_root):
        os.makedirs(spider.data_root)

    try:
        # 如果已有json则加载，否则爬取
        if os.path.exists(novel_path):
            print(f"从{novel_path}加载小说...")
            with io.open(novel_path, "r", encoding="utf-8") as f:
                novel = load_novel_from_json(f.read())
        else:
            print(f"开始获取小说{spider.resource_name}...")
            novel = await spider.get_novel()
            with io.open(novel_path, "w", encoding="utf-8") as f:
                f.write(novel_to_json(novel))

        print(f"获取成功：《{novel.title}》 作者：{novel.author}")
        print(f"章节数：{len(novel.chapters)}")

        # 保存可翻译的json
        untrans_json_path = os.path.join(spider.data_root, f"{code}_untrans.json")
        if not os.path.exists(untrans_json_path):
            print(f"保存可翻译json到{untrans_json_path}")
            with io.open(untrans_json_path, "w", encoding="utf-8") as f:
                f.write(novel_to_translatable_json(novel))

        trans_json_path = os.path.join(spider.data_root, f"{code}_trans.json")
        # AITranslator 出来的默认文件名，忘了改名时的兼容
        if not os.path.exists(trans_json_path):
            trans_json_path = os.path.join(spider.data_root, f"合并结果.json")
        trans_dict: Dict[str, str] = {}
        if os.path.exists(trans_json_path):
            print("Load translatable")
            with io.open(trans_json_path, "r", encoding="utf-8") as f:
                trans_json = f.read()
                trans_dict = load_json_dict(trans_json)

        # 生成markdown
        print("生成markdown...")
        md_text_dict = novel_to_markdown(novel, trans_dict, 500000)
        for key, md_text in md_text_dict.items():
            with io.open(
                os.path.join(spider.data_root, f"{code}({key}).md"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(md_text)

    except Exception as e:
        print(f"发生错误：{e}")
        raise e


def test_main():
    """测试入口函数"""
    # 获取小说ID参数，如果没有则使用默认值
    code = "n3828fz"  # 默认ID
    if len(sys.argv) > 2:  # sys.argv[1]是'syosetu'，所以要检查是否有第3个参数
        code = sys.argv[2]
    asyncio.run(_test_syosetu(code))
