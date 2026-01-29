# 拼音正则表达式引擎 - 开发指南

本文档为参与该项目的开发者提供详细的开发指南和代码约定。

## 项目概览

这是一个Python库，支持使用拼音正则表达式匹配中文字符。实现了完整的NFA（非确定性有限自动机）引擎，支持正则表达式语法和拼音模糊匹配。

## 核心设计

### 汉字拆分机制

与传统正则表达式不同，本项目采用独特的汉字拆分策略，将每个中文字符拆分为多种匹配形式：

- **拼音全拼**：如"音" → "yin"
- **拼音首字母**：如"音" → "y"  
- **原始字符**：如"音" → "音"
- **多音字变体**：如"乐" → "le", "yue"

这种设计使得用户可以使用拼音、首字母或混合方式来匹配中文字符，大大提高了匹配的灵活性。

### 双层匹配机制

项目实现了双层匹配机制，通过不同的token字段支持不同的匹配策略：

#### 1. 常规匹配 (使用 token["pinyins"])
- **用途**：精确的拼音匹配
- **匹配内容**：拼音全拼、首字母、原始字符
- **示例**：`token["pinyins"] = {"yin", "y", "音"}`

#### 2. 模糊匹配 (使用 token["char"])
- **用途**：字符级别的模糊匹配
- **匹配内容**：仅原始字符
- **示例**：`token["char"] = "音"`

### 工作流程示例

以匹配模式 `"yy"` 与文本 `"音乐"` 为例：

1. **文本处理**：
   ```
   "音乐" → [
     {"char": "音", "pinyins": {"yin", "y", "音"}},
     {"char": "乐", "pinyins": {"yue", "le", "y", "l", "乐"}}
   ]
   ```

2. **匹配过程**：
   - 第一个字符匹配：`y` → `{"yin", "y", "音"}` ✓
   - 第二个字符匹配：`y` → `{"yue", "le", "y", "l", "乐"}` ✓

3. **结果**：匹配成功

### 设计优势

1. **灵活性**：支持多种拼音输入方式
2. **兼容性**：保持传统正则表达式的语法
3. **扩展性**：易于添加新的拼音变体或匹配规则
4. **性能**：通过NFA引擎高效处理复杂匹配

## 构建和测试命令

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/example/pinyin-regex.git
cd pinyin-regex

# 安装开发依赖
pip install -e ".[dev]"
```

### 测试命令
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试类
python -m pytest tests/test_engine.py::TestPinyinRegexBasic

# 运行单个测试方法
python -m pytest tests/test_engine.py::TestPinyinRegexBasic::test_full_pinyin_match

# 生成覆盖率报告
python -m pytest tests/ --cov=pinyin_regex --cov-report=html

# 运行标记的测试
python -m pytest -m "not slow"  # 跳过慢测试
python -m pytest -m unit       # 只运行单元测试
```

### 代码质量检查
```bash
# 代码格式化
black pinyin_regex/ tests/

# 类型检查
mypy pinyin_regex/

# 代码风格检查
ruff check pinyin_regex/ tests/

# 自动修复ruff问题
ruff check pinyin_regex/ tests/ --fix
```

### 调试和开发工具
```bash
# 运行调试演示
python examples/debug/debug_demo.py

# 运行调试测试
python examples/debug/debug_test.py

# 测试图形化功能
python examples/debug/test_graphviz.py

# 运行性能分析
python examples/performance/performance_demo.py

# 运行基础示例
python examples/basic/demo.py
```

### 构建和分发
```bash
# 构建包
python -m build

# 安装本地版本
pip install -e .
```

## 代码风格指南

### 格式化配置
- **行长度**: 100字符
- **格式化工具**: Black
- **导入排序**: isort (Black profile)
- **代码检查**: Ruff + MyPy

### 导入约定
```python
# 标准库导入优先
import sys
import time
from typing import List, Dict, Set, Any, Optional, Union

# 第三方库导入
from pypinyin import pinyin, Style

# 本地模块导入
from .pinyin_utils import text_to_tokens
from .engine import State, run_pinyin_regex
```

### 类型注解
- **必需**: 所有公共API函数必须有类型注解
- **推荐**: 内部函数也应该有类型注解
- **规范**: 使用typing模块的类型

```python
def pinyin_regex_match(
    pattern: str,
    text: str,
    use_initials: bool = True,
    use_fuzzy: bool = True,
    split_chars: bool = True,
) -> bool:
    """函数文档字符串"""
    # 实现
```

### 命名约定
- **变量/函数**: snake_case
- **类名**: PascalCase
- **常量**: UPPER_SNAKE_CASE
- **私有成员**: 前缀下划线

```python
class State:
    def __init__(self):
        self.eps: Set["State"] = set()  # epsilon转换
        self._private_var: str = "private"

INITIALS: List[str] = ["zh", "ch", "sh"]

def epsilon_closure(states: Set[State]) -> Set[State]:
    """计算epsilon闭包"""
    pass
```

### 文档字符串规范
使用Google风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """函数简短描述
    
    Args:
        param1: 参数描述
        param2: 参数描述
    
    Returns:
        返回值描述
    
    Examples:
        >>> function_name("test", 123)
        True
    """
    pass
```

### 错误处理
- 使用自定义异常类（定义在errors.py中）
- 异常类继承自PinyinRegexError
- 提供有意义的错误信息

```python
from .errors import PatternParseError

def compile_regex(pattern: str) -> State:
    if not pattern:
        raise PatternParseError("空模式字符串")
    # 实现
```

## 项目结构

```
pinyin_regex/
├── __init__.py          # 包API定义，导出公共接口
├── engine.py           # NFA引擎核心
├── parser.py           # 正则表达式解析器
├── pinyin_utils.py     # 拼音处理工具
├── debug.py            # 调试工具模块（新增）
└── errors.py           # 自定义异常类

examples/               # 示例和演示
├── README.md           # 示例目录说明
├── basic/              # 基础功能示例
│   └── demo.py         # 基础使用示例
├── debug/              # 调试工具示例
│   ├── debug_demo.py   # 调试功能完整演示
│   ├── debug_test.py   # 调试工具基础测试
│   └── test_graphviz.py # 图形化功能测试
└── performance/        # 性能分析示例
    └── performance_demo.py # 性能分析演示
```

## 测试约定

### 测试用例开发流程
为了确保测试质量，所有新的测试用例都需要经过以下流程：

1. **候选阶段**：在`candidates/`目录中创建测试用例
   - 使用简单格式：`pattern`、`text`、`result`
   - 使用注释和文件名明确测试目标
   - 文件命名格式：`test_功能名.py`

2. **人工审核**：由开发者确认测试用例的正确性
   - 验证pattern的逻辑正确性
   - 确认text的代表性
   - 检查result的准确性

3. **正式实现**：审核通过后在`tests/`目录生成测试代码
   - 转换为标准的unittest/pytest格式
   - 添加适当的断言和错误处理
   - 包含边界情况和异常测试

### 测试文件结构
- 测试文件以`test_`开头
- 测试类以`Test`开头
- 测试方法以`test_`开头

### 测试标记
```python
import pytest

@pytest.mark.slow
def test_slow_function():
    pass

@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_function():
    pass
```

### 测试组织
```python
class TestPinyinRegexBasic(unittest.TestCase):
    """基础拼音匹配功能测试"""
    
    def test_full_pinyin_match(self):
        """测试全拼匹配"""
        test_cases = [
            ("yinyue", "音乐", True),
            ("chongqing", "重庆", True),
        ]
        
        for pattern, text, expected in test_cases:
            with self.subTest(pattern=pattern, text=text):
                result = pinyin_regex_match(pattern, text)
                self.assertEqual(result, expected)
```

## 提交规范

### 分支命名
- `feature/功能名`
- `bugfix/问题描述`
- `hotfix/紧急修复`

### 提交信息格式
```
类型: 简短描述

详细描述（可选）

Closes #issue号
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 性能考虑

### 关键路径优化
- NFA状态转换使用集合操作
- 拼音转换结果缓存（如需要）
- 避免不必要的字符串操作

### 内存管理
- 及时释放大对象
- 使用生成器处理大数据集
- 避免循环引用

## 调试工具

### 调试模块功能

项目提供了完整的调试工具模块 `pinyin_regex.debug`，包含以下功能：

#### 1. NFA可视化
```python
from pinyin_regex.debug import dump_nfa, visualize_nfa

# 基础NFA结构打印
start_state = compile_regex("yinyue")
dump_nfa(start_state)

# 生成DOT图形文件
visualize_nfa(start_state, "nfa.dot")

# 如果安装了graphviz，可生成PNG/SVG
from pinyin_regex.debug import render_nfa_graph
render_nfa_graph(start_state, "nfa.png", "png")
```

#### 2. 调试运行
```python
from pinyin_regex.debug import debug_pattern

# 获取详细的匹配信息
debug_info = debug_pattern("yinyue", "音乐")
print(f"匹配结果: {debug_info['match_result']}")
print(f"步骤数: {debug_info['step_count']}")
print(f"统计信息: {debug_info['stats']}")
```

#### 3. 性能分析
```python
from pinyin_regex.debug import PerformanceProfiler

profiler = PerformanceProfiler()

# 测试编译性能
duration = profiler.profile_compilation("yinyue")

# 测试匹配性能
duration = profiler.profile_matching("yinyue", "音乐")

# 获取性能摘要
summary = profiler.get_summary()
```

#### 4. 交互式调试
```python
from pinyin_regex.debug import NFADebugger

debugger = NFADebugger(verbose=True)
# 调试运行会显示每一步的状态变化
```

### 可选依赖

调试工具的图形化功能需要安装 `graphviz`：

```bash
# 安装Python包
pip install graphviz

# 安装系统工具（Windows）
# 下载并安装 Graphviz: https://graphviz.org/download/

# 安装系统工具（macOS）
brew install graphviz

# 安装系统工具（Linux）
sudo apt-get install graphviz
```

### 调试演示

运行调试演示查看完整功能：

```bash
# 完整调试演示
python examples/debug/debug_demo.py

# 基础调试测试
python examples/debug/debug_test.py

# 图形化功能测试
python examples/debug/test_graphviz.py

# 性能分析演示
python examples/performance/performance_demo.py

# 基础功能示例
python examples/basic/demo.py
```

## 调试技巧

### 启用调试输出
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 单步调试
使用pytest的调试功能：
```bash
python -m pytest -s tests/test_engine.py::TestPinyinRegexBasic::test_full_pinyin_match
```

## 发布流程

1. 确保所有测试通过
2. 更新版本号（pyproject.toml）
3. 更新CHANGELOG.md
4. 运行完整测试套件
5. 创建Git标签
6. 构建并上传到PyPI

## 常见问题

### Q: 如何添加新的正则表达式特性？
A: 
1. 在parser.py中添加解析逻辑
2. 在engine.py中添加执行逻辑
3. 添加相应的测试用例
4. 更新文档

### Q: 如何处理新的拼音边缘情况？
A:
1. 在pinyin_utils.py中添加处理逻辑
2. 添加测试用例验证
3. 确保向后兼容性

### Q: 性能优化建议？
A:
1. 使用性能分析工具找出瓶颈
2. 优化NFA状态转换逻辑
3. 考虑使用缓存机制
4. 避免不必要的计算

## 开发工具推荐

- **IDE**: VS Code / PyCharm
- **插件**: Python, Black, isort, MyPy
- **调试**: pdb, pytest内置调试器
- **性能分析**: cProfile, line_profiler
- **文档**: Sphinx

## 联系方式

- 仓库: https://github.com/example/pinyin-regex
- 问题反馈: 创建GitHub Issue
- 文档: https://pinyin-regex.readthedocs.io/