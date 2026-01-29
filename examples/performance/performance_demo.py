#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控和统计功能演示
"""

import sys
import os

# 添加项目根目录到路径以便导入pinyin_regex
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pinyin_regex.debug import PerformanceProfiler
from pinyin_regex import pinyin_regex_match, compile_regex
from pinyin_regex.pinyin_utils import text_to_tokens


def benchmark_compilation():
    """编译性能基准测试"""
    print("=== 编译性能基准测试 ===")

    profiler = PerformanceProfiler()

    # 测试不同复杂度的模式
    patterns = [
        "a",  # 简单字符
        "ab",  # 两个字符
        "abc",  # 三个字符
        "a(b|c)",  # 或操作
        "a(b|c)*",  # 重复
        "a(b|c)+d(e|f)*",  # 复杂模式
        "[a-z]+",  # 字符类
        "yin(yue|le)+",  # 中文模式
        "y.+e",  # 通配符
        "y{1,3}in",  # 量词
    ]

    print("模式编译时间测试:")
    print(f"{'模式':<20} {'时间(秒)':<12} {'状态数':<8}")
    print("-" * 45)

    for pattern in patterns:
        # 测试编译时间
        duration = profiler.profile_compilation(pattern)

        # 计算状态数
        start_state = compile_regex(pattern)
        state_count = count_states(start_state)

        print(f"{pattern:<20} {duration:<12.6f} {state_count:<8}")

    # 编译性能摘要
    summary = profiler.get_summary()
    if "compilation" in summary:
        stats = summary["compilation"]
        print(f"\n编译性能摘要:")
        print(f"  总测试数: {stats['count']}")
        print(f"  平均时间: {stats['average']:.6f}秒")
        print(f"  最快时间: {stats['min']:.6f}秒")
        print(f"  最慢时间: {stats['max']:.6f}秒")


def benchmark_matching():
    """匹配性能基准测试"""
    print("\n=== 匹配性能基准测试 ===")

    profiler = PerformanceProfiler()

    # 测试用例
    test_cases = [
        ("yinyue", "音乐"),
        ("yy", "音乐"),
        ("chongqing", "重庆"),
        ("cq", "重庆"),
        ("beijing", "北京"),
        ("bj", "北京"),
        ("yin(yue|le)", "音乐"),
        ("y.+e", "音乐"),
        ("[a-z]+", "test"),
        ("y{1,2}", "音乐"),
    ]

    print("匹配时间测试:")
    print(f"{'模式':<20} {'文本':<8} {'时间(秒)':<12} {'结果':<6}")
    print("-" * 50)

    for pattern, text in test_cases:
        duration = profiler.profile_matching(pattern, text)
        result = pinyin_regex_match(pattern, text)

        print(f"{pattern:<20} {text:<8} {duration:<12.6f} {result:<6}")

    # 匹配性能摘要
    summary = profiler.get_summary()
    if "matching" in summary:
        stats = summary["matching"]
        print(f"\n匹配性能摘要:")
        print(f"  总测试数: {stats['count']}")
        print(f"  平均时间: {stats['average']:.6f}秒")
        print(f"  最快时间: {stats['min']:.6f}秒")
        print(f"  最慢时间: {stats['max']:.6f}秒")


def benchmark_tokenization():
    """Token化性能测试"""
    print("\n=== Token化性能测试 ===")

    profiler = PerformanceProfiler()

    # 测试不同长度的文本
    test_texts = [
        "音",
        "音乐",
        "音乐很好",
        "音乐非常好听",
        "音乐非常好听我喜欢",
        "音乐非常好听我喜欢听音乐",
        "音乐非常好听我喜欢听音乐因为音乐能让我放松心情",
    ]

    print("Token化时间测试:")
    print(f"{'文本长度':<8} {'时间(秒)':<12} {'Token数':<8}")
    print("-" * 35)

    for text in test_texts:
        start_time = profiler.perf_counter()
        tokens = text_to_tokens(text)
        end_time = profiler.perf_counter()

        duration = end_time - start_time
        profiler.timings["tokenization"].append(duration)

        print(f"{len(text):<8} {duration:<12.6f} {len(tokens):<8}")

    # Token化性能摘要
    summary = profiler.get_summary()
    if "tokenization" in summary:
        stats = summary["tokenization"]
        print(f"\nToken化性能摘要:")
        print(f"  总测试数: {stats['count']}")
        print(f"  平均时间: {stats['average']:.6f}秒")
        print(f"  最快时间: {stats['min']:.6f}秒")
        print(f"  最慢时间: {stats['max']:.6f}秒")


def memory_usage_analysis():
    """内存使用分析"""
    print("\n=== 内存使用分析 ===")

    try:
        import psutil

        process = psutil.Process()

        # 基线内存
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"基线内存使用: {baseline_memory:.2f} MB")

        # 编译多个模式后的内存
        patterns = ["a" * i for i in range(1, 20)]  # 1-19个字符的模式
        compiled_states = []

        for pattern in patterns:
            start_state = compile_regex(pattern)
            compiled_states.append(start_state)

        after_compile_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"编译{len(patterns)}个模式后: {after_compile_memory:.2f} MB")
        print(f"内存增长: {after_compile_memory - baseline_memory:.2f} MB")

        # 清理
        del compiled_states

    except ImportError:
        print("psutil未安装，无法进行内存分析")
        print("请使用 'pip install psutil' 安装")


def count_states(start_state):
    """计算NFA状态数"""
    visited = set()
    stack = [start_state]

    while stack:
        s = stack.pop()
        if s in visited:
            continue
        visited.add(s)

        stack.extend(s.eps)
        for targets in s.trans.values():
            stack.extend(targets)

    return len(visited)


def performance_comparison():
    """性能对比测试"""
    print("\n=== 性能对比测试 ===")

    profiler = PerformanceProfiler()

    # 对比不同选项的性能
    pattern = "yinyue"
    text = "音乐"

    options_list = [
        {"use_initials": True, "use_fuzzy": True, "split_chars": True},
        {"use_initials": False, "use_fuzzy": True, "split_chars": True},
        {"use_initials": True, "use_fuzzy": False, "split_chars": True},
        {"use_initials": True, "use_fuzzy": True, "split_chars": False},
    ]

    print("不同选项的性能对比:")
    print(f"{'选项':<40} {'时间(秒)':<12}")
    print("-" * 55)

    for options in options_list:
        duration = profiler.profile_matching(pattern, text, **options)
        options_str = str(options).replace("'", "")[1:-1]  # 美化显示
        print(f"{options_str:<40} {duration:<12.6f}")


def main():
    """运行所有性能测试"""
    print("拼音正则表达式性能监控演示")
    print("=" * 50)

    benchmark_compilation()
    benchmark_matching()
    benchmark_tokenization()
    memory_usage_analysis()
    performance_comparison()

    print("\n" + "=" * 50)
    print("性能测试完成！")


if __name__ == "__main__":
    main()
