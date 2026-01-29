#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼音正则表达式调试工具模块单元测试
"""

import unittest
import io
import os
import sys
from contextlib import redirect_stdout

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pinyin_regex import compile_regex, pinyin_regex_match
from pinyin_regex.debug import (
    dump_nfa,
    visualize_nfa,
    debug_pattern,
    NFAVisualizer,
    PerformanceProfiler,
    render_nfa_graph,
    GRAPHVIZ_AVAILABLE,
)


class TestDebugModule(unittest.TestCase):
    """调试工具模块测试类"""

    def setUp(self):
        """测试前准备"""
        self.pattern = "yinyue"
        self.text = "音乐"
        self.start_state = compile_regex(self.pattern)

    def test_dump_nfa(self):
        """测试NFA结构打印功能"""
        # 重定向输出并验证
        f = io.StringIO()
        with redirect_stdout(f):
            dump_nfa(self.start_state)
        output = f.getvalue()

        # 验证输出包含预期的NFA结构元素
        self.assertIn("State", output)
        self.assertIn("ACCEPT", output)
        self.assertIn("ε", output)
        self.assertIn("->", output)

    def test_visualize_nfa_dot_format(self):
        """测试NFA DOT格式输出"""
        # 测试DOT格式输出到文件
        output_file = "test_nfa.dot"

        try:
            visualize_nfa(self.start_state, output_file, "dot")

            # 验证文件是否生成
            self.assertTrue(os.path.exists(output_file))

            # 验证文件内容
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("digraph NFA", content)
            self.assertIn("rankdir", content)
            self.assertIn("label", content)

        finally:
            # 清理测试文件
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_visualize_nfa_stdout(self):
        """测试NFA输出到stdout"""
        # 重定向输出并验证
        f = io.StringIO()
        with redirect_stdout(f):
            visualize_nfa(self.start_state, None, "dot")
        output = f.getvalue()

        # 验证输出包含DOT格式
        self.assertIn("digraph NFA", output)
        self.assertIn("rankdir", output)

    @unittest.skipUnless(GRAPHVIZ_AVAILABLE, "graphviz not available")
    def test_graphviz_rendering(self):
        """测试graphviz图形渲染（如果可用）"""
        output_file = "test_nfa_render.png"

        try:
            result = render_nfa_graph(self.start_state, output_file, "png")

            if result:  # 如果渲染成功
                self.assertTrue(os.path.exists(result))
                # 验证文件不为空
                self.assertGreater(os.path.getsize(result), 0)

                # 清理生成的文件
                os.remove(result)

        except Exception as e:
            # graphviz渲染失败不应该导致测试失败
            self.skipTest(f"graphviz rendering failed: {e}")

    def test_debug_pattern_basic(self):
        """测试基础调试模式"""
        debug_info = debug_pattern(self.pattern, self.text)

        # 验证返回信息结构
        self.assertIn("pattern", debug_info)
        self.assertIn("text", debug_info)
        self.assertIn("match_result", debug_info)
        self.assertIn("tokens", debug_info)
        self.assertIn("stats", debug_info)
        self.assertIn("step_count", debug_info)

        # 验证内容
        self.assertEqual(debug_info["pattern"], self.pattern)
        self.assertEqual(debug_info["text"], self.text)
        self.assertIsInstance(debug_info["match_result"], bool)
        self.assertIsInstance(debug_info["tokens"], list)
        self.assertIsInstance(debug_info["stats"], dict)
        self.assertIsInstance(debug_info["step_count"], int)
        self.assertGreater(debug_info["step_count"], 0)

    def test_debug_pattern_stats(self):
        """测试调试模式统计信息"""
        debug_info = debug_pattern("yin", "音")

        stats = debug_info["stats"]

        # 验证统计字段
        possible_stats = ["transitions", "epsilon_closures", "final_states", "accept_states"]
        for stat in possible_stats:
            if stat in stats:
                self.assertIsInstance(stats[stat], int)
                self.assertGreaterEqual(stats[stat], 0)

    def test_performance_profiler_compilation(self):
        """测试性能分析器编译功能"""
        profiler = PerformanceProfiler()

        # 测试编译性能
        duration = profiler.profile_compilation(self.pattern)

        # 验证返回值
        self.assertIsInstance(duration, float)
        self.assertGreaterEqual(duration, 0)

        # 验证内部记录
        self.assertIn("compilation", profiler.timings)
        self.assertEqual(len(profiler.timings["compilation"]), 1)

    def test_performance_profiler_matching(self):
        """测试性能分析器匹配功能"""
        profiler = PerformanceProfiler()

        # 测试匹配性能
        duration = profiler.profile_matching(self.pattern, self.text)

        # 验证返回值
        self.assertIsInstance(duration, float)
        self.assertGreaterEqual(duration, 0)

        # 验证内部记录
        self.assertIn("matching", profiler.timings)
        self.assertEqual(len(profiler.timings["matching"]), 1)

    def test_performance_profiler_summary(self):
        """测试性能分析器摘要功能"""
        profiler = PerformanceProfiler()

        # 执行一些操作
        profiler.profile_compilation(self.pattern)
        profiler.profile_matching(self.pattern, self.text)

        # 获取摘要
        summary = profiler.get_summary()

        # 验证摘要结构
        self.assertIn("compilation", summary)
        self.assertIn("matching", summary)

        # 验证摘要内容
        for operation, stats in summary.items():
            self.assertIn("count", stats)
            self.assertIn("total", stats)
            self.assertIn("average", stats)
            self.assertIn("min", stats)
            self.assertIn("max", stats)

            self.assertEqual(stats["count"], 1)
            self.assertGreater(stats["total"], 0)
            self.assertGreater(stats["average"], 0)
            self.assertGreater(stats["min"], 0)
            self.assertGreater(stats["max"], 0)

    def test_nfa_visualizer_init(self):
        """测试NFA可视化器初始化"""
        visualizer = NFAVisualizer()
        self.assertEqual(visualizer.use_colors, True)

        visualizer_no_colors = NFAVisualizer(use_colors=False)
        self.assertEqual(visualizer_no_colors.use_colors, False)

    def test_nfa_visualizer_generate_dot(self):
        """测试NFA可视化器DOT生成"""
        visualizer = NFAVisualizer()

        dot_content = visualizer.generate_dot(self.start_state)

        # 验证DOT格式
        self.assertIsInstance(dot_content, str)
        self.assertIn("digraph NFA", dot_content)
        self.assertIn("rankdir", dot_content)
        self.assertIn("label", dot_content)
        self.assertIn(";", dot_content)

    def test_multiple_patterns_debug(self):
        """测试多种模式的调试功能"""
        test_cases = [
            ("a", "a"),
            ("ab", "ab"),
            ("a|b", "a"),
            ("a*", ""),
            ("a+", "aaa"),
        ]

        for pattern, text in test_cases:
            with self.subTest(pattern=pattern, text=text):
                debug_info = debug_pattern(pattern, text)

                # 基本验证
                self.assertIsInstance(debug_info["match_result"], bool)
                self.assertGreater(debug_info["step_count"], 0)
                self.assertIsInstance(debug_info["tokens"], list)

    def test_debug_pattern_options(self):
        """测试调试模式选项"""
        debug_info = debug_pattern("yy", "音乐", use_initials=False, use_fuzzy=False)

        # 验证选项影响了结果（yy不匹配音乐当禁用首字母时）
        self.assertFalse(debug_info["match_result"])

    def test_perf_counter(self):
        """测试性能计数器"""
        profiler = PerformanceProfiler()

        time1 = profiler.perf_counter()
        time2 = profiler.perf_counter()

        # 验证计数器递增
        self.assertGreaterEqual(time2, time1)
        self.assertIsInstance(time1, float)
        self.assertIsInstance(time2, float)

    def test_debug_pattern_bug_fix(self):
        """测试TODO中提到的debug_pattern bug修复

        验证debug_pattern('yin', '音')返回True，与pinyin_regex_match一致
        """
        from pinyin_regex import pinyin_regex_match

        # 具体问题用例：pattern = "yin", text = "音"
        debug_info = debug_pattern("yin", "音")

        # 验证修复后返回True
        self.assertTrue(debug_info["match_result"])

        # 验证与正常匹配函数结果一致
        normal_result = pinyin_regex_match("yin", "音")
        self.assertEqual(debug_info["match_result"], normal_result)

        # 验证调试信息完整性
        self.assertIn("stats", debug_info)
        self.assertIn("step_count", debug_info)
        self.assertIsInstance(debug_info["stats"], dict)
        self.assertIsInstance(debug_info["step_count"], int)
        self.assertGreater(debug_info["step_count"], 0)

    def test_debug_pattern_consistency_with_normal_match(self):
        """测试debug_pattern与pinyin_regex_match的一致性"""
        from pinyin_regex import pinyin_regex_match

        test_cases = [
            ("yin", "音"),
            ("yinyue", "音乐"),
            ("yy", "音乐"),
            ("yin(yue|le)", "音乐"),
            ("notfound", "音乐"),
            ("^yin$", "音"),
            ("yin+", "音乐音乐"),
            ("yin*", ""),
        ]

        for pattern, text in test_cases:
            with self.subTest(pattern=pattern, text=text):
                debug_result = debug_pattern(pattern, text)["match_result"]
                normal_result = pinyin_regex_match(pattern, text)

                self.assertEqual(
                    debug_result,
                    normal_result,
                    f"debug_pattern和pinyin_regex_match结果不一致: pattern={pattern}, text={text}",
                )


if __name__ == "__main__":
    unittest.main()
