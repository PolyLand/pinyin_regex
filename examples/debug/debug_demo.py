#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼音正则表达式调试工具演示

演示如何使用debug模块的各种功能：
1. NFA结构可视化
2. 调试运行
3. 性能分析
4. 详细调试信息
"""

import sys
import os

# 添加项目根目录到路径以便导入pinyin_regex
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pinyin_regex import pinyin_regex_match, compile_regex
from pinyin_regex.debug import (
    dump_nfa,
    debug_run,
    visualize_nfa,
    debug_pattern,
    NFAVisualizer,
    NFADebugger,
    PerformanceProfiler,
)


def demo_basic_nfa_dump():
    """演示基础NFA结构打印"""
    print("=== Demo 1: 基础NFA结构打印 ===")

    pattern = "yinyue"
    print(f"模式: {pattern}")

    start_state = compile_regex(pattern)
    dump_nfa(start_state)
    print()


def demo_complex_nfa_dump():
    """演示复杂正则表达式的NFA结构"""
    print("=== Demo 2: 复杂正则表达式NFA ===")

    pattern = "yin(yue|le)+"
    print(f"模式: {pattern}")

    start_state = compile_regex(pattern)
    dump_nfa(start_state)
    print()


def demo_debug_run():
    """演示调试运行功能"""
    print("=== Demo 3: 调试运行功能 ===")

    pattern = "yy"
    text = "音乐"
    print(f"模式: {pattern}, 文本: {text}")

    start_state = compile_regex(pattern)

    # 创建调试器
    debugger = NFADebugger(verbose=True)

    # 获取tokens
    from pinyin_regex.pinyin_utils import text_to_tokens

    tokens = text_to_tokens(text)
    print(f"Tokens: {tokens}")

    # 调试运行
    from pinyin_regex.parser import Frag

    frag = Frag(start_state, start_state)  # 简化的frag，实际应该由parser创建
    # 这里为了演示，我们用debug_pattern函数
    print()


def demo_debug_pattern():
    """演示完整模式调试"""
    print("=== Demo 4: 完整模式调试 ===")

    test_cases = [
        ("yinyue", "音乐"),
        ("yy", "音乐"),
        ("yin(yue|le)", "音乐"),
        ("y.+e", "音乐"),
        ("zong", "中"),  # 模糊音
    ]

    for pattern, text in test_cases:
        print(f"模式: {pattern}, 文本: {text}")

        debug_info = debug_pattern(pattern, text)
        print(f"匹配结果: {debug_info['match_result']}")
        print(f"Tokens: {debug_info['tokens']}")
        print(f"统计信息: {debug_info['stats']}")
        print(f"步骤数: {debug_info['step_count']}")
        print("-" * 40)


def demo_visualization():
    """演示NFA可视化功能"""
    print("=== Demo 5: NFA可视化 ===")

    # 简单模式
    pattern = "abc"
    print(f"生成模式 '{pattern}' 的DOT图...")

    start_state = compile_regex(pattern)

    # 保存DOT文件
    dot_file = "nfa_simple.dot"
    visualize_nfa(start_state, dot_file)

    # 复杂模式
    pattern2 = "a(b|c)*"
    print(f"生成模式 '{pattern2}' 的DOT图...")

    start_state2 = compile_regex(pattern2)
    dot_file2 = "nfa_complex.dot"
    visualize_nfa(start_state2, dot_file2)

    print("提示：可以使用 'dot -Tpng nfa_simple.dot -o nfa_simple.png' 生成图片")
    print()


def demo_performance_profiling():
    """演示性能分析功能"""
    print("=== Demo 6: 性能分析 ===")

    profiler = PerformanceProfiler()

    # 测试编译性能
    patterns = ["a", "ab", "a(b|c)*", "yin(yue|le)+", "[a-z]+"]
    print("编译性能测试:")
    for pattern in patterns:
        duration = profiler.profile_compilation(pattern)
        print(f"  {pattern}: {duration:.6f}s")

    # 测试匹配性能
    test_cases = [
        ("yinyue", "音乐"),
        ("yy", "音乐"),
        ("chongqing", "重庆"),
    ]

    print("\n匹配性能测试:")
    for pattern, text in test_cases:
        duration = profiler.profile_matching(pattern, text)
        print(f"  {pattern} 匹配 {text}: {duration:.6f}s")

    # 性能摘要
    print("\n性能摘要:")
    summary = profiler.get_summary()
    for operation, stats in summary.items():
        print(f"  {operation}:")
        print(f"    次数: {stats['count']}")
        print(f"    总时间: {stats['total']:.6f}s")
        print(f"    平均时间: {stats['average']:.6f}s")
        print(f"    最小时间: {stats['min']:.6f}s")
        print(f"    最大时间: {stats['max']:.6f}s")
    print()


def demo_step_by_step():
    """演示步骤调试功能"""
    print("=== Demo 7: 步骤调试 ===")

    pattern = "y.+e"
    text = "音乐"

    print(f"模式: {pattern}, 文本: {text}")

    debug_info = debug_pattern(pattern, text)

    # 打印步骤历史
    debugger = NFADebugger(verbose=False)
    from pinyin_regex.pinyin_utils import text_to_tokens

    tokens = text_to_tokens(text)
    from pinyin_regex.parser import Frag

    start_state = compile_regex(pattern)
    frag = Frag(start_state, start_state)  # 简化

    debugger.debug_run(frag, tokens)
    debugger.print_history()
    print()


def demo_error_cases():
    """演示错误情况调试"""
    print("=== Demo 8: 错误情况调试 ===")

    # 不匹配的情况
    error_cases = [
        ("xyz", "音乐"),  # 完全不匹配
        ("yin.", "音乐"),  # 部分匹配
        ("yinyue", "舞蹈"),  # 文本不匹配
    ]

    for pattern, text in error_cases:
        print(f"模式: {pattern}, 文本: {text}")

        try:
            debug_info = debug_pattern(pattern, text)
            print(f"匹配结果: {debug_info['match_result']}")
            print(f"Tokens: {debug_info['tokens']}")
            print(f"最终状态数: {debug_info['stats'].get('final_states', 0)}")
            print(f"接受状态数: {debug_info['stats'].get('accept_states', 0)}")
        except Exception as e:
            print(f"错误: {e}")

        print("-" * 30)
    print()


def main():
    """主函数，运行所有演示"""
    print("拼音正则表达式调试工具演示")
    print("=" * 50)

    demos = [
        demo_basic_nfa_dump,
        demo_complex_nfa_dump,
        demo_debug_pattern,
        demo_visualization,
        demo_performance_profiling,
        demo_step_by_step,
        demo_error_cases,
    ]

    for i, demo in enumerate(demos, 1):
        try:
            demo()
        except Exception as e:
            print(f"演示 {i} 出错: {e}")
            import traceback

            traceback.print_exc()

        input("按回车键继续下一个演示...")
        print("\n" + "=" * 50 + "\n")

    print("所有演示完成！")


if __name__ == "__main__":
    main()
