# 教学笔记（工作用）

## 学习者画像

- 前端出身：TypeScript + React / Vue，用过 Node。工程概念齐备（模块、异步、类型、包管理）
- Python 起步阶段，但**第 1 课已通过**（独立写出 Agent 循环，见 `learning-records/0002`）
- 每天在用 Claude Code / Cursor，对 Agent 的**行为**有直觉，缺的是**内部机制**
- **有 Anthropic API key,但属于第三方中转**,因此必须同时配 `ANTHROPIC_BASE_URL`。
  他自己提出了这一点(而我原先误以为是官方 key),说明他对配置类问题有敏感度,不是被动跟做
- 终点是独立接活交付,所以偏好「能留下来的代码」而不是抛弃式练习

## 教学策略

1. **一切用 TS 做锚点。** 已被验证有效：`**` 展开靠一句「等于 TS 的展开运算符」就用对了。继续沿用。
2. **每节课 20–30 分钟，一个可运行产物。** 不做纯理论课。
3. **摩擦按需引入。** 第 1 课刻意用假模型避开环境配置；第 2 课才引入 venv，因为此时它是真需要。
4. **储存强度优先。** 每节课测验都是回忆式（等长选项、`quiz.js` 打乱顺序），并**刻意回考前几课**。
   第 2 课已回考第 1 课两题（轮数上限、空列表假值）。这个做法要保持。
5. **风格问题交给工具，不占教学预算。** 见下方「习惯」。
6. **术语一律对齐 `reference/glossary.html`**，且该表只收录已确认掌握的术语。

## 环境事实（已实测）

- `python3` = **3.13.14**
- `anthropic` SDK **0.121.0** 可正常安装
- `client.messages.create` 必填参数：`model` / `max_tokens` / `messages`（已用假 key 打到 401 验证过调用形状）
- 默认读取的环境变量是 `ANTHROPIC_API_KEY`，**以及 `ANTHROPIC_BASE_URL`**（源码里确认）。
  因此换供应商不需要改任何 Python 代码，这已被写成第 2 课的一个教学点
- **Kimi 可作备选供应商**：`https://api.moonshot.cn/anthropic` 是 Anthropic 兼容端点，
  官方 SDK 直接可用（假 key 打过去返回 Moonshot 自己的 `invalid_authentication_error`，路由确认）。
  模型 `kimi-k3` 等。注意用 `.cn`，`.ai` 域名从本机不可达
- 练习脚本统一用 `LESSON_MODEL` 环境变量指定模型，默认 `claude-haiku-4-5`
- **他实际选用的是 Kimi**：`base_url=https://api.moonshot.cn/anthropic`、`LESSON_MODEL=kimi-k3`，已连通
- **`kimi-k3` 是思考型模型**，`resp.content` 的第一个块是 `thinking` 而非 `text`。
  内容块类型与取值（已从 SDK 类型定义确认）：
  | 类 | `type` | 内容属性 |
  |---|---|---|
  | `TextBlock` | `"text"` | `.text` |
  | `ThinkingBlock` | `"thinking"` | `.thinking`（**无 `.text`**） |
  | `ToolUseBlock` | `"tool_use"` | `.name` / `.input` |
  | `RedactedThinkingBlock` | `"redacted_thinking"` | `.data` |
  **因此教材一律用 `"".join(b.text for b in resp.content if b.type == "text")`，
  禁止出现 `content[0].text` 这种写法。**
- **`max_tokens` 对思考型模型要给够**（≥512）。thinking 也算输出 token，给小了会在产出文本前就截断
- **`exercises/00_check_env.py` 是环境自检脚本**，后续每节课遇到配置问题都先让他跑这个。
  它会打印 `[b.type for b in resp.content]`，正好把「内容块是列表」这件事可视化
- 有效模型 ID（从 SDK 类型定义中读出）：`claude-haiku-4-5`、`claude-sonnet-5`、`claude-opus-5` 等
- **网络：`curl` 和 `pip` 可用；`WebSearch` / `WebFetch` 被拦。核实资料一律走 `curl`。**
- Anthropic 文档站（`docs.claude.com` / `platform.claude.com`）从本机不可达；
  **用官方 SDK 仓库 + 本地 `inspect` 源码替代**，这条路更准

## 习惯（非知识缺口，不要当成错误教）

- `if(cond):` 条件外加括号，`hello.py` 和第 1 课都有，是稳定的 JS 肌肉记忆
- 逗号前留空格、单双引号混用

**处理方式：** 第 2 课引入 `ruff format`（Prettier + ESLint 的对应物），用工具纠正而非讲规则。
**待确认：** 他是否真的跑了 `ruff`、风格是否随之改变。第 3 课开始前检查一次。

## 待办 / 观察点

- [x] ~~第 3 课前检查 `02_first_call.py` 与 `ruff` 是否见效~~ → **均已确认**。
      三处 TODO 全对且 TODO 2 用的是健壮版按类型筛；`ruff format` 已实际使用，
      `if(cond):` 的 JS 括号习惯在新代码中消失
- [x] ~~第 4 课前检查 `03_real_tool_loop.py` 的四处 TODO~~ → **均已确认**。
      TODO 1/2/3 一次写对（含头号错误点 TODO 3）；TODO 4 有个字段名笔误
      `tool_use_id` 打成 `tool_user_id`，指出行号后他自己修好，不是没学会
- [x] ~~第 5 课前检查 `04_resilient_loop.py` 的三处 TODO~~ → **均已确认**。
      TODO 1/3 一次写对；TODO 2 逻辑正确，留了一行无害的占位符 `...` 没删干净，
      不影响运行。观察点记在 `learning-records/0005`，暂不作为回考素材
- [ ] 尚未询问社区偏好（是否愿意进论坛 / 社群）。他已经开始提架构性问题
      （「第三方 key 要不要配 url」），时机接近成熟
- [ ] 成本直觉：第 2 课的 token 对比已跑过，第 3 课的多轮循环会让他看到递增。
      **仍缺定价数据**（见 `RESOURCES.md` 的 Gaps），这是报价能力的直接输入
- [ ] 可变默认参数、`is` vs `==` 两个经典坑尚未触发，继续留作回考素材
- [ ] 他前端强项（React/Vue + SSE 流式）迟早要接进来，那节课体感最好，留作动力储备
- [ ] **第 6 课前检查**：`05_trim_and_log.py` 的三处 TODO。重点看他是否理解
      "裁剪单位是一对不是一条"，以及裁剪后模型回答信息缺失那个现象有没有引起他的注意
- [ ] **观察点**：写完代码不回读一遍的习惯（第 4 课那个残留 `...`）。目前只出现一次，
      不足以下结论，如果再出现，可以提一句"提交前扫一遍 diff"，对应他日后过 code review 的场景

## 第 3 课已埋下的后续线索

课程末尾留了四个「先想，别写」的问题，就是第 4、5 课的内容，也是「demo → 可交付」的差距：
工具抛异常、幻觉工具名、上下文超限、危险操作的人工确认。全部处理完毕。

## 第 4 课的设计与结果

第 4 课处理了四个问题里的两个：工具报错（`is_error`）、危险操作确认（`input()` 问人）。
「幻觉工具名」顺带被同一个 `try/except` 解决，不需要单独教。剩下两个（上下文超限、
日志监控）交给第 5 课。

## 第 5 课的设计与结果

第 5 课处理剩下两个问题：历史裁剪（`trim_history`，强调"单位是一对不是一条"）、
结构化日志（`log()`，`print` 换 JSON，去处变心智不变）。故意把 `MAX_HISTORY_MESSAGES`
设得很小（3），让裁剪在几轮工具调用内就能被亲眼看到，也刻意让"裁剪丢信息"这个副作用
在第二个测试问题（三次连续工具调用）里真实发生，作为"裁剪不是免费午餐"的活教材。
下一课方向：接上 HTTP + SSE，对齐他的前端强项，是 `MISSION.md` 里"接上自己的前端"这条的落地。
