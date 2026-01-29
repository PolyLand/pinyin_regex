"""
拼音正则表达式调试工具模块

提供NFA可视化、调试运行、性能分析等功能，用于开发和调试。
"""

import time
import os
from typing import Set, Dict, List, Any, Optional, Union
from collections import defaultdict

from .engine import State, epsilon_closure, advance_states
from .pinyin_utils import text_to_tokens
from .parser import compile_regex

# 可选的graphviz支持
try:
    import graphviz

    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


class NFAVisualizer:
    """NFA可视化工具类"""

    def __init__(self, use_colors: bool = True):
        self.visited_states: Set[int] = set()
        self.state_info: Dict[int, Dict[str, Any]] = {}
        self.use_colors = use_colors

    def dump_nfa(self, start: State) -> None:
        """将NFA结构打印到stdout

        Args:
            start: NFA起始状态
        """
        visited = set()
        stack = [start]

        print("=== NFA Structure ===")

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            state_id = id(s)
            accept_marker = "ACCEPT" if s.accept else ""
            print(f"State {state_id}  {accept_marker}")

            # 打印epsilon转换
            for e in s.eps:
                print(f"  ε  -> {id(e)}")

            # 打印字符转换
            for sym, targets in s.trans.items():
                for t in targets:
                    print(f"  {sym} -> {id(t)}")

            stack.extend(s.eps)
            for targets in s.trans.values():
                stack.extend(targets)

        print("====================")

    def generate_dot(self, start: State) -> str:
        """生成Graphviz DOT格式的NFA图

        Args:
            start: NFA起始状态

        Returns:
            DOT格式的字符串
        """
        visited = set()
        stack = [start]
        lines = ["digraph NFA {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=circle];")

        # 添加起始状态标记
        lines.append(f"  start [shape=point, style=invis];")
        lines.append(f'  start -> {id(start)} [label="start"];')

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            state_id = id(s)

            # 接受状态用双圆圈
            if s.accept:
                lines.append(f"  {state_id} [shape=doublecircle];")

            # epsilon转换
            for e in s.eps:
                lines.append(f'  {state_id} -> {id(e)} [label="ε", style=dashed];')

            # 字符转换
            for sym, targets in s.trans.items():
                for t in targets:
                    # 转义特殊字符
                    safe_sym = str(sym).replace('"', '\\"')
                    lines.append(f'  {state_id} -> {id(t)} [label="{safe_sym}"];')

            stack.extend(s.eps)
            for targets in s.trans.values():
                stack.extend(targets)

        lines.append("}")
        return "\n".join(lines)

    def render_graphviz(
        self, start: State, output_file: str = None, format: str = "png"
    ) -> Optional[str]:
        """使用graphviz渲染NFA图

        Args:
            start: NFA起始状态
            output_file: 输出文件名，如果为None则使用临时文件
            format: 输出格式（png, svg, pdf等）

        Returns:
            生成的文件路径，如果graphviz不可用则返回None
        """
        if not GRAPHVIZ_AVAILABLE:
            print("警告: graphviz未安装，无法生成图形")
            print("请使用 'pip install graphviz' 安装graphviz Python包")
            print("并安装Graphviz系统工具: https://graphviz.org/download/")
            return None

        # 创建有向图
        dot = graphviz.Digraph(comment="NFA", format=format)
        dot.attr(rankdir="LR")
        dot.attr("node", shape="circle")

        visited = set()
        stack = [start]

        # 添加起始节点标记
        dot.node("start", shape="point", style="invis")

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            state_id = str(id(s))

            # 设置节点样式
            if s.accept:
                dot.node(state_id, shape="doublecircle", color="red", penwidth="2")
            else:
                dot.node(state_id, color="blue")

        # 重新遍历以添加边
        visited = set()
        stack = [start]

        # 连接起始节点到起始状态
        dot.edge("start", str(id(start)), label="start", style="bold")

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            state_id = str(id(s))

            # epsilon转换
            for e in s.eps:
                target_id = str(id(e))
                dot.edge(state_id, target_id, label="ε", style="dashed", color="green")
                stack.append(e)

            # 字符转换
            for sym, targets in s.trans.items():
                for t in targets:
                    target_id = str(id(t))
                    safe_sym = str(sym).replace('"', '\\"')

                    # 根据符号类型设置颜色
                    if isinstance(sym, str) and sym.startswith("⟨"):
                        # 特殊符号用紫色
                        dot.edge(state_id, target_id, label=safe_sym, color="purple")
                    else:
                        # 普通符号用黑色
                        dot.edge(state_id, target_id, label=safe_sym, color="black")

                    stack.append(t)

        # 渲染图形
        if output_file:
            # 去掉扩展名，让graphviz自动添加
            base_name = os.path.splitext(output_file)[0]
            dot.render(base_name, cleanup=True)
            return f"{base_name}.{format}"
        else:
            # 使用临时文件
            dot.render("nfa_temp", cleanup=True)
            return f"nfa_temp.{format}"


class NFADebugger:
    """NFA调试运行器"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.stats = defaultdict(int)
        self.step_history: List[Dict[str, Any]] = []

    def debug_run(self, start_state: State, tokens: List[Any]) -> bool:
        """调试运行NFA，记录详细步骤

        Args:
            start_state: NFA起始状态（已包含accept状态设置）
            tokens: 输入token列表

        Returns:
            是否匹配成功
        """
        self.stats.clear()
        self.step_history.clear()

        # 初始化状态集合，与run_pinyin_regex保持一致
        start_closure = epsilon_closure({start_state})
        current = set(start_closure)

        if self.verbose:
            print(f"INIT: {[id(s) for s in current]}")

        self.step_history.append(
            {"step": 0, "token": None, "states": [id(s) for s in current], "epsilon_closure": True}
        )

        for i, tok in enumerate(tokens, 1):
            if self.verbose:
                print(f"\nREAD TOKEN: {tok}")

            nxt_states = set()
            transition_count = 0

            # 与run_pinyin_regex保持一致的逻辑
            if isinstance(tok, dict):
                # 对于字典token，检查pinyins字段
                for py in tok.get("pinyins", []):
                    st = advance_states(current, tok["char"], py)
                    # ⭐ 如果本 token 内已经到 accept，直接成功
                    if any(s.accept for s in st):
                        if self.verbose:
                            print(f"EARLY ACCEPT at step {i}")
                        return True
                    nxt_states |= st
                    transition_count += 1
            else:
                # 对于简单字符串token
                st = advance_states(current, tok, tok)
                if any(s.accept for s in st):
                    if self.verbose:
                        print(f"EARLY ACCEPT at step {i}")
                    return True
                nxt_states |= st
                transition_count += 1

            self.stats["epsilon_closures"] += 1
            # 与run_pinyin_regex保持一致，加入start_closure
            nxt_states |= start_closure
            current = nxt_states

            if self.verbose:
                print(f"NOW: {[id(s) for s in current]}")

            self.step_history.append(
                {
                    "step": i,
                    "token": tok,
                    "states": [id(s) for s in current],
                    "epsilon_closure": True,
                    "transitions_used": transition_count,
                }
            )

        accept = any(s.accept for s in current)
        self.stats["final_states"] = len(current)
        self.stats["accept_states"] = sum(1 for s in current if s.accept)

        if self.verbose:
            print(f"\nACCEPT? {accept}")
            print(f"Final states: {len(current)}")
            print(f"Accept states: {self.stats['accept_states']}")

        return accept

    def get_stats(self) -> Dict[str, int]:
        """获取运行统计信息

        Returns:
            统计信息字典
        """
        return dict(self.stats)

    def print_history(self) -> None:
        """打印步骤历史"""
        print("\n=== Step History ===")
        for step_info in self.step_history:
            step = step_info["step"]
            token = step_info["token"] or "START"
            states = step_info["states"]
            print(f"Step {step}: Token='{token}' -> States={states}")
        print("===================")


class PerformanceProfiler:
    """性能分析器"""

    def __init__(self):
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.memory_usage: List[int] = []

    def profile_compilation(self, pattern: str) -> float:
        """分析正则表达式编译性能

        Args:
            pattern: 正则表达式模式

        Returns:
            编译耗时（秒）
        """
        start_time = time.perf_counter()
        compile_regex(pattern)
        end_time = time.perf_counter()

        duration = end_time - start_time
        self.timings["compilation"].append(duration)
        return duration

    def profile_matching(self, pattern: str, text: str, **options) -> float:
        """分析匹配性能

        Args:
            pattern: 正则表达式模式
            text: 匹配文本
            **options: 匹配选项

        Returns:
            匹配耗时（秒）
        """
        from . import pinyin_regex_match

        start_time = time.perf_counter()
        pinyin_regex_match(pattern, text, **options)
        end_time = time.perf_counter()

        duration = end_time - start_time
        self.timings["matching"].append(duration)
        return duration

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """获取性能摘要

        Returns:
            性能摘要字典
        """
        summary = {}
        for operation, times in self.timings.items():
            if times:
                summary[operation] = {
                    "count": len(times),
                    "total": sum(times),
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }
        return summary

    def perf_counter(self) -> float:
        """获取高性能计时器

        Returns:
            当前时间（秒）
        """
        return time.perf_counter()


# 便捷函数，保持向后兼容
def dump_nfa(start: State) -> None:
    """Dump NFA to stdout (向后兼容函数)"""
    visualizer = NFAVisualizer()
    visualizer.dump_nfa(start)


def debug_run(start_state: State, tokens: List[Any]) -> bool:
    """Debug run NFA (向后兼容函数)"""
    debugger = NFADebugger(verbose=True)
    return debugger.debug_run(start_state, tokens)


# 新增的便捷函数
def visualize_nfa(start: State, output_file: Optional[str] = None, format: str = "dot") -> None:
    """可视化NFA，可选择保存到文件

    Args:
        start: NFA起始状态
        output_file: 输出文件路径，如果为None则打印到stdout
        format: 输出格式（dot, png, svg等）
    """
    visualizer = NFAVisualizer()

    if format == "dot" or not GRAPHVIZ_AVAILABLE:
        # 生成DOT格式
        dot_content = visualizer.generate_dot(start)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(dot_content)
            print(f"NFA DOT graph saved to: {output_file}")
        else:
            print(dot_content)
    else:
        # 使用graphviz渲染
        result = visualizer.render_graphviz(start, output_file, format)
        if result:
            print(f"NFA graph saved to: {result}")
        else:
            print("Failed to generate NFA graph")


def render_nfa_graph(start: State, output_file: str, format: str = "png") -> bool:
    """渲染NFA为图形文件

    Args:
        start: NFA起始状态
        output_file: 输出文件名
        format: 图形格式（png, svg, pdf等）

    Returns:
        是否成功生成
    """
    visualizer = NFAVisualizer()
    result = visualizer.render_graphviz(start, output_file, format)
    return result is not None


def debug_pattern(pattern: str, text: str, **options) -> Dict[str, Any]:
    """调试正则表达式匹配，返回详细信息

    Args:
        pattern: 正则表达式模式
        text: 匹配文本
        **options: 匹配选项

    Returns:
        调试信息字典
    """
    from . import pinyin_regex_match

    # 编译模式获取起始状态
    start_state = compile_regex(pattern.lower())

    # 获取tokens
    tokens = text_to_tokens(
        text,
        use_initials=options.get("use_initials", True),
        use_fuzzy=options.get("use_fuzzy", True),
        split_chars=options.get("split_chars", True),
    )

    # 调试运行
    debugger = NFADebugger(verbose=False)
    result = debugger.debug_run(start_state, tokens)

    return {
        "pattern": pattern,
        "text": text,
        "tokens": tokens,
        "match_result": result,
        "stats": debugger.get_stats(),
        "step_count": len(debugger.step_history),
    }


__all__ = [
    "NFAVisualizer",
    "NFADebugger",
    "PerformanceProfiler",
    "dump_nfa",
    "debug_run",
    "visualize_nfa",
    "render_nfa_graph",
    "debug_pattern",
    "GRAPHVIZ_AVAILABLE",
]
