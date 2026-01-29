"""
NFA引擎核心模块

实现非确定性有限自动机(NFA)的核心逻辑，包括状态管理、模式匹配等。
"""

from typing import Set, Dict, Any, List, Union, Tuple, Optional
from .pinyin_utils import text_to_tokens


class State:
    """NFA状态类"""

    def __init__(self):
        self.eps: Set["State"] = set()  # epsilon转换
        self.trans: Dict[Union[str, frozenset, Tuple], Set["State"]] = {}  # 字符转换
        self.accept: bool = False  # 是否为接受状态


def epsilon_closure(states: Set[State]) -> Set[State]:
    """计算epsilon闭包

    Args:
        states: 初始状态集合

    Returns:
        epsilon闭包状态集合
    """
    stack = list(states)
    res = set(states)

    while stack:
        s = stack.pop()
        for e in s.eps:
            if e not in res:
                res.add(e)
                stack.append(e)

    return res


def match_label(label: Union[str, frozenset, Tuple], ch_org: str, ch: str) -> bool:
    """检查标签是否匹配字符

    Args:
        label: 匹配标签
        ch_org: 原始字符
        ch: 要匹配的字符

    Returns:
        是否匹配
    """
    # 任意字符
    if label == ".":
        return ch_org not in {"⟨BOS⟩", "⟨EOS⟩"}
    
    if label == "⟨BOS⟩":
        return label == ch
    
    if label == "⟨EOS⟩":
        return label == ch

    # 转义类
    if isinstance(label, str) and label.startswith("\\"):
        if label == r"\d":
            return ch_org.isdigit()
        if label == r"\w":
            return ch_org.isascii() and ch_org.isalnum()
        if label == r"\s":
            return ch_org.isspace()
        if label == r"\z":
            if len(ch_org) != 1:
                return False
            return 0x4E00 <= ord(ch_org) <= 0x9FFF

    # 字符集合
    if isinstance(label, frozenset):
        return ch in label

    # 否定集合
    if isinstance(label, tuple) and label[0] == "NEG":
        return ch not in label[1]

    # 普通字符
    return ch == label


# =========================
# Thompson 构造
# =========================
class Frag:
    """NFA片段类"""

    def __init__(self, start: State, end: State):
        self.start = start
        self.end = end

def clone_frag(frag):
    """复制片段
    Args:
        frag: 片段
    """
    state_map = {}  # old_state -> new_state

    def clone_state(s):
        if s in state_map:
            return state_map[s]

        # 1️⃣ 创建新状态（先放进 map，防止递归环）
        new_s = State()
        new_s.accept = s.accept
        state_map[s] = new_s

        # 2️⃣ 复制 ε 边
        for nxt in s.eps:
            new_s.eps.add(clone_state(nxt))

        # 3️⃣ 复制字符转移
        for sym, targets in s.trans.items():
            new_s.trans[sym] = {clone_state(t) for t in targets}

        return new_s

    new_start = clone_state(frag.start)
    new_end = state_map[frag.end]

    return Frag(new_start, new_end)

def literal_frag(label: Union[str, frozenset, Tuple]) -> Frag:
    """创建字面量片段

    Args:
        label: 字符标签

    Returns:
        NFA片段
    """
    s1, s2 = State(), State()
    s1.trans.setdefault(label, set()).add(s2)
    return Frag(s1, s2)


def concat_frag(a: Frag, b: Frag) -> Frag:
    """连接两个片段

    Args:
        a: 第一个片段
        b: 第二个片段

    Returns:
        连接后的片段
    """
    a.end.eps.add(b.start)
    return Frag(a.start, b.end)


def alt_frag(a: Frag, b: Frag) -> Frag:
    """创建选择片段

    Args:
        a: 第一个片段
        b: 第二个片段

    Returns:
        选择片段
    """
    s, e = State(), State()
    s.eps |= {a.start, b.start}
    a.end.eps.add(e)
    b.end.eps.add(e)
    return Frag(s, e)


def star_frag(a: Frag) -> Frag:
    """创建星号片段（零次或多次）

    Args:
        a: 输入片段

    Returns:
        星号片段
    """
    s, e = State(), State()
    s.eps |= {a.start, e}
    a.end.eps |= {a.start, e}
    return Frag(s, e)


def plus_frag(a: Frag) -> Frag:
    """创建加号片段（一次或多次）

    Args:
        a: 输入片段

    Returns:
        加号片段
    """
    s, e = State(), State()
    s.eps.add(a.start)
    a.end.eps |= {a.start, e}
    return Frag(s, e)


def question_frag(a: Frag) -> Frag:
    """创建问号片段（零次或一次）

    Args:
        a: 输入片段

    Returns:
        问号片段
    """
    s, e = State(), State()
    s.eps |= {a.start, e}
    a.end.eps.add(e)
    return Frag(s, e)


def count_frag(a: Frag, count: int) -> Optional[Frag]:
    """精确重复 count 次

    Args:
        a: 输入片段
        count: 重复次数

    Returns:
        重复后的片段，如果count <= 0则返回None
    """
    if count <= 0:
        return question_frag(a) if count == 0 else star_frag(a)
    
    result = a
    for _ in range(count - 1):
        result = concat_frag(result, clone_frag(a))
    return result


def range_frag(a: Frag, min_count: int, max_count: Union[int, float]) -> Frag:
    """重复 min 到 max 次，max_count 为 float('inf') 表示无上限

    Args:
        a: 输入片段
        min_count: 最小重复次数
        max_count: 最大重复次数

    Returns:
        范围重复片段
    """
    # 处理特殊情况
    if min_count == 0 and max_count == float("inf"):
        return star_frag(a)
    elif min_count == 1 and max_count == float("inf"):
        return plus_frag(a)
    elif min_count == 0 and max_count == 1:
        return question_frag(a)
    elif min_count == 0 and max_count == 0:
        # {0} - 完全跳过 a，等价于空字符串
        s, e = State(), State()
        s.eps.add(e)
        return Frag(s, e)

    s, e = State(), State()

    # 如果 min_count == 0，可以直接跳到结束状态
    if min_count == 0:
        s.eps.add(e)

    # 预先计算必选部分的 fragment（避免重复计算）
    required_frag = None
    if min_count > 0:
        required_frag = count_frag(a, min_count)
        if required_frag:
            s.eps.add(required_frag.start)
            required_frag.end.eps.add(e)

    # 构造可选的额外 max-min 次
    if max_count > min_count:
        # 从必选部分的结束状态开始（如果有必选部分）
        if min_count > 0 and required_frag is not None:
            current = required_frag.end
        else:
            # 没有必选部分，从开始状态开始
            current = s

        # 添加可选的重复次数
        remaining = max_count - min_count
        if remaining == float("inf"):
            # 无限重复，类似 star 逻辑
            current.eps.add(a.start)
            a.end.eps.add(current)
            a.end.eps.add(e)
        else:
            # 有限重复
            for i in range(int(remaining)):
                if i < remaining - 1:
                    # 可以继续重复
                    current.eps.add(a.start)
                    a.end.eps.add(current)
                    current = a.end
                else:
                    # 最后一次可选
                    current.eps.add(a.start)
                    a.end.eps.add(e)

    return Frag(s, e)


def advance_states(states: Set[State], ch_org: str, s: str) -> Set[State]:
    """让NFA状态集推进一个字符

    Args:
        states: 当前状态集合
        ch_org: 原始字符
        s: 要匹配的字符串

    Returns:
        推进后的状态集合
    """
    cur = epsilon_closure(states)

    if s in {"⟨BOS⟩", "⟨EOS⟩"}:
        for st in cur:
            for label, to_states in st.trans.items():
                if match_label(label, ch_org, s):
                    cur = epsilon_closure(to_states)
    else:
        for ch in s:
            nxt = set()
            for st in cur:
                for label, to_states in st.trans.items():
                    if match_label(label, ch_org, ch):
                        nxt |= to_states
            cur = epsilon_closure(nxt)
            if not cur:
                break

    return cur


def run_pinyin_regex(start_state: State, tokens: List[Dict[str, Any]]) -> bool:
    """运行拼音正则表达式匹配

    Args:
        start_state: NFA起始状态
        tokens: 拼音token列表

    Returns:
        是否匹配成功
    """
    start_closure = epsilon_closure({start_state})
    current = set(start_closure)

    for token in tokens:
        next_states = set()

        for py in token["pinyins"]:
            st = advance_states(current, token["char"], py)
            # ⭐ 如果本 token 内已经到 accept，直接成功
            if any(s.accept for s in st):
                return True
            next_states |= st

        next_states |= start_closure
        current = next_states

    return any(st.accept for st in current)
