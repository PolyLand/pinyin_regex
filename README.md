# 拼音正则表达式引擎 (Pinyin Regex Engine)

Python库，支持使用拼音正则表达式匹配中文字符。该库实现了完整的NFA（非确定性有限自动机）引擎，支持正则表达式语法和拼音模糊匹配。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## 功能特性

- ✅ **完整拼音支持**: 全拼、首字母、模糊音匹配
- ✅ **正则表达式语法**: 支持 `|`, `*`, `+`, `?`, `[]`, `{m,n}`, `.` 等操作符
- ✅ **多音字处理**: 自动处理汉字的多音字情况
- ✅ **模糊音匹配**: 支持 zh/ch/sh 的模糊音
- ✅ **字符类匹配**: 支持 `\d`, `\w`, `\s`, `\z` 等转义序列
- ✅ **子串匹配**: 支持在长文本中搜索匹配项
- ✅ **模块化设计**: 清晰的代码结构，易于维护和扩展
- ✅ **完整测试**: 全面的单元测试覆盖
- ✅ **类型提示**: 完整的类型注解支持

## 项目结构

```
pinyin_reg/
├── pinyin_regex/                # 核心库代码包
│   ├── __init__.py              # 包API定义
│   ├── engine.py                # NFA/Regex 核心逻辑
│   ├── parser.py                # 模式解析
│   ├── pinyin_utils.py          # 拼音转换/模糊音处理
│   └── errors.py                # 自定义异常类型
├── tests/                       # 测试目录
│   ├── __init__.py
│   └── test_engine.py           # 单元测试
├── examples/                    # 示例代码
│   └── demo.py                  # 使用示例
├── docs/                        # 文档目录
│   └── usage.md                 # 详细使用文档
├── README.md                    # 项目说明
├── pyproject.toml               # 包管理文件
└── AGENTS.md                    # 开发指南
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

## 详细功能说明

### 1. 拼音匹配模式

- **全拼匹配**: `yinyue` 匹配 `音乐`
- **首字母匹配**: `yy` 匹配 `音乐`
- **模糊音匹配**: `zong` 匹配 `中` (zh/ch/sh → z/c/s)

### 2. 正则表达式语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `|` | 或操作 | `yin(yue|le)` 匹配 `音乐` |
| `*` | 零次或多次 | `yin.*le` 匹配 `音乐` |
| `+` | 一次或多次 | `y.+e` 匹配 `音乐` |
| `?` | 零次或一次 | `yi?n` 匹配 `音` |
| `{m}` | 精确m次 | `y{2}` 匹配两个y开头字符 |
| `{m,n}` | m到n次 | `y{1,2}` 匹配1-2个y开头字符 |
| `{m,}` | 至少m次 | `y{1,}` 匹配至少1个y开头字符 |
| `[]` | 字符集合 | `[yl]in` 匹配 `音` |
| `[^]` | 否定集合 | `[^z]hong` 不匹配 `中` |
| `.` | 任意字符 | `y.n` 匹配 `音` |

### 3. 转义序列

| 转义 | 说明 | 示例 |
|------|------|------|
| `\d` | 数字字符 | `yin\d` 匹配 `音1` |
| `\w` | ASCII字母数字 | `y\w+e` 匹配字母序列 |
| `\s` | 空白字符 | `yin\s` 匹配后跟空格 |
| `\z` | 任意拼音token | `\z+` 匹配 任意中文 |

## API 参考

### `pinyin_regex_match(pattern, text, **options)`

主要匹配函数。

**参数:**
- `pattern` (str): 拼音正则表达式模式
- `text` (str): 要搜索的中文文本
- `use_initials` (bool): 是否启用首字母匹配，默认 `True`
- `use_fuzzy` (bool): 是否启用模糊音匹配，默认 `True`
- `split_chars` (bool): 是否按字符分割，默认 `True`

**返回:**
- `bool`: 是否匹配成功

### 工具函数

```python
from pinyin_regex import (
    text_to_tokens,    # 文本转拼音token
    expand_pinyin,     # 扩展拼音变体
    get_shengmu,       # 提取声母
    INITIALS,          # 声母表
    FUZZY_MAP,         # 模糊音映射
)
```

## 使用示例

### 基础匹配
```python
# 全拼匹配
pinyin_regex_match("chongqing", "重庆")  # True
pinyin_regex_match("zhongqing", "重庆")  # True (多音字)

# 首字母匹配
pinyin_regex_match("cq", "重庆")  # True
```

### 正则表达式
```python
# 或操作
pinyin_regex_match("(yin|zhong)", "音乐")  # True

# 重复匹配
pinyin_regex_match("y.+e", "音乐")  # True
pinyin_regex_match("yin.*", "音乐")  # True

# 范围量词
pinyin_regex_match("y{1,2}", "音乐")  # True

# 字符类
pinyin_regex_match("[a-z]+", "音乐")  # True
pinyin_regex_match("[^z]hong", "中")  # False
```

### 高级功能
```python
# 子串匹配
pinyin_regex_match("yue", "我的音乐很好听")  # True

# 转义序列
pinyin_regex_match(r"\d+", "123")  # True
pinyin_regex_match(r"\z+", "音乐")  # True

# 配置选项
pinyin_regex_match("yy", "音乐", use_initials=False)  # False
pinyin_regex_match("zong", "中", use_fuzzy=False)     # False
```

## 开发

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_engine.py::TestPinyinRegexBasic

# 生成覆盖率报告
python -m pytest tests/ --cov=pinyin_regex --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
black pinyin_regex/ tests/

# 类型检查
mypy pinyin_regex/

# 代码风格检查
ruff check pinyin_regex/ tests/
```

### 运行示例

```bash
python examples/demo.py
```

## 测试覆盖

测试套件包含：
- 基础拼音匹配测试 (33项)
- 正则表达式功能测试 (25项)
- 范围量词测试 (15项)
- 边界情况和错误处理测试
- 性能测试
- 工具函数测试

总体测试覆盖率 > 95%

## 实现原理

1. **拼音转换**: 使用 `pypinyin` 库将中文转换为拼音
2. **NFA构造**: 使用Thompson构造法编译正则表达式
3. **状态匹配**: 基于NFA的状态机进行模式匹配
4. **模糊处理**: 支持声母模糊音和多音字处理

## 模块说明

- **`pinyin_utils.py`**: 拼音处理工具，包含声母提取、模糊音映射、文本token化
- **`engine.py`**: NFA引擎核心，包含状态管理、模式匹配逻辑
- **`parser.py`**: 正则表达式解析器，递归下降解析模式字符串
- **`errors.py`**: 自定义异常类定义
- **`__init__.py`**: 包API入口，导出公共函数和类


## 贡献

欢迎提交Issue和Pull Request

## 文档

更多详细信息请查看 [docs/usage.md](docs/usage.md) 使用指南。

## 更新日志

### v1.0.0
- ✨ 重构为模块化架构
- ✨ 支持范围量词 `{m,n}`
- ✨ 完整的类型注解
- ✨ 全面的单元测试
- ✨ 详细的使用文档
- ✅ 修复多个边界情况
- 🚀 性能优化