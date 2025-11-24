#import "@preview/grape-suite:3.1.0": exercise
#import exercise: project, subtask, task
#set text(lang: "zh",font: "Microsoft JhengHei UI")

#show: project.with(
  title: "自动化录题工具项目报告",
  show-outline: true,
  author: "王浩然",
  show-solutions: false,
)
#pagebreak()
= 项目概述 (Executive Summary)
#image("image.png")
+ *目标:* 开发一个全自动工具，从“组卷网”抓取试卷，利用AI分析并自动录入到题库系统。
+ *核心创新:* 通过异步并发技术实现多任务并行处理，并集成大语言模型（LLM）自动分析试卷是否录入错误。
#image("image-3.png")
+ *主要成果:* 极大提升了录题效率，降低了人工成本和错误率。

#image("image-1.png")
#image("image-2.png")
= 背景与痛点 (Problem Statement)

== 传统流程

传统的试题录入工作需要以下步骤：

1. *手动浏览*：工作人员逐个访问组卷网试卷页面
2. *复制粘贴*：手动选择、复制题干和选项内容
+ *答案核对*：人工分析题目，确定正确题目
+ *重复检查*：核对录入内容，修正错误
+ *提交保存*：完成单题录入，继续下一题

每份试卷通常包含20-50道题目，整个流程耗时较长且容易出错。

== 存在问题

- *效率低下:* 人工复制、粘贴非常耗时。
- *成本高昂:* 需要投入大量人力和时间，尤其是在高峰期。
- *重复性劳动:* 工作枯燥，价值感低。

= 解决方案与技术架构 (Solution & Architecture)

== 整体设计

本项目采用基于Python asyncio的异步并发架构，实现了从试卷抓取到自动录入的端到端工作流。整个系统由以下核心组件协同工作：

=== 系统架构

系统采用多进程+异步IO的设计模式，主要包含以下模块：

1. *配置管理模块 (`model.py`)*：
   - 定义数据结构（`questionData`、`question_page`、`muti_thread_config`）
   - 管理多线程配置，支持最多无限多个并发端口(2001\...),默认支持10个端口(2001-2010)
   - 自动从组卷网目录页获取试卷列表

2. *浏览器连接模块 (`connect_browser.py`)*：
   - 为每个任务分配独立的浏览器实例和端口
   - 支持Playwright异步浏览器操作
   - 实现浏览器实例复用和资源管理

3. *页面下载与解析模块 (`download_page.py`)*：
   - 使用BeautifulSoup解析HTML结构
   - 提取试卷基本信息（省份、年级、学科、年份）
   - 批量解析试题内容，生成结构化数据
   - 自动生成 PDF 文件

4. *AI分析模块 (`ask_llm.py`, `ask_llm_chatgpt.py`)*：
   - 集成大语言模型进行试题分析
   - 自动识别选择题答案
   - 检测重复题目，避免重复录入
   - 支持多种LLM接口（ChatGPT、自定义模型）

5. *自动化录入模块 (`add_question.py`, `add_and_click_tianjia.py`)*：
   - 模拟用户操作，自动填写表单
   - 监听网络请求，获取系统反馈
   - 处理录入过程中的异常情况

=== 工作流程

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  获取试卷     │───▶│   并发处理    │───▶│   结果汇总    │
│   列表       │    │   (最多10个)  │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
       │                   │                 │
       ▼                   ▼                 ▼
 组卷网目录页        多浏览器实例        处理完成通知
```

具体执行步骤：

1. *初始化阶段*：
   ```python
   config = await muti_thread_config.create(
       ports=[2001, 2002, ..., 2010],
       zujvanwang_catalogue_url="组卷网目录页"
   )
   ```

2. *任务分配*：
   - 获取有效试卷列表：`valid_papers = [paper for paper in config.zujvanwang_papers if paper.get('url')]`
   - 创建并发任务：每个端口处理一份试卷
   - 任务数量 = `min(端口数, 试卷数)`

3. *并发执行*：
   ```python
   await asyncio.gather(*tasks)  # 同时启动所有core任务
   ```

4. *单任务流程*（`core`函数）：
   - 浏览器连接 → 页面下载 → 预处理 → 试题解析 → AI分析 → 自动录入

=== 数据流转

```
组卷网HTML ──解析──▶ questionData对象 ──AI分析──▶ 标准答案
     │                    │                      │
     ▼                    ▼                      ▼
PDF自动上传原卷        JSON结构化数据            自动录入系统
```

数据在各模块间采用标准化的数据结构传递，确保了系统的可维护性和扩展性。

== 技术亮点

=== 高并发处理架构

本项目采用基于 `asyncio` 的异步并发架构，实现了真正的多任务并行处理：

- *多端口浏览器实例*：通过端口2001-2010启动最多10个独立浏览器进程，每个进程处理一份试卷
- *任务动态分配*：`num_tasks = min(len(config.ports), len(valid_papers))`，智能匹配可用资源和任务数量
- *异步任务调度*：使用 `asyncio.gather(*tasks)` 实现真正的并发执行，而非串行处理
- *资源隔离管理*：每个任务拥有独立的浏览器实例和端口，避免进程间干扰

```python
# 核心并发逻辑
for i in range(num_tasks):
    port = config.ports[i]
    paper_info = valid_papers[i]
    task = core(target_url=paper_info['url'], 
               target_title=paper_info['title'], 
               port=port)
    tasks.append(task)
await asyncio.gather(*tasks)  # 并发执行所有任务
```

=== AI智能分析与质量控制

AI分析模块是本项目的核心创新，不仅识别答案，更重要的是进行质量控制：

- *智能题目校对*：通过对比试题来源(`origin`)与题库现有数据(`origin_from_our_bank`)，自动检测可能的重复或错误录入
- *精确错误定位*：AI能够识别出"新题被误标为旧题"或"旧题被误标为新题"的问题
- *结构化错误报告*：生成包含错误原因、题目内容、来源对比的详细JSON报告
- *多LLM接口支持*：支持ChatGPT和自定义xchatbot等多种AI模型

```python
# AI校对核心逻辑示例
prompt = f"""
I want you to act as an expert in proofreading exam questions.
Compare 'origin' with 'origin_from_our_bank' to detect potential errors.
A potential error exists if the 'origin_from_our_bank' does not contain 
a source that is the same as or very similar to the 'origin'.
"""
```

*质量控制工作流*：
1. 解析试题结构化数据
2. 对比题目来源与题库现有记录
3. 识别潜在的重复或标记错误
4. 生成错误报告并保存到 `other/LLM_output/` 目录
5. 为可疑题目提供人工复核建议

=== 模块化设计架构

系统采用松耦合的模块化设计，每个模块职责单一且可独立测试：

- *配置管理层*(`model.py`)：数据结构定义与多线程配置管理
- *网络通信层*(`connect_browser.py`)：浏览器连接与会话管理  
- *数据采集层*(`download_page.py`)：HTML解析与结构化数据提取
- *AI分析层*(`ask_llm.py`, `ask_llm_chatgpt.py`)：智能分析与质量控制
- *业务逻辑层*(`core.py`)：工作流编排与异常处理
- *自动化操作层*(`add_question.py`, `add_and_click_tianjia.py`)：UI自动化与表单填写

*设计优势*：
- 单一职责原则：每个模块专注一项功能
- 接口标准化：模块间通过标准数据结构通信
- 易于维护：可独立修改某个模块而不影响其他部分
- 便于扩展：添加新功能只需实现对应接口

=== 端到端自动化流程

实现了从数据获取到最终录入的全流程无人干预：

- *智能试卷发现*：自动访问组卷网目录页，提取所有试卷链接和标题
- *并行数据采集*：同时处理多份试卷，自动解析题目内容和元数据
- *AI质量把控*：自动检测重复题目和潜在错误，生成质量报告
- *智能重复检测*：通过API检查题目是否已存在于目标系统
- *自动化录入*：模拟用户操作完成表单填写和提交
- *异常处理*：自动处理网络错误、解析失败等异常情况

*关键创新点*：
- 重复检测：`check_paper_exists()` 函数通过API预检查，避免重复工作
- 数据备份：自动生成PDF备份和JSON结构化数据
- 错误恢复：支持从中断点继续执行，不会丢失已处理数据
- 日志记录：详细记录处理过程，便于问题排查和性能优化

= 项目成果与业务价值 (Results & Business Impact)

== 量化指标

- *效率提升:* 
  - 手动录入：平均每份试卷需要10分钟（包含30-40道题目）
  - 自动化工具：平均 10 份试卷仅需5分钟（并发处理10份试卷同时进行，还可以并行处理更多的试卷）
  - *效率提升倍数：5-10+倍*
  - 支持最多10+个并发任务，理论上可同时处理10份试卷

- *准确率:* 
  - 重复题目检测：自动识别已存在题目，避免重复录入
  - 存疑题目标记：对于AI无法确定的题目，系统会自动标记为存疑，供人工复核，把题目数据放在 `.other/LLM_output/` 目录下
  - 格式标准化：确保所有录入数据格式统一，无人为格式错误
  - 数据完整性：自动提取试卷元信息（省份、年级、学科、年份）

- *可扩展性:* 
  - 多学科支持：当前支持科学，语文学科，可轻松扩展到语文、数学、英语等其他学科
  - 多网站适配：模块化设计便于适配其他题库网站（如菁优网、学科网等）
  - 并发能力：支持1-10个并发任务，可根据服务器性能调整
  - AI模型升级：支持接入不同的大语言模型（GPT、Claude、国产模型等）

=  未来展望 (Future Work)

- 在识别城市时，使用更为快速的方法提升效率。
- 加入错误更多处理
- 加入对变式题目录入的支持
- 与 rust 结合提升性能
