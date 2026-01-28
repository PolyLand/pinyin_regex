"""
正则表达式解析器模块

实现递归下降解析器，将正则表达式模式编译为NFA。
"""

from typing import Optional, Union, Set
from .engine import (
    Frag,
    State,
    literal_frag,
    concat_frag,
    alt_frag,
    star_frag,
    plus_frag,
    question_frag,
    range_frag,
)


class Parser:
    """正则表达式解析器类"""

    def __init__(self, pattern: str):
        self.p = pattern
        self.i = 0

    def peek(self) -> Optional[str]:
        """查看当前字符"""
        return self.p[self.i] if self.i < len(self.p) else None

    def get(self) -> Optional[str]:
        """获取当前字符并前进"""
        c = self.peek()
        self.i += 1
        return c

    def parse(self) -> Frag:
        """解析正则表达式模式"""
        return self.parse_alt()

    def parse_alt(self) -> Frag:
        """解析选择表达式（|操作）"""
        left = self.parse_seq()
        while self.peek() == "|":
            self.get()
            right = self.parse_seq()
            left = alt_frag(left, right)
        return left

    def parse_seq(self) -> Frag:
        """解析序列表达式"""
        frags = []
        while True:
            c = self.peek()
            if c is None or c in "|)":
                break
            frags.append(self.parse_repeat())

        if not frags:
            s = State()
            return Frag(s, s)

        res = frags[0]
        for f in frags[1:]:
            res = concat_frag(res, f)
        return res

    def parse_repeat(self) -> Frag:
        """解析重复表达式（*, +, ?, {m,n}）"""
        atom = self.parse_atom()

        while True:
            c = self.peek()
            if c is None:
                break

            if c in "*+?":
                op = self.get()
                if op == "*":
                    atom = star_frag(atom)
                elif op == "+":
                    atom = plus_frag(atom)
                elif op == "?":
                    atom = question_frag(atom)
            elif c == "{":
                atom = self.parse_range_quantifier(atom)
            else:
                break

        return atom

    def parse_range_quantifier(self, atom: Frag) -> Frag:
        """解析 {m,n} 量词"""
        # 保存原始位置，用于错误回退
        start_pos = self.i

        try:
            self.get()  # 消耗'{'

            # 解析 m
            m_str = ""
            while (c := self.peek()) is not None and c.isdigit():
                m_str += self.get()

            if not m_str:
                raise SyntaxError("Missing number before comma")

            min_count = int(m_str)

            # 检查是否有逗号
            max_count = min_count  # 默认 {m} = {m,m}
            if self.peek() == ",":
                self.get()  # 消耗','

                # 解析 n（可选）
                n_str = ""
                while (c := self.peek()) is not None and c.isdigit():
                    n_str += self.get()

                if n_str:
                    max_count = int(n_str)
                else:
                    # {m,} = {m, 正无穷}
                    max_count = float("inf")

            # 消耗'}'
            if self.peek() != "}":
                raise SyntaxError("Missing closing brace '}'")
            self.get()

            # 验证范围
            if max_count != float("inf") and min_count > max_count:
                raise SyntaxError(
                    f"min count {min_count} greater than max count {max_count}"
                )

            return range_frag(atom, min_count, max_count)

        except (SyntaxError, ValueError):
            # 语法错误：回退到原始位置，返回原始 atom
            self.i = start_pos
            return atom

    def parse_atom(self) -> Frag:
        """解析原子表达式"""
        c = self.get()

        if c is None:
            return literal_frag("")

        if c == "\\":
            next_char = self.get()
            if next_char is None:
                return literal_frag("\\")
            # 处理转义的边界符号
            if next_char == "^":
                return literal_frag("^")
            if next_char == "$":
                return literal_frag("$")
            return literal_frag("\\" + next_char)

        if c == "[":
            return self.parse_charclass()

        if c == "(":
            frag = self.parse_alt()
            if self.peek() == ")":
                self.get()
            return frag

        if c == ".":
            return literal_frag(".")
        
        # 边界符号 ^ 和 $
        if c == "^":
            return literal_frag("⟨BOS⟩")
        
        if c == "$":
            return literal_frag("⟨EOS⟩")

        return literal_frag(c)

    def parse_charclass(self) -> Frag:
        """解析字符类表达式"""
        negate = False
        chars = set()

        if self.peek() == "^":
            negate = True
            self.get()

        while self.peek() and self.peek() != "]":
            c = self.get()

            # 范围 a-z
            if self.peek() == "-" and self.p[self.i + 1] != "]":
                self.get()  # -
                end = self.get()
                if c is not None and end is not None:
                    for code in range(ord(c), ord(end) + 1):
                        chars.add(chr(code))
            else:
                if c is not None:
                    chars.add(c)

        self.get()  # ]

        if negate:
            return literal_frag(("NEG", frozenset(chars)))
        else:
            return literal_frag(frozenset(chars))


def compile_regex(pattern: str) -> State:
    """编译正则表达式模式为NFA起始状态

    Args:
        pattern: 正则表达式模式字符串

    Returns:
        NFA起始状态
    """
    parser = Parser(pattern)
    frag = parser.parse()
    frag.end.accept = True
    return frag.start
