"""
自定义异常模块

定义拼音正则表达式引擎中使用的自定义异常类。
"""


class PinyinRegexError(Exception):
    """拼音正则表达式基础异常类"""

    pass


class PatternParseError(PinyinRegexError):
    """正则表达式模式解析错误"""

    pass


class InvalidPatternError(PatternParseError):
    """无效的正则表达式模式"""

    pass


class QuantifierError(PatternParseError):
    """量词使用错误"""

    pass


class CharClassError(PatternParseError):
    """字符类语法错误"""

    pass


class TokenError(PinyinRegexError):
    """拼音token处理错误"""

    pass
