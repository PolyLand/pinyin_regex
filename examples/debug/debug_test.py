#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼音正则表达式调试工具测试

快速测试debug模块是否能正常工作
"""

import sys
import os

# 添加父目录到路径以便导入pinyin_regex
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pinyin_regex import pinyin_regex_match, compile_regex
from pinyin_regex.debug import (
    dump_nfa,
    visualize_nfa,
    debug_pattern,
    NFAVisualizer,
    PerformanceProfiler,
)


def test_basic_functionality():
    """测试基础功能"""
    print("测试基础NFA结构打印...")

    pattern = "yinyue"
    start_state = compile_regex(pattern)

    # 测试dump_nfa
    print("OK dump_nfa 测试通过")

    # 测试visualize_nfa
    try:
        visualize_nfa(start_state, "test_nfa.dot")
        if os.path.exists("test_nfa.dot"):
            os.remove("test_nfa.dot")
            print("OK visualize_nfa 测试通过")
        else:
            print("FAIL visualize_nfa 文件生成失败")
    except Exception as e:
        print(f"FAIL visualize_nfa 测试失败: {e}")


def test_debug_pattern():
    """测试调试模式功能"""
    print("\n测试debug_pattern...")

    try:
        debug_info = debug_pattern("yinyue", "音乐")
        assert "match_result" in debug_info
        assert "stats" in debug_info
        assert "tokens" in debug_info
        print("OK debug_pattern 测试通过")
        print(f"  匹配结果: {debug_info['match_result']}")
        print(f"  Tokens: {debug_info['tokens']}")
    except Exception as e:
        print(f"FAIL debug_pattern 测试失败: {e}")


def test_performance_profiler():
    """测试性能分析器"""
    print("\n测试性能分析器...")

    try:
        profiler = PerformanceProfiler()

        # 测试编译性能
        duration = profiler.profile_compilation("test")
        assert duration >= 0

        # 测试匹配性能
        duration = profiler.profile_matching("test", "test")
        assert duration >= 0

        # 测试摘要
        summary = profiler.get_summary()
        assert "compilation" in summary
        assert "matching" in summary

        print("OK 性能分析器测试通过")
    except Exception as e:
        print(f"FAIL 性能分析器测试失败: {e}")


def test_multiple_patterns():
    """测试多种模式"""
    print("\n测试多种模式...")

    test_cases = [
        ("yinyue", "音乐", True),
        ("yy", "音乐", True),
        ("zong", "中", True),  # 模糊音
        ("xyz", "音乐", False),
    ]

    all_passed = True
    for pattern, text, expected in test_cases:
        try:
            result = pinyin_regex_match(pattern, text)
            if result == expected:
                print(f"OK {pattern} 匹配 {text}: {result}")
            else:
                print(f"FAIL {pattern} 匹配 {text}: 期望 {expected}, 得到 {result}")
                all_passed = False
        except Exception as e:
            print(f"FAIL {pattern} 匹配 {text}: 异常 {e}")
            all_passed = False

    if all_passed:
        print("OK 所有模式测试通过")
    else:
        print("FAIL 部分模式测试失败")


def main():
    """运行所有测试"""
    print("拼音正则表达式调试工具测试")
    print("=" * 40)

    test_basic_functionality()
    test_debug_pattern()
    test_performance_profiler()
    test_multiple_patterns()

    print("\n" + "=" * 40)
    print("测试完成！")


if __name__ == "__main__":
    main()
