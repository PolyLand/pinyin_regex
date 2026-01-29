#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼音正则表达式引擎单元测试

测试覆盖：
- 基础拼音匹配功能
- 正则表达式语法支持
- 边界情况和错误处理
- 性能测试
- 集成测试
"""

import unittest
import sys
import time
from typing import List, Tuple, Any

# 导入被测试的模块
from pinyin_regex import (
    pinyin_regex_match,
    text_to_tokens,
    compile_regex,
    expand_pinyin,
    get_shengmu,
    INITIALS,
    FUZZY_MAP,
)


class TestPinyinRegexBasic(unittest.TestCase):
    """基础拼音匹配功能测试"""

    def test_full_pinyin_match(self):
        """测试全拼匹配"""
        test_cases = [
            ("yinyue", "音乐", True),
            ("chongqing", "重庆", True),
            ("beijing", "北京", True),
            ("shanghai", "上海", True),
            ("guangzhou", "广州", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(
                    result,
                    expected,
                    f"Pattern '{pattern}' should {'match' if expected else 'not match'} '{text}'",
                )

    def test_initials_match(self):
        """测试首字母匹配"""
        test_cases = [
            ("yy", "音乐", True),
            ("cq", "重庆", True),
            ("bj", "北京", True),
            ("sh", "上海", True),
            ("gz", "广州", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_fuzzy_match(self):
        """测试模糊音匹配"""
        test_cases = [
            # zh/ch/sh 模糊音
            ("zong", "中", True),  # zhong -> zong
            ("cong", "冲", True),  # chong -> cong
            ("song", "山", False),  # shan -> song (实际不匹配，因为shan不以sh开头)
            ("si", "是", True),  # shi -> si
            ("ci", "吃", True),  # chi -> ci
            ("zi", "知", True),  # zhi -> zi
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_polyphonic_characters(self):
        """测试多音字处理"""
        test_cases = [
            ("chongqing", "重庆", True),  # 重: chong/zhong
            ("zhongqing", "重庆", True),  # 重: chong/zhong
            ("changjiang", "长江", True),  # 长: chang/zhang
            ("zhangjiang", "长江", True),  # 长: chang/zhang
            ("le", "乐", True),  # 乐: le/yue
            ("yue", "乐", True),  # 乐: le/yue
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestPinyinRegexFeatures(unittest.TestCase):
    """正则表达式功能测试"""

    def test_alternation(self):
        """测试或操作"""
        test_cases = [
            ("yin(yue|le)", "音乐", True),
            ("(yin|zhong)", "音乐", True),
            ("(zhong|yin)", "音乐", True),
            ("(abc|def)", "音乐", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_quantifiers(self):
        """测试量词"""
        test_cases = [
            # * 量词
            ("yin.*le", "音乐", True),
            (".*le", "音乐", True),
            ("yin.*", "音乐", True),
            # + 量词
            ("y.+e", "音乐", True),
            ("y.+", "音乐", True),
            # ? 量词
            ("yi?n", "音", True),
            ("zh?ong", "中", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_character_classes(self):
        """测试字符类"""
        test_cases = [
            (r"y\w+e", "音乐", False),
            (r"\w+", "音乐", False),
            (r"\d+", "音乐", False),
            (r"\z\z", "音乐", True),
            (r"[yl]in", "音", True),
            (r"[abc]in", "音", False),
            (r"y[a-z]+e", "音乐", True),
            (r"[^z]hong", "中", False),
            (r"[^a]in", "音", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_wildcard(self):
        """测试通配符"""
        test_cases = [
            (r"y.n", "音", True),  # yin
            (r".+", "音乐", True),
            (r"y..", "音乐", True),  # yinyue
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_escaped_sequences(self):
        """测试转义序列"""
        test_cases = [
            (r"yin\d", "音1", True),
            (r"\d+", "123", True),
            (r"\d+", "音乐", False),
            (r"\z+", "音乐", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestRangeQuantifiers(unittest.TestCase):
    """测试 {m,n} 量词功能"""

    def test_exact_count(self):
        """测试精确重复 {m}"""
        test_cases = [
            (r"yin{2}", "音能", True),  # yin + yin (两个字符都以in结尾)
            (r"y{2}", "音乐", True),  # yy (两个字符的首字母都是y)
            (r"y{3}", "音乐", False),  # yyy (需要3个字符都是y开头)
            (r"y{1}", "音乐", True),  # y (至少1个字符是y开头)
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_range_count(self):
        """测试范围重复 {m,n}"""
        test_cases = [
            (r"y{1,2}", "音乐", True),  # y 或 yy (1-2个字符y开头)
            (r"y{2,3}", "音乐世界", True),  # yy 或 yyy (2-3个字符y开头)
            (r"yin{1,2}", "音乐因", True),  # yin + in 或 yin(匹配第一个字符)
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_open_range(self):
        """测试开放范围 {m,}"""
        test_cases = [
            (r"y{1,}", "音乐", True),  # y, yy, yyy... (至少1个字符y开头)
            (r"yin{0,}", "音乐因", True),  # yin, yinin, yininin...
            (r"y{2,}", "音乐", True),  # yy (至少2个字符y开头，音乐两个字符都可以匹配y)
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_empty_count(self):
        """测试 {0} 空重复"""
        test_cases = [
            (r"y{0}", "音乐", True),  # 空字符串，应该匹配任何文本
            (r"x{0}", "音乐", True),  # 空字符串，应该匹配任何文本
            (r"y{0}", "", True),  # 空字符串应该匹配空文本
            (r"x{0}", "", True),  # 空字符串应该匹配空文本
            (r"a{0}", "xyz", True),  # 空字符串应该匹配任意文本
            (r"b{0}", "abc", True),  # 空字符串应该匹配任意文本
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestPinyinUtils(unittest.TestCase):
    """拼音工具函数测试"""

    def test_get_shengmu(self):
        """测试声母提取"""
        test_cases = [
            ("zhong", "zh"),
            ("chang", "ch"),
            ("shang", "sh"),
            ("bei", "b"),
            ("a", "a"),
            ("", ""),
        ]

        for pinyin, expected in test_cases:
            with self.subTest(pinyin=pinyin):
                result = get_shengmu(pinyin)
                self.assertEqual(result, expected)

    def test_expand_pinyin(self):
        """测试拼音扩展"""
        # 测试基本扩展
        result = expand_pinyin("zhong", use_initials=True, use_fuzzy=False)
        self.assertIn("zhong", result)
        self.assertIn("zh", result)

        # 测试模糊音扩展
        result = expand_pinyin("zhong", use_initials=True, use_fuzzy=True)
        self.assertIn("zhong", result)
        self.assertIn("zh", result)
        self.assertIn("zong", result)
        self.assertIn("z", result)

    def test_text_to_tokens(self):
        """测试文本转换为token"""
        tokens = text_to_tokens("音乐")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0]["char"], "音")
        self.assertIn("yin", tokens[0]["pinyins"])
        self.assertEqual(tokens[1]["char"], "乐")
        self.assertIn("yue", tokens[1]["pinyins"])


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_pattern(self):
        """测试空模式"""
        result = pinyin_regex_match("", "音乐")
        self.assertTrue(result)

    def test_empty_text(self):
        """测试空文本"""
        result = pinyin_regex_match("yinyue", "")
        self.assertFalse(result)

    def test_substring_matching(self):
        """测试子串匹配"""
        test_cases = [
            ("yue", "我的音乐很好听", True),
            ("yin", "纯音乐", True),
            ("beijing", "我爱北京天安门", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_non_matching_cases(self):
        """测试不匹配情况"""
        test_cases = [
            ("bei", "音乐", False),
            ("shanghai", "北京", False),
            ("zzz", "音乐", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_large_text_performance(self):
        """测试大文本性能"""
        # 创建包含大量中文的文本
        large_text = "音乐" * 1000
        start_time = time.time()
        result = pinyin_regex_match("yinyue", large_text)
        end_time = time.time()

        self.assertTrue(result)
        # 性能要求：处理1000个字符应该在1秒内完成
        self.assertLess(end_time - start_time, 1.0)

    def test_complex_pattern_performance(self):
        """测试复杂模式性能"""
        complex_pattern = r"(yin|zhong|chang|bei|shang)[a-z]*"
        start_time = time.time()
        result = pinyin_regex_match(complex_pattern, "音乐中国长江北京上海")
        end_time = time.time()

        self.assertTrue(result)
        # 复杂模式应该在合理时间内完成
        self.assertLess(end_time - start_time, 2.0)


class TestComplexCombination(unittest.TestCase):
    """复杂规则组合测试 - 基于candidates目录审核通过的测试用例"""

    def test_complex_combination_patterns(self):
        """测试多规则组合模式"""
        test_cases = [
            # yin(yue|le){2} 匹配 "音乐了"
            ("yin(yue|le){2}", "音乐了", True, "yin + (yue或le)重复2次"),
            ("yin(yue|le){2}", "音乐", False, "需要(yue|le)重复2次，只有1次"),
            # (y(yue|le)){2} 匹配 "音乐音乐"
            ("(y(yue|le)){2}", "音乐音乐", True, "(y+(yue|le))重复2次"),
            ("(y(yue|le)){2}", "音乐", False, "需要重复2次，只有1次"),
            # yin(yue|le)+ 匹配 "音乐乐乐"
            ("yin(yue|le)+", "音乐乐乐", True, "yin + (yue或le)1次或多次"),
        ]

        for pattern, text, expected, description in test_cases:
            with self.subTest(pattern=pattern, text=text, description=description):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(
                    result,
                    expected,
                    f"Pattern '{pattern}' should {'match' if expected else 'not match'} '{text}' - {description}",
                )

    def test_boundary_matching(self):
        """测试边界匹配"""
        test_cases = [
            # ^$ 边界匹配
            ("^yin(yue|le)$", "音乐", True, "从开始到结束完全匹配"),
            ("^yin(yue|le)$", "音乐家", False, "^$要求完全匹配，多了'家'"),
            ("^yin", "音乐", True, "以yin开头"),
            ("yue$", "音乐", True, "以yue结尾"),
        ]

        for pattern, text, expected, description in test_cases:
            with self.subTest(pattern=pattern, text=text, description=description):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(
                    result,
                    expected,
                    f"Pattern '{pattern}' should {'match' if expected else 'not match'} '{text}' - {description}",
                )

    def test_special_symbols_handling(self):
        """测试特殊符号处理"""
        test_cases = [
            # . 符号不应该匹配边界符
            (".", "", False, ".不应该匹配边界符号"),
            (".+", "", False, ".+不应该匹配纯边界符号"),
            # . 匹配普通字符
            (".", "音", True, ".应该匹配普通字符'音'"),
        ]

        for pattern, text, expected, description in test_cases:
            with self.subTest(pattern=pattern, text=text, description=description):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(
                    result,
                    expected,
                    f"Pattern '{pattern}' should {'match' if expected else 'not match'} '{text}' - {description}",
                )


if __name__ == "__main__":
    unittest.main()
