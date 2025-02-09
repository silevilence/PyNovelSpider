from typing import Dict, Optional
from novel_spiders.spiders.syosetu_18_spider import Syosetu18Spider
from novel_spiders.utils.novel_save_load import (
    novel_to_json,
    load_novel_from_json,
    novel_to_translatable_json,
    load_json_dict,
    novel_to_markdown,
)
from novel_spiders.entities.novel import Novel
import asyncio
import io
import os
import sys


async def main():
    # spider = Syosetu18Spider()
    # # spider.resource_name = "n3057hq"
    # spider.resource_name = "n0609jx"
    # novel = await spider.get_novel()
    # json = novel_to_json(novel)
    # # 保存到test.json中
    # with io.open("test.json", "w", encoding="utf-8") as f:
    #     f.write(json)

    # with io.open("test.json", "r", encoding="utf-8") as f:
    #     json = f.read()
    # novel2 = load_novel_from_json(json)
    # print(novel2.title)
    # # trans_json = novel_to_translatable_json(novel2)
    # # with io.open("testtrans.json", "w", encoding="utf-8") as f:
    # #     f.write(trans_json)
    # with io.open("transed.json", "r", encoding="utf-8") as f:
    #     trans_json = f.read()
    # trans_dict = load_json_dict(trans_json)
    # md_text = novel_to_markdown(novel2, trans_dict)
    # with io.open("test.md", "w", encoding="utf-8") as f:
    #     f.write(md_text)

    # 采集导出试验
    code = sys.argv[1]
    spider = Syosetu18Spider()
    spider.resource_name = code
    spider.data_root = f"./data/{code}"
    spider.asset_dir = "assets"

    # 目录不存在则创建
    if not os.path.exists(spider.data_root):
        os.makedirs(spider.data_root)

    novel_path = os.path.join(spider.data_root, f"{code}.json")
    novel: Optional[Novel] = None
    if os.path.exists(novel_path):
        print(f"Load novel from {novel_path}")
        with io.open(novel_path, "r", encoding="utf-8") as f:
            novel = load_novel_from_json(f.read())
    else:
        print(f"Get novel from {spider.resource_name}")
        novel = await spider.get_novel(proxy=Syosetu18Spider.PROXY_URL)
        with io.open(novel_path, "w", encoding="utf-8") as f:
            f.write(novel_to_json(novel))

    untrans_json_path = os.path.join(spider.data_root, f"{code}_untrans.json")
    if not os.path.exists(untrans_json_path):
        print(f"Save untranslatable json to {untrans_json_path}")
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

    print("Save markdown")
    md_text = novel_to_markdown(novel, trans_dict)
    with io.open(
        os.path.join(spider.data_root, f"{code}.md"), "w", encoding="utf-8"
    ) as f:
        f.write(md_text)


if __name__ == "__main__":
    asyncio.run(main())
