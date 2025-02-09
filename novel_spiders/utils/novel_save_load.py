import json
from typing import Dict, List, Optional

from novel_spiders.entities.novel import ChapterContent, Novel


def load_json_dict(json_str: str) -> Dict:
    """加载json字符串到字典"""
    return json.loads(json_str)


def novel_to_json(novel: Novel) -> str:
    """将小说对象转换为json字符串"""
    # return json.dumps(novel, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)
    return novel.model_dump_json(indent=4)


def load_novel_from_json(json_str: str) -> Novel:
    """从json字符串中加载小说对象"""
    return Novel.model_validate_json(json_str)


def novel_to_translatable_json(novel: Novel) -> str:
    """将小说对象转换为适合翻译的json格式
    :param novel: 小说对象
    :return: json字符串
    """
    data = {
        "title": novel.title,
        "description": novel.description,
        # "author": novel.author,
    }

    # 按章节索引排序
    sorted_chapters = sorted(novel.chapters, key=lambda c: c.index)

    for chapter in sorted_chapters:
        # 添加章节信息
        # 大章节标题不翻译
        # data[_get_ch_ep_json_key(chapter.index)] = chapter.ep_title
        data[_get_ch_title_json_key(chapter.index)] = chapter.title

        # 处理前置内容
        for content in chapter.prepend_contents:
            if _is_skip_line(content.content):
                continue
            data[_get_ch_line_json_key(content, chapter.index)] = content.content

        # 处理主要内容
        for content in chapter.contents:
            if _is_skip_line(content.content):
                continue
            data[_get_ch_line_json_key(content, chapter.index)] = content.content

        # 处理追加内容
        for content in chapter.append_contents:
            if _is_skip_line(content.content):
                continue
            data[_get_ch_line_json_key(content, chapter.index)] = content.content

    return json.dumps(data, ensure_ascii=False, indent=4)


def novel_to_markdown(novel: Novel, translates: Dict[str, str]) -> str:
    """将小说对象带翻译转换为markdown格式
    :param novel: 小说对象
    :param translates: 翻译内容
    :return: markdown字符串，前面带yaml头
    """
    lines: List[str] = []

    # yaml头
    lines.append("---")
    lines.append("title:")
    lines.append("- type: main")
    lines.append(f"  text: {novel.title}")
    lines.append("creator:")
    lines.append("- role: author")
    lines.append(f"  text: {novel.author}")
    lines.append("...")
    lines.append("")

    # 标题和简介
    _append_content_and_translate(f"# {novel.title}", "title", translates, lines)
    _append_content_and_translate(novel.description, "description", translates, lines)

    current_ep = ""
    for chapter in novel.chapters:
        if current_ep != chapter.ep_title:
            current_ep = chapter.ep_title
            _append_content_and_translate(
                f"# {current_ep}", _get_ch_ep_json_key(chapter.index), translates, lines
            )

        _append_content_and_translate(
            f"## {chapter.title}",
            _get_ch_title_json_key(chapter.index),
            translates,
            lines,
        )

        last_blank = False
        if len(chapter.prepend_contents) > 0:
            for content in chapter.prepend_contents:
                last_blank = _append_content_line(
                    content, lines, last_blank, chapter.index, translates
                )

            if not last_blank:
                lines.append("")
            lines.append("--------------------")
            last_blank = False

        for content in chapter.contents:
            last_blank = _append_content_line(
                content, lines, last_blank, chapter.index, translates
            )

        if len(chapter.append_contents) > 0:
            if not last_blank:
                lines.append("")
            lines.append("--------------------")
            last_blank = False
            for content in chapter.append_contents:
                last_blank = _append_content_line(
                    content, lines, last_blank, chapter.index, translates
                )

        if not last_blank:
            lines.append("")
    return "\n".join(lines)


def _append_content_line(
    content: ChapterContent,
    lines: List[str],
    last_blank: bool,
    index: int,
    translates: Dict[str, str],
) -> bool:
    """添加章节内容行
    :param content: 章节内容
    :param lines: 行列表
    :param last_blank: 上一行是否是空行
    :param index: 章节索引
    :param translates: 翻译内容
    :return: 当前行是否是空行
    """
    if _is_blank_line(content.content):
        lines.append("")
        last_blank = True
    elif _is_image_line(content.content):
        img_content = content.content.lstrip("img: ")
        lines.append(img_content)
        last_blank = False
    else:
        _append_content_and_translate(
            content.content,
            _get_ch_line_json_key(content, index),
            translates,
            lines,
            prepend_blank_line=not last_blank,
        )
        last_blank = False

    return last_blank


def _get_translate(key: str, translates: Dict[str, str]) -> Optional[str]:
    """获取翻译内容"""
    return translates.get(key, None)


def _append_translate_if_exist(key: str, translates: Dict[str, str], lines: List[str]):
    """如果翻译存在则添加到lines"""
    translate = _get_translate(key, translates)
    ori = lines[-1].strip()
    # 翻译和原文不一致时才添加翻译
    if translate is not None and translate.strip() and translate.strip() != ori:
        lines.append("")
        lines.append(translate)


def _append_content_and_translate(
    content: str,
    key: str,
    translates: Dict[str, str],
    lines: List[str],
    prepend_blank_line: bool = True,
):
    """添加内容和翻译"""
    if prepend_blank_line:
        lines.append("")
    lines.append(content)
    _append_translate_if_exist(key, translates, lines)


def _get_ch_line_json_key(content: ChapterContent, index: int) -> str:
    """获取章节内容的json key"""
    return f"ch-{index}-{content.key}"


def _get_ch_ep_json_key(index: int) -> str:
    """获取章节大标题的json key"""
    return f"ch-{index}-ep"


def _get_ch_title_json_key(index: int) -> str:
    """获取章节标题的json key"""
    return f"ch-{index}-title"


def _is_skip_line(line: str) -> bool:
    """判断是否是需要跳过的行"""
    return (
        line.strip() == ""
        or line.strip().startswith("#")
        or line.strip().startswith("img:")
        # 行内容只有纯粹的标点符号或数字时也跳过
        or all(c in ".,:;!?。，：；！？ #1234567890＊-+=()*♥" for c in line.strip())
    )


def _is_blank_line(line: str) -> bool:
    """判断是否是空行"""
    return line.strip() == ""


def _is_image_line(line: str) -> bool:
    """判断是否是图片行"""
    return line.strip().startswith("img:")
