#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼音正则表达式引擎使用示例

演示如何使用pinyin_regex库进行各种拼音匹配操作。
"""

import sys
import os

# 添加项目根目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pinyin_regex import (
    pinyin_regex_match,
    text_to_tokens,
    expand_pinyin,
    get_shengmu,
    INITIALS,
    FUZZY_MAP,
)


def basic_examples():
    """基础功能示例"""
    print("=== 基础拼音匹配示例 ===")

    # 全拼匹配
    examples = [
        ("yinyue", "音乐", "全拼匹配"),
        ("chongqing", "重庆", "全拼匹配"),
        ("beijing", "北京", "全拼匹配"),
        ("yy", "音乐", "首字母匹配"),
        ("cq", "重庆", "首字母匹配"),
        ("bj", "北京", "首字母匹配"),
        ("zong", "中", "模糊音匹配 zhong→zong"),
        ("si", "是", "模糊音匹配 shi→si"),
        ("ci", "吃", "模糊音匹配 chi→ci"),
    ]

    for pattern, text, description in examples:
        result = pinyin_regex_match(pattern, text)
        print(f"{pattern:12} vs {text:6} -> {result} ({description})")


def regex_examples():
    """正则表达式功能示例"""
    print("\n=== 正则表达式功能示例 ===")

    regex_examples = [
        ("yin(yue|le)", "音乐", "或操作"),
        ("(yin|zhong)", "音乐", "选择匹配"),
        ("yin.*le", "音乐", "零次或多次重复"),
        ("y.+e", "音乐", "一次或多次重复"),
        ("yi?n", "音", "零次或一次重复"),
        (r"y\w+e", "音乐", "字母字符类"),
        (r"\z\z", "音乐", "中文token类"),
        (r"[yl]in", "音", "字符集合"),
        (r"y[a-z]+e", "音乐", "字符范围"),
        (r"[^z]hong", "中", "否定字符集合"),
    ]

    for pattern, text, description in regex_examples:
        result = pinyin_regex_match(pattern, text)
        print(f"{pattern:15} vs {text:6} -> {result} ({description})")


def range_quantifier_examples():
    """范围量词示例"""
    print("\n=== 范围量词 {m,n} 示例 ===")

    range_examples = [
        (r"y{2}", "音乐", "精确重复2次"),
        (r"y{1,2}", "音乐", "重复1-2次"),
        (r"y{1,}", "音乐", "至少重复1次"),
        (r"yin{1,2}", "音乐因", "拼音重复1-2次"),
        (r"y{0}", "音乐", "空重复（匹配任何文本）"),
    ]

    for pattern, text, description in range_examples:
        result = pinyin_regex_match(pattern, text)
        print(f"{pattern:15} vs {text:8} -> {result} ({description})")


def substring_matching_examples():
    """子串匹配示例"""
    print("\n=== 子串匹配示例 ===")

    substring_examples = [
        ("yue", "我的音乐很好听", "在长文本中搜索"),
        ("yin", "纯音乐欣赏", "子串匹配"),
        ("beijing", "我爱北京天安门", "城市名子串"),
        ("yinyue", "背景音乐很重要", "多字子串"),
    ]

    for pattern, text, description in substring_examples:
        result = pinyin_regex_match(pattern, text)
        print(f"{pattern:12} vs '{text}' -> {result} ({description})")


def utility_function_examples():
    """工具函数示例"""
    print("\n=== 工具函数示例 ===")

    # 声母提取
    print("声母提取:")
    pinyins = ["zhong", "chang", "shang", "bei", "a"]
    for py in pinyins:
        shengmu = get_shengmu(py)
        print(f"  {py} -> {shengmu}")

    # 拼音扩展
    print("\n拼音扩展 (含首字母和模糊音):")
    zhong_expanded = expand_pinyin("zhong", use_initials=True, use_fuzzy=True)
    print(f"  zhong -> {sorted(zhong_expanded)}")

    # 文本转token
    print("\n文本转拼音token:")
    text = "音乐"
    tokens = text_to_tokens(text)
    for i, token in enumerate(tokens):
        print(f"  字符 '{token['char']}' -> 拼音: {sorted(token['pinyins'])}")


def advanced_examples():
    """高级功能示例"""
    print("\n=== 高级功能示例 ===")

    # 多音字处理
    print("多音字处理:")
    polyphonic_examples = [
        ("chongqing", "重庆", "重: chong/zhong"),
        ("zhongqing", "重庆", "重: chong/zhong"),
        ("changjiang", "长江", "长: chang/zhang"),
        ("zhangjiang", "长江", "长: chang/zhang"),
        ("le", "乐", "乐: le/yue"),
        ("yue", "乐", "乐: le/yue"),
    ]

    for pattern, text, description in polyphonic_examples:
        result = pinyin_regex_match(pattern, text)
        print(f"  {pattern:12} vs {text:6} -> {result} ({description})")

    # 复杂模式
    print("\n复杂正则模式:")
    complex_patterns = [
        (r"(yin|zhong|chang|bei)[a-z]*", "音乐中国长江北京", "多个城市名匹配"),
        (r"[yz][a-z]+", "音乐因应永", "以y或z开头的拼音"),
        (r".+ing", "北京南京上海", "以ing结尾的拼音"),
    ]

    for pattern, text, description in complex_patterns:
        result = pinyin_regex_match(pattern, text)
        print(f"  {pattern:25} vs '{text}' -> {result} ({description})")


def configuration_examples():
    """配置选项示例"""
    print("\n=== 配置选项示例 ===")

    pattern = "zhong"
    text = "中"

    # 不同配置的匹配结果
    configs = [
        (True, True, "启用首字母和模糊音"),
        (True, False, "启用首字母，禁用模糊音"),
        (False, True, "禁用首字母，启用模糊音"),
        (False, False, "禁用首字母和模糊音"),
    ]

    print(f"模式: {pattern}, 文本: {text}")
    for use_initials, use_fuzzy, description in configs:
        result = pinyin_regex_match(pattern, text, use_initials=use_initials, use_fuzzy=use_fuzzy)
        print(f"  {description:25} -> {result}")


def main():
    """主函数"""
    print("拼音正则表达式引擎使用示例")
    print("=" * 50)

    try:
        basic_examples()
        regex_examples()
        range_quantifier_examples()
        substring_matching_examples()
        utility_function_examples()
        advanced_examples()
        configuration_examples()

        print("\n" + "=" * 50)
        print("所有示例运行完成！")

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保pinyin_regex包已正确安装")
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
