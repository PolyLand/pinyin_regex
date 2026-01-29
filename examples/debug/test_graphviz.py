#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图形化NFA输出功能
"""

import sys
import os

# 添加项目根目录到路径以便导入pinyin_regex
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pinyin_regex.debug import visualize_nfa, render_nfa_graph, GRAPHVIZ_AVAILABLE
from pinyin_regex import compile_regex


def test_graphviz_features():
    """测试图形化功能"""
    print("测试图形化NFA输出功能...")

    # 简单模式
    pattern = "abc"
    start_state = compile_regex(pattern)

    # 测试DOT格式输出
    print("1. 生成DOT格式:")
    visualize_nfa(start_state, "test_graph.dot", "dot")
    if os.path.exists("test_graph.dot"):
        print("   OK DOT文件生成成功")
        os.remove("test_graph.dot")
    else:
        print("   FAIL DOT文件生成失败")

    # 测试graphviz渲染
    if GRAPHVIZ_AVAILABLE:
        print("2. 生成PNG格式:")
        success = render_nfa_graph(start_state, "test_nfa.png", "png")
        if success and os.path.exists("test_nfa.png"):
            print("   OK PNG文件生成成功")
            os.remove("test_nfa.png")
        else:
            print("   FAIL PNG文件生成失败")
    else:
        print("2. graphviz不可用，跳过图形渲染测试")

    # 测试复杂模式
    pattern2 = "a(b|c)*"
    start_state2 = compile_regex(pattern2)

    print(f"3. 复杂模式 '{pattern2}' 的DOT图:")
    visualize_nfa(start_state2, "complex_graph.dot", "dot")
    if os.path.exists("complex_graph.dot"):
        print("   OK 复杂模式DOT文件生成成功")
        with open("complex_graph.dot", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"   文件包含 {len(lines)} 行")
        os.remove("complex_graph.dot")
    else:
        print("   FAIL 复杂模式DOT文件生成失败")

    # 测试中文模式
    pattern3 = "yinyue"
    start_state3 = compile_regex(pattern3)

    print(f"4. 中文模式 '{pattern3}' 的图形:")
    if GRAPHVIZ_AVAILABLE:
        success = render_nfa_graph(start_state3, "chinese_nfa.png", "png")
        if success and os.path.exists("chinese_nfa.png"):
            print("   OK 中文模式PNG文件生成成功")
            os.remove("chinese_nfa.png")
        else:
            print("   FAIL 中文模式PNG文件生成失败")
    else:
        visualize_nfa(start_state3, "chinese_nfa.dot", "dot")
        if os.path.exists("chinese_nfa.dot"):
            print("   OK 中文模式DOT文件生成成功")
            os.remove("chinese_nfa.dot")
        else:
            print("   FAIL 中文模式DOT文件生成失败")


if __name__ == "__main__":
    test_graphviz_features()
