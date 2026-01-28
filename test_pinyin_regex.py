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


class TestRegexSyntax(unittest.TestCase):
    """正则表达式语法测试"""

    def test_alternation(self):
        """测试或操作 |"""
        test_cases = [
            ("yin(yue|le)", "音乐", True),
            ("(yin|zhong)", "音乐", True),
            ("(zhong|yin)", "音乐", True),
            ("(beijing|shanghai)", "北京", True),
            ("(beijing|shanghai)", "上海", True),
            ("(beijing|shanghai)", "广州", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_star_quantifier(self):
        """测试星号量官 *"""
        test_cases = [
            ("yin.*le", "音乐", True),
            (".*le", "音乐", True),
            ("yin.*", "音乐", True),
            (".*", "音乐", True),
            ("y.*", "音乐", True),
            ("a.*", "音乐", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_plus_quantifier(self):
        """测试加号量官 +"""
        test_cases = [
            ("y.+e", "音乐", True),
            ("y.+", "音乐", True),
            (".+e", "音乐", True),
            (".+n", "音乐", True),
            ("a.+b", "音乐", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_question_quantifier(self):
        """测试问号量官 ?"""
        test_cases = [
            ("yi?n", "音", True),
            ("zh?ong", "中", True),
            ("ch?ong", "重", True),
            ("sh?ang", "上", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_character_class(self):
        """测试字符类 []"""
        test_cases = [
            ("[yl]in", "音", True),  # yin
            ("[abc]in", "音", False),  # 不匹配
            ("[bpm]ei", "北", True),  # bei
            ("[gkh]uo", "国", True),  # guo
            ("[jqx]in", "心", True),  # xin
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_negated_character_class(self):
        """测试否定字符类 [^]"""
        test_cases = [
            ("[^z]hong", "中", False),  # zhong 以 z 开头
            ("[^a]in", "音", True),  # yin 不以 a 开头
            ("[^b]ei", "北", False),  # bei 以 b 开头
            ("[^x]in", "心", False),  # xin 以 x 开头
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_range_character_class(self):
        """测试范围字符类 [a-z]"""
        test_cases = [
            ("y[a-z]+e", "音乐", True),
            ("[a-z]+", "音乐", True),
            ("[b-p]ei", "北", True),  # b-p 包含 p
            ("[m-q]ing", "明", True),  # m-q 包含 m
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_dot_wildcard(self):
        """测试点号通配符 ."""
        test_cases = [
            ("y.n", "音", True),  # yin
            (".+", "音乐", True),
            ("..", "音乐", True),
            ("...", "音乐", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestEscapeSequences(unittest.TestCase):
    """转义序列测试"""

    def test_digit_escape(self):
        """测试数字转义"""
        test_cases = [
            (r"yin\d", "音1", True),
            (r"yin\d", "音2", True),
            (r"\d+", "123", True),
            (r"\d+", "音乐", False),
            (r"bei\d", "北3", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_word_escape(self):
        """测试字母数字转义"""
        test_cases = [
            (r"y\w+e", "音乐", False),  # y + 任意字母 + e
            (r"\w+", "音乐", False),  # 任意拼音
            (r"\w+le", "音乐", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_pinyin_escape(self):
        """测试中文token转义"""
        test_cases = [
            (r"\z\z", "音乐", True),  # 两个汉字
            (r"\z+", "音乐", True),
            (r"\z", "音", True),
            (r"\z{3}", "音乐家", True),  # \z{3} 现在支持了
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestSubstringMatching(unittest.TestCase):
    """子串匹配测试"""

    def test_substring_match(self):
        """测试在长文本中匹配子串"""
        test_cases = [
            ("yue", "我的音乐很好听", True),
            ("yin", "纯音乐", True),
            ("bei", "北京欢迎您", True),
            ("shang", "夜上海", True),
            ("guang", "光辉岁月", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_no_match_cases(self):
        """测试不匹配的情况"""
        test_cases = [
            ("bei", "音乐", False),
            ("shanghai", "北京", False),
            ("zzz", "音乐", False),
            ("abc", "中文", False),
            ("xyz", "汉字", False),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_empty_pattern(self):
        """测试空模式"""
        result = pinyin_regex_match("", "音乐")
        self.assertTrue(result, "Empty pattern should match any text")

    def test_empty_text(self):
        """测试空文本"""
        result = pinyin_regex_match(".*", "")
        self.assertTrue(result, "Empty text should match .* pattern")

        result = pinyin_regex_match("yin", "")
        self.assertFalse(result, "Empty text should not match non-empty pattern")

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        test_cases = [
            ("YINYUE", "音乐", True),  # 大写应该匹配
            ("YinYue", "音乐", True),  # 混合大小写
            ("yinyue", "音乐", True),  # 小写
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_options_parameters(self):
        """测试选项参数"""
        text = "中"

        # 测试 use_initials=False (实际上仍然匹配，因为zhong本身包含z)
        result = pinyin_regex_match("z", text, use_initials=False)
        self.assertTrue(
            result,
            "Should still match when use_initials=False because zhong contains z",
        )

        # 测试 use_fuzzy=False
        result = pinyin_regex_match("zong", text, use_fuzzy=False)
        self.assertFalse(result, "Should not match fuzzy when use_fuzzy=False")

        # 测试 split_chars=False
        result = pinyin_regex_match("zhong", text, split_chars=False)
        self.assertTrue(result, "Should match when split_chars=False")


class TestUtilityFunctions(unittest.TestCase):
    """工具函数测试"""

    def test_get_shengmu(self):
        """测试获取声母函数"""
        test_cases = [
            ("zhong", "zh"),
            ("chong", "ch"),
            ("shang", "sh"),
            ("beijing", "b"),
            ("yin", "y"),
            ("", ""),
        ]

        for pinyin, expected in test_cases:
            with self.subTest(pinyin=pinyin):
                result = get_shengmu(pinyin)
                self.assertEqual(result, expected)

    def test_expand_pinyin(self):
        """测试拼音扩展函数"""
        # 测试正常拼音
        result = expand_pinyin("zhong", use_initials=True, use_fuzzy=True)
        self.assertIn("zhong", result)
        self.assertIn("zh", result)
        self.assertIn("zong", result)
        self.assertIn("z", result)

        # 测试非模糊音
        result = expand_pinyin("bei", use_initials=True, use_fuzzy=True)
        self.assertIn("bei", result)
        self.assertIn("b", result)
        self.assertNotIn("pei", result)

        # 测试关闭选项
        result = expand_pinyin("zhong", use_initials=False, use_fuzzy=False)
        self.assertEqual(result, {"zhong"})

    def test_text_to_tokens(self):
        """测试文本转token函数"""
        tokens = text_to_tokens("音乐")

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0]["char"], "音")
        self.assertEqual(tokens[1]["char"], "乐")

        # 检查拼音集合不为空
        self.assertTrue(tokens[0]["pinyins"])
        self.assertTrue(tokens[1]["pinyins"])


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_performance_simple_patterns(self):
        """测试简单模式性能"""
        text = "这是一个用于性能测试的长文本，包含很多中文字符"
        patterns = ["yin", "yue", "shi", "ce", "wen"]

        start_time = time.time()
        for _ in range(100):
            for pattern in patterns:
                pinyin_regex_match(pattern, text)
        end_time = time.time()

        duration = end_time - start_time
        self.assertLess(
            duration, 5.0, f"Performance test took too long: {duration:.2f}s"
        )

    def test_performance_complex_patterns(self):
        """测试复杂模式性能"""
        text = "音乐测试文本用于性能评估"
        patterns = ["yin(yue|le)", "y.+e", "[a-z]+", "(yin|yue|ce|shi)"]

        start_time = time.time()
        for _ in range(50):
            for pattern in patterns:
                pinyin_regex_match(pattern, text)
        end_time = time.time()

        duration = end_time - start_time
        self.assertLess(
            duration, 5.0, f"Complex pattern test took too long: {duration:.2f}s"
        )


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_real_world_scenarios(self):
        """测试真实世界场景"""
        scenarios = [
            # 搜索音乐
            ("yinyue", "我想听音乐", True),
            ("gequ", "播放歌曲", True),
            # 搜索城市
            ("beijing", "北京是首都", True),
            ("shanghai", "上海很繁华", True),
            # 搜索人名
            ("zhangsan", "张三来了", True),
            ("lisi", "李四走了", True),
        ]

        for pattern, text, expected in scenarios:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)

    def test_complex_regex_combinations(self):
        """测试复杂正则组合"""
        test_cases = [
            (r"(yin|zhong)\w*", "音乐", True),
            (r"[yz]\w+", "音乐", False),
            (r"y(in|ue)?", "音乐", True),
            (r"(be|shi|guang).+", "北京上海广州", True),
        ]

        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)


def run_comprehensive_tests():
    """运行全面测试套件"""
    print("开始运行拼音正则表达式引擎全面测试套件...")
    print("=" * 60)

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestPinyinRegexBasic,
        TestRegexSyntax,
        TestEscapeSequences,
        TestSubstringMatching,
        TestEdgeCases,
        TestUtilityFunctions,
        TestPerformance,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出测试结果统计
    print("\n" + "=" * 60)
    print("测试结果统计:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
    )
    print(f"\n成功率: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("所有测试通过！")
        return True
    else:
        print("部分测试失败")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
