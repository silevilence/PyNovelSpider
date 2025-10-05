import json
from typing import Dict, List, Optional, Tuple

from novel_spiders.entities.novel import ChapterContent, Novel

_SPLIT_LINE = "--------------------"


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


def novel_to_markdown(
    novel: Novel, translates: Dict[str, str], split: int = -1
) -> Dict[str, str]:
    """将小说对象带翻译转换为markdown格式
    :param novel: 小说对象
    :param translates: 翻译内容
    :param split: 按最大字数分割章节，0或以下表示不分割
    :return: 章节范围 -> markdown字符串，前面带yaml头
    """
    content_lines: List[str] = []
    header_lines: List[str] = []

    result_dict: Dict[str, str] = {}

    # yaml头
    header_lines.append("---")
    header_lines.append("title:")
    header_lines.append("- type: main")
    header_lines.append(f"  text: {novel.title}")
    header_lines.append("creator:")
    header_lines.append("- role: author")
    header_lines.append(f"  text: {novel.author}")
    header_lines.append("...")
    header_lines.append("")

    # 标题和简介
    _append_content_and_translate(f"# {novel.title}", "title", translates, header_lines)
    _append_content_and_translate(
        novel.description, "description", translates, header_lines
    )

    current_ep = ""
    current_word_count = 0
    start_idx = -1
    end_idx = -1
    for chapter in novel.chapters:
        if current_word_count == 0:
            start_idx = chapter.index

        if current_ep != chapter.ep_title:
            current_ep = chapter.ep_title
            current_word_count += _append_content_and_translate(
                f"# {current_ep}",
                _get_ch_ep_json_key(chapter.index),
                translates,
                content_lines,
            )

        current_word_count += _append_content_and_translate(
            f"## {chapter.title}",
            _get_ch_title_json_key(chapter.index),
            translates,
            content_lines,
        )

        last_blank = False
        if len(chapter.prepend_contents) > 0:
            for content in chapter.prepend_contents:
                last_blank, temp_count = _append_content_line(
                    content, content_lines, last_blank, chapter.index, translates
                )
                current_word_count += temp_count

            if not last_blank:
                content_lines.append("")
                current_word_count += 2
            content_lines.append(_SPLIT_LINE)
            current_word_count += len(_SPLIT_LINE) + 2
            last_blank = False

        for content in chapter.contents:
            last_blank, temp_count = _append_content_line(
                content, content_lines, last_blank, chapter.index, translates
            )
            current_word_count += temp_count

        if len(chapter.append_contents) > 0:
            if not last_blank:
                content_lines.append("")
                current_word_count += 2
            content_lines.append(_SPLIT_LINE)
            current_word_count += len(_SPLIT_LINE) + 2
            last_blank = False
            for content in chapter.append_contents:
                last_blank, temp_count = _append_content_line(
                    content, content_lines, last_blank, chapter.index, translates
                )
                current_word_count += temp_count

        if not last_blank:
            content_lines.append("")
            current_word_count += 2

        # 达到分割字数则分割
        end_idx = chapter.index
        if split > 0 and current_word_count >= split:
            key = f"{start_idx}-{end_idx}"
            result_dict[key] = "\n".join(header_lines + content_lines)

            # 重置相关的变量
            content_lines = []
            current_word_count = 0
            current_ep = ""

    # 处理剩余内容
    if len(content_lines) > 0:
        key = f"{start_idx}-{end_idx}"
        result_dict[key] = "\n".join(header_lines + content_lines)

    return result_dict


def _append_content_line(
    content: ChapterContent,
    lines: List[str],
    last_blank: bool,
    index: int,
    translates: Dict[str, str],
) -> Tuple[bool, int]:
    """添加章节内容行
    :param content: 章节内容
    :param lines: 行列表
    :param last_blank: 上一行是否是空行
    :param index: 章节索引
    :param translates: 翻译内容
    :return: (当前行是否是空行, 添加的字数)
    """
    word_count = 0
    if _is_blank_line(content.content):
        lines.append("")
        last_blank = True
        word_count += 2
    elif _is_image_line(content.content):
        img_content = content.content.lstrip("img: ")
        lines.append(img_content)
        last_blank = False
        word_count += 2
    else:
        word_count = _append_content_and_translate(
            content.content,
            _get_ch_line_json_key(content, index),
            translates,
            lines,
            prepend_blank_line=not last_blank,
        )
        last_blank = False

    return last_blank, word_count


def _get_translate(key: str, translates: Dict[str, str]) -> Optional[str]:
    """获取翻译内容"""
    return translates.get(key, None)


def _append_translate_if_exist(
    key: str, translates: Dict[str, str], lines: List[str]
) -> int:
    """如果翻译存在则添加到lines，返回添加的字数"""
    word_count = 0
    translate = _get_translate(key, translates)
    ori = lines[-1].strip()
    # 翻译和原文不一致时才添加翻译
    if translate is not None and translate.strip() and translate.strip() != ori:
        lines.append("")
        lines.append(translate)
        word_count += len(translate) + 4

    return word_count


def _append_content_and_translate(
    content: str,
    key: str,
    translates: Dict[str, str],
    lines: List[str],
    prepend_blank_line: bool = True,
) -> int:
    """添加内容和翻译，返回字数"""
    word_count = 0
    if prepend_blank_line:
        lines.append("")
        word_count += 2
    lines.append(content)
    word_count += len(content) + 2
    word_count += _append_translate_if_exist(key, translates, lines)

    return word_count


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
