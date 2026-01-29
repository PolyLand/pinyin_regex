# 拼音正则表达式引擎使用指南

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [正则表达式语法](#正则表达式语法)
- [高级用法](#高级用法)
- [配置选项](#配置选项)
- [API参考](#api参考)
- [性能优化](#性能优化)
- [常见问题](#常见问题)

## 安装

### 使用pip安装

```bash
pip install pinyin-regex
```

### 从源码安装

```bash
git clone https://github.com/example/pinyin-regex.git
cd pinyin-regex
pip install -e .
```

### 开发环境安装

```bash
git clone https://github.com/example/pinyin-regex.git
cd pinyin-regex
pip install -e ".[dev]"
```

## 快速开始

```python
from pinyin_regex import pinyin_regex_match

# 基础拼音匹配
print(pinyin_regex_match("yinyue", "音乐"))  # True
print(pinyin_regex_match("yy", "音乐"))      # True (首字母)

# 模糊音匹配
print(pinyin_regex_match("zong", "中"))      # True (zhong → zong)
print(pinyin_regex_match("si", "是"))       # True (shi → si)

# 正则表达式语法
print(pinyin_regex_match("yin(yue|le)", "音乐"))  # True (或操作)
print(pinyin_regex_match("y.+e", "音乐"))         # True (正则匹配)
```

## 核心功能

### 1. 拼音匹配模式

#### 全拼匹配
```python
pinyin_regex_match("yinyue", "音乐")     # True
pinyin_regex_match("chongqing", "重庆")  # True
pinyin_regex_match("beijing", "北京")    # True
```

#### 首字母匹配
```python
pinyin_regex_match("yy", "音乐")     # True
pinyin_regex_match("cq", "重庆")     # True
pinyin_regex_match("bj", "北京")     # True
```

#### 模糊音匹配
```python
# zh/ch/sh → z/c/s
pinyin_regex_match("zong", "中")     # True (zhong → zong)
pinyin_regex_match("cong", "冲")     # True (chong → cong)
pinyin_regex_match("song", "山")     # False (shan不以sh开头)
pinyin_regex_match("si", "是")       # True (shi → si)
pinyin_regex_match("ci", "吃")       # True (chi → ci)
pinyin_regex_match("zi", "知")       # True (zhi → zi)
```

### 2. 多音字处理

库自动处理汉字的多音字情况：

```python
# "重" 有 chong/zhong 两个读音
pinyin_regex_match("chongqing", "重庆")  # True
pinyin_regex_match("zhongqing", "重庆")  # True

# "长" 有 chang/zhang 两个读音
pinyin_regex_match("changjiang", "长江")  # True
pinyin_regex_match("zhangjiang", "长江")  # True

# "乐" 有 le/yue 两个读音
pinyin_regex_match("le", "乐")   # True
pinyin_regex_match("yue", "乐")  # True
```

## 正则表达式语法

### 基础操作符

| 操作符 | 说明 | 示例 | 结果 |
|--------|------|------|------|
| `|` | 或操作 | `yin(yue\|le)` | 匹配"音乐" |
| `*` | 零次或多次 | `yin.*le` | 匹配"音乐" |
| `+` | 一次或多次 | `y.+e` | 匹配"音乐" |
| `?` | 零次或一次 | `yi?n` | 匹配"音" |
| `[]` | 字符集合 | `[yl]in` | 匹配"音" |
| `[^]` | 否定集合 | `[^z]hong` | 不匹配"中" |
| `.` | 任意字符 | `y.n` | 匹配"音" |
| `^` | 行首锚点 | `^yin` | 匹配行首的"音" |
| `$` | 行尾锚点 | `yue$` | 匹配行尾的"乐" |

### 转义序列

| 转义 | 说明 | 示例 | 结果 |
|------|------|------|------|
| `\d` | 数字字符 | `yin\d` | 匹配"音1" |
| `\w` | ASCII字母数字 | `y\w+e` | 匹配字母序列 |
| `\s` | 空白字符 | `yin\s` | 匹配后跟空格 |
| `\z` | 任意拼音token | `\z+` | 匹配任意中文 |

### 范围量词 {m,n}

| 量词 | 说明 | 示例 | 结果 |
|------|------|------|------|
| `{m}` | 精确m次 | `y{2}` | 匹配两个y开头的字符 |
| `{m,n}` | m到n次 | `y{1,2}` | 匹配1-2个y开头字符 |
| `{m,}` | 至少m次 | `y{1,}` | 匹配至少1个y开头字符 |
| `{0}` | 零次（空字符串） | `y{0}` | 匹配任意文本 |

## 高级用法

### 复杂模式示例

```python
# 多城市名匹配
pinyin_regex_match(
    r"(yin|zhong|chang|bei|shang)[a-z]*", 
    "音乐中国长江北京上海"
)  # True

# 特定模式匹配
pinyin_regex_match(r"[yz][a-z]+", "音乐因应永")  # True
pinyin_regex_match(r".+ing", "北京南京上海")     # True
```

### 子串匹配

支持在长文本中搜索拼音模式：

```python
text = "我的音乐很好听"
pinyin_regex_match("yue", text)           # True
pinyin_regex_match("yin", text)           # True
pinyin_regex_match("hao", text)           # True
```

### 配置选项

可以通过参数控制匹配行为：

```python
# 禁用首字母匹配
pinyin_regex_match("yy", "音乐", use_initials=False)  # False

# 禁用模糊音匹配
pinyin_regex_match("zong", "中", use_fuzzy=False)     # False

# 不按字符分割（整个文本作为一个token）
pinyin_regex_match("yinyue", "音乐", split_chars=False)  # False
```

## 调试和开发工具

### NFA可视化

#### `dump_nfa(start_state)`
打印NFA结构到控制台，用于调试和理解自动机构造。

```python
from pinyin_regex.debug import dump_nfa
from pinyin_regex import compile_regex

start_state = compile_regex("yinyue")
dump_nfa(start_state)
# 输出：
# State 2500617130672  
#   y -> 2500616414672
# State 2500616414672  
#   ε -> 2500616414992
# ...
```

#### `visualize_nfa(start_state, output_file=None, format="dot")`
生成NFA的图形化表示。

```python
from pinyin_regex.debug import visualize_nfa, render_nfa_graph

# 生成DOT文件
visualize_nfa(start_state, "nfa.dot")

# 直接渲染为图片（需要安装graphviz）
render_nfa_graph(start_state, "nfa.png", "png")
```

### 调试模式

#### `debug_pattern(pattern, text, **options)`
提供详细的匹配过程信息，包括状态变化和统计。

```python
from pinyin_regex.debug import debug_pattern

debug_info = debug_pattern("yinyue", "音乐")
print(f"匹配结果: {debug_info['match_result']}")
print(f"Tokens: {debug_info['tokens']}")
print(f"统计: {debug_info['stats']}")
print(f"步骤数: {debug_info['step_count']}")
```

输出示例：
```
{
    'pattern': 'yinyue',
    'text': '音乐',
    'match_result': True,
    'tokens': [{'char': '⟨BOS⟩', 'pinyins': {'⟨BOS⟩'}}, ...],
    'stats': {
        'transitions': 7,
        'epsilon_closures': 9,
        'final_states': 3,
        'accept_states': 1
    },
    'step_count': 10
}
```

### 性能分析

#### `PerformanceProfiler`
用于分析编译和匹配性能。

```python
from pinyin_regex.debug import PerformanceProfiler

profiler = PerformanceProfiler()

# 分析编译性能
duration = profiler.profile_compilation("yinyue")

# 分析匹配性能
duration = profiler.profile_matching("yinyue", "音乐")

# 获取性能摘要
summary = profiler.get_summary()
print(f"编译平均时间: {summary['compilation']['average']:.6f}秒")
print(f"匹配平均时间: {summary['matching']['average']:.6f}秒")
```

### 图形化功能

#### 安装Graphviz支持

为了生成PNG/SVG等格式的NFA图，需要安装graphviz：

```bash
# 安装Python包
pip install graphviz

# 安装系统工具
# Windows: 从 https://graphviz.org/download/ 下载安装
# macOS: brew install graphviz
# Linux: sudo apt-get install graphviz
```

#### 高级可视化选项

```python
from pinyin_regex.debug import NFAVisualizer

# 创建可视化器
visualizer = NFAVisualizer(use_colors=True)

# 生成带颜色的DOT文件
dot_content = visualizer.generate_dot(start_state)

# 直接渲染为图片
result = visualizer.render_graphviz(start_state, "nfa.png", "png")
```

### 调试最佳实践

1. **理解NFA结构**: 使用`dump_nfa`查看自动机构造
2. **性能优化**: 使用`PerformanceProfiler`识别瓶颈
3. **复杂模式调试**: 使用`debug_pattern`分析匹配过程
4. **可视化展示**: 使用图形化工具直观理解模式

## API参考

### 主要函数

#### `pinyin_regex_match(pattern, text, **options)`

主要匹配函数。

**参数:**
- `pattern` (str): 拼音正则表达式模式
- `text` (str): 要搜索的中文文本
- `use_initials` (bool): 是否启用首字母匹配，默认True
- `use_fuzzy` (bool): 是否启用模糊音匹配，默认True  
- `split_chars` (bool): 是否按字符分割，默认True

**返回:**
- `bool`: 是否匹配成功

### 工具函数

#### `text_to_tokens(text, **options)`

将文本转换为拼音token列表。

```python
from pinyin_regex import text_to_tokens

tokens = text_to_tokens("音乐")
# [
#   {"char": "音", "pinyins": {"yin", "y", "音"}},
#   {"char": "乐", "pinyins": {"yue", "le", "y", "乐"}}
# ]
```

#### `expand_pinyin(py, use_initials=True, use_fuzzy=True)`

扩展拼音为变体集合。

```python
from pinyin_regex import expand_pinyin

result = expand_pinyin("zhong")
# {"zhong", "zh", "zong", "z"}
```

#### `get_shengmu(py)`

提取拼音的声母部分。

```python
from pinyin_regex import get_shengmu

get_shengmu("zhong")  # "zh"
get_shengmu("bei")    # "b"
```

### 常量

```python
from pinyin_regex import INITIALS, FUZZY_MAP

# 声母表
INITIALS  # ["zh", "ch", "sh", "b", "p", ...]

# 模糊音映射
FUZZY_MAP  # {"zh": "z", "ch": "c", "sh": "s"}
```

## 性能优化

### 1. 合理使用量词

```python
# 好：明确的范围
pattern = r"y{1,3}"

# 避免：过于宽泛的量词
pattern = r".*"  # 可能导致性能问题
```

### 2. 优先使用简单匹配

```python
# 好：直接匹配
pinyin_regex_match("yinyue", text)

# 可接受：使用正则
pinyin_regex_match(r"y.n.", text)

# 避免：过度复杂的正则
pinyin_regex_match(r".*[yz].*[aeiou].*", text)
```

### 3. 大文本处理

对于大文本，考虑分块处理：

```python
def search_large_text(pattern, large_text, chunk_size=1000):
    for i in range(0, len(large_text), chunk_size):
        chunk = large_text[i:i+chunk_size]
        if pinyin_regex_match(pattern, chunk):
            return True
    return False
```

## 常见问题

### Q: 为什么某些拼音不匹配？

**A:** 检查以下几点：
1. 确认拼音拼写正确
2. 检查是否启用了首字母匹配 (`use_initials=True`)
3. 检查是否启用了模糊音匹配 (`use_fuzzy=True`)
4. 确认目标字符确实是这个读音

### Q: 如何匹配特定声母的所有字符？

**A:** 使用字符类：

```python
# 匹配所有以zh开头的字符
pinyin_regex_match(r"zh[a-z]*", text)

# 使用首字母模式更高效
pinyin_regex_match("zh", text, use_initials=True)
```

### Q: 为什么多音字匹配不成功？

**A:** 确保使用的是该字的有效读音之一：

```python
# "行" 有 xing/hang 两个读音
pinyin_regex_match("xing", "银行")  # True
pinyin_regex_match("hang", "银行")  # True
pinyin_regex_match("li", "银行")    # False (不是有效读音)
```

### Q: 如何提高匹配速度？

**A:** 
1. 使用更具体的模式
2. 避免过度使用 `.*` 等宽泛量词
3. 对于大量文本，考虑预处理或分块
4. 如果不需要，禁用首字母或模糊音匹配

### Q: 支持哪些正则特性？

**A:** 当前支持：
- 基础操作符：`|`, `*`, `+`, `?`, `[]`, `.`
- 转义序列：`\d`, `\w`, `\s`, `\z`
- 范围量词：`{m}`, `{m,n}`, `{m,}`
- 字符类：`[a-z]`, `[^abc]` 等

不支持：
- 环视断言（lookahead/lookbehind）
- 反向引用
- 非贪婪匹配
- 锚点（^, $） - ✅ 已支持行首行尾匹配

### Q: 如何调试匹配失败？

**A:** 使用工具函数查看token：

```python
from pinyin_regex import text_to_tokens

tokens = text_to_tokens("音乐")
for token in tokens:
    print(f"字符: {token['char']}")
    print(f"拼音: {sorted(token['pinyins'])}")
```

## 更多示例

查看 `examples/demo.py` 文件获取更多使用示例。

## 报告问题

如果遇到问题，请：
1. 检查本文档的常见问题部分
2. 查看 GitHub Issues
3. 提交新问题时包含：
   - 完整的模式和文本
   - 期望的结果和实际结果
   - 使用的配置选项