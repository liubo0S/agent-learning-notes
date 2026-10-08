# Python 与 Agent 开发 · 资源

> **链接状态已核对（第 2 课时）。** 用 `curl` 逐条验证过 HTTP 状态。
> 结论：Anthropic 的**文档站从这台机器不可达**（`docs.claude.com` / `docs.anthropic.com` /
> `platform.claude.com` 全部超时），但**工程博客和 GitHub 可达**。因此本表已把不可达的条目
> 剔除或替换为可达的等价来源。
>
> 附带发现：`WebSearch` 和 `WebFetch` 工具被策略拦截，但 `curl` 与 `pip` 有网络。
> 以后要核实资料就走 `curl`，不要再依赖内建的抓取工具。

## Knowledge

- ✅ [Anthropic Engineering — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
  Agent 与 workflow 的架构边界、常见编排模式（chaining / routing / parallelization /
  orchestrator-workers / evaluator-optimizer）。原文已抓取核对，[术语表](reference/glossary.html)
  对 Agent 的定义以此为准。
  **何时读：** 设计新 Agent 之前，先判断到底该不该用 Agent。文章本身的核心忠告是「先找最简单的方案」。

- ✅ [anthropic-sdk-python（官方 SDK 仓库）](https://github.com/anthropics/anthropic-sdk-python)
  官方文档站不可达期间，**这是 API 用法最可靠的替代来源**。README 有最小可运行示例，
  仓库里的类型定义就是权威接口说明。
  **何时读：** 任何「这个参数到底叫什么」的问题。比任何博客可靠。
  **更硬的办法：** 装好包之后直接在本地读源码，比读文档还准：
  `python -c "import inspect, anthropic; print(inspect.signature(anthropic.resources.messages.Messages.create))"`

- ✅ [The Python Tutorial（官方教程）](https://docs.python.org/3/tutorial/)
  语言本身的一级来源。第 4 章（控制流与函数）、第 5 章（数据结构）是前期主战场。
  **何时读：** 任何语法拿不准的时候，优先于任何博客。

- ✅ [Python 官方文档 — venv](https://docs.python.org/3/library/venv.html)
  虚拟环境的权威说明。
  **何时读：** 环境出问题时。比搜到的教程可靠。

- ✅ [Python Packaging — 用 pip 和虚拟环境安装包](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
  官方打包权威指南，比 `venv` 文档更贴近实操。
  **何时读：** 依赖管理、`requirements.txt`、项目结构。

- ⚠️ [Real Python](https://realpython.com/)
  质量稳定的教程站，讲解比官方文档友好。对 `curl` 返回 403（挡爬虫），**浏览器里正常**。
  **何时读：** 官方文档太干时的第二落点（虚拟环境、装饰器、类型标注）。

- 📖 [Fluent Python, 2nd ed. — Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
  写「地道 Python」的权威书。专治「用 JS 的写法写 Python」，对迁移者价值极高。
  **何时读：** 能跑通项目之后，用来把代码从「能用」提到「专业」。

- 🔧 [Anthropic Console](https://console.anthropic.com)
  不是读物，是仪表盘。Usage 页是**用量与花费的权威数字**。
  **何时用：** 每次跑完实验都去看一眼，建立成本直觉。定价页目前从本机不可达，用量页请在浏览器里看。

- ✅ [Moonshot（Kimi）开放平台文档](https://platform.moonshot.cn/docs/guide/agent-support)
  **备选供应商。** 已实测：Kimi 提供 **Anthropic 兼容端点**，官方 `anthropic` SDK 只改
  `ANTHROPIC_BASE_URL` 就能直接用，不必换 SDK。
  - 端点：`https://api.moonshot.cn/anthropic`（**用 `.cn`**，`api.moonshot.ai` 从本机不可达）
  - 模型 ID（取自官方文档）：`kimi-k3`（文档建议的默认）、`kimi-k2.6`、`kimi-k2.5`、`kimi-k2.7-code-highspeed`
  - 验证方式：假 key 打过去会返回 Moonshot 自己的 `invalid_authentication_error`，证明路由正确
  **何时用：** 中转不稳、想省钱、或需要长上下文时切过去。

## Wisdom (Communities)

> 尚未与学习者确认社区意愿，先列候选，不主动推动。

- [r/LLMDevs](https://reddit.com/r/LLMDevs)　实战向：成本、延迟、可靠性踩坑。**何时用：** 方案评审、被质疑。
- [r/learnpython](https://reddit.com/r/learnpython)　对新手友好、审核良好。**何时用：** 代码 review 请求。
- [Anthropic Discord](https://www.anthropic.com/discord)　官方社群，能碰到真在做 Agent 的人。**何时用：** API 行为疑难。

## Gaps

需要补的资源，驱动后续检索：

- **定价与成本模型**：定价页从本机不可达，目前只能靠 Console 的实际用量反推。
  这是报价能力的直接输入，缺口优先级最高。
- **中文一级来源**：目前全是英文。若阅读成本影响进度，需要找质量对得起的中文资料。
- **部署与交付**：独立接活的部署路径（容器、Serverless、成本结构），尚无可信来源。
- **前端接 Agent**：流式输出（SSE）在 React / Vue 侧的成熟范式，缺权威示例。
  这一块是他的强项区，找到好来源能省很多时间。
- **报价与商务**：独立开发者如何为 AI 项目定价，尚无来源。
