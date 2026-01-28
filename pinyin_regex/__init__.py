"""
拼音正则表达式引擎

Python库，支持使用拼音正则表达式匹配中文字符。
该库实现了完整的NFA（非确定性有限自动机）引擎，
支持正则表达式语法和拼音模糊匹配。
"""

__version__ = "1.0.0"
__author__ = "Pinyin Regex Engine Team"

# 导入核心功能
from .pinyin_utils import (
    text_to_tokens,
    expand_pinyin,
    get_shengmu,
    INITIALS,
    FUZZY_MAP,
)
from .engine import (
    State,
    run_pinyin_regex,
    epsilon_closure,
    match_label,
)
from .parser import compile_regex
from .errors import (
    PinyinRegexError,
    PatternParseError,
    InvalidPatternError,
    QuantifierError,
    CharClassError,
    TokenError,
)


def pinyin_regex_match(
    pattern: str,
    text: str,
    use_initials: bool = True,
    use_fuzzy: bool = True,
    split_chars: bool = True,
) -> bool:
    """拼音正则表达式匹配函数

    Args:
        pattern: 拼音正则表达式模式
        text: 要搜索的中文文本
        use_initials: 是否启用首字母匹配，默认True
        use_fuzzy: 是否启用模糊音匹配，默认True
        split_chars: 是否按字符分割，默认True

    Returns:
        是否匹配成功

    Examples:
        >>> pinyin_regex_match("yinyue", "音乐")
        True
        >>> pinyin_regex_match("yy", "音乐")  # 首字母匹配
        True
        >>> pinyin_regex_match("zong", "中")  # 模糊音匹配
        True
        >>> pinyin_regex_match("yin(yue|le)", "音乐")  # 正则表达式
        True
    """
    start_state = compile_regex(pattern.lower())
    tokens = text_to_tokens(
        text, use_initials=use_initials, use_fuzzy=use_fuzzy, split_chars=split_chars
    )
    return run_pinyin_regex(start_state, tokens)


# 导出公共API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    # 主要API
    "pinyin_regex_match",
    # 拼音工具
    "text_to_tokens",
    "expand_pinyin",
    "get_shengmu",
    "INITIALS",
    "FUZZY_MAP",
    # 引擎核心
    "State",
    "run_pinyin_regex",
    "epsilon_closure",
    "match_label",
    # 解析器
    "compile_regex",
    # 异常类
    "PinyinRegexError",
    "PatternParseError",
    "InvalidPatternError",
    "QuantifierError",
    "CharClassError",
    "TokenError",
]
