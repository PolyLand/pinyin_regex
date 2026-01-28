"""
拼音处理工具模块

提供拼音转换、声母提取、模糊音匹配等功能。
"""

from pypinyin import pinyin, Style
from typing import List, Dict, Set, Any


# 声母表
INITIALS: List[str] = [
    "zh",
    "ch",
    "sh",
    "b",
    "p",
    "m",
    "f",
    "d",
    "t",
    "n",
    "l",
    "g",
    "k",
    "h",
    "j",
    "q",
    "x",
    "r",
    "z",
    "c",
    "s",
    "y",
    "w",
]


# 模糊音映射表
FUZZY_MAP: Dict[str, str] = {
    "zh": "z",
    "ch": "c",
    "sh": "s",
}


def get_shengmu(py: str) -> str:
    """提取拼音的声母部分

    Args:
        py: 拼音字符串

    Returns:
        声母字符串，如果没有找到则返回原字符
    """
    for ini in INITIALS:
        if py.startswith(ini):
            return ini
    return py[0] if py else py


def expand_pinyin(
    py: str, use_initials: bool = True, use_fuzzy: bool = True
) -> Set[str]:
    """扩展拼音，包含声母和模糊音变体

    Args:
        py: 原始拼音
        use_initials: 是否使用声母索引
        use_fuzzy: 是否使用模糊音

    Returns:
        扩展后的拼音集合
    """
    res = {py}

    sm = get_shengmu(py)

    # 声母索引
    if use_initials:
        res.add(sm)

    # 模糊音
    if use_fuzzy and sm in FUZZY_MAP:
        fuzzy_sm = FUZZY_MAP[sm]
        res.add(fuzzy_sm + py[len(sm) :])  # zong
        res.add(fuzzy_sm)  # z

    return res


def text_to_tokens(
    text: str,
    use_initials: bool = True,
    use_fuzzy: bool = True,
    split_chars: bool = True,
) -> List[Dict[str, Any]]:
    """将文本转换为拼音token列表

    Args:
        text: 输入文本
        use_initials: 是否启用声母索引
        use_fuzzy: 是否启用模糊音
        split_chars: 是否按字符分割

    Returns:
        包含字符和对应拼音集合的token列表
    """
    if split_chars and isinstance(text, str):
        text = list(text)

    pys = pinyin(text, style=Style.NORMAL, heteronym=True)
    tokens = []

    for ch, py_list in zip(text, pys):
        base = set()
        for py in py_list:
            base |= expand_pinyin(py, use_initials, use_fuzzy)
        base |= set(ch)

        tokens.append({"char": ch, "pinyins": base})

    return tokens
