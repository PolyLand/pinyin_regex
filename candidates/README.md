# 测试用例候选目录

本目录用于存放待审核的测试用例，格式简单明确。

## 测试用例格式

每个文件包含测试用例，格式如下：
```python
# 测试目标：多规则组合测试
# pattern: "yin(yue|le){2}"
# text: "音乐了"
# result: True

# 测试目标：边界匹配测试  
# pattern: "^yin(yue|le)$"
# text: "音乐"
# result: True
```

## 审核流程
1. 在此目录创建测试用例文件
2. 人工确认pattern、text、result的正确性
3. 确认后生成正式的测试代码到tests/目录