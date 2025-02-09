from typing import List
from pydantic import BaseModel


class ChapterContent(BaseModel):
    """章节内容实体类"""

    key: str
    content: str


class Chapter(BaseModel):
    """章节实体类"""

    index: int
    title: str
    ep_title: str
    prepend_contents: List[ChapterContent]
    contents: List[ChapterContent]
    append_contents: List[ChapterContent]


class Novel(BaseModel):
    """小说实体类"""

    title: str
    description: str
    author: str
    chapters: List[Chapter]
