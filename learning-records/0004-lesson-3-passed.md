# 第 3 课通过：工具调用打通，一次真实笔误恰好撞上课程强调的坑

学习者独立完成了 `exercises/03_real_tool_loop.py` 的四处 TODO，TODO 1（`ADD_SCHEMA`）、TODO 2（筛 `tool_use` 块）、TODO 3（assistant 内容回填）**一次写对**，包括本课头号错误点 TODO 3。

## 卡点与修复

跑起来后 `tool_result` 报 400，配对不上对应的 `tool_use`。检查后发现 TODO 4 里把字段名 `tool_use_id` 打成了 `tool_user_id`（多了个 `r`）。逻辑和结构完全正确，纯粹是拼写。指出具体行号后他自己去改，没有直接要答案。

**教学含义**：这类"字段名一个字母之差"的笔误，正是 [[reference/tool-use-protocol.html]] 里反复强调"方向不对称、字段名不对称"要提防的那类问题。他撞上的不是没学会,而是打字失误,不需要为此调整教学内容,但可以作为回考素材:"tool_use_id 和 tool_use 的 .id 是什么关系"。

## Evidence

- TODO 1/2/3 首次提交即正确，说明第 1、2 课的循环骨架和"按类型筛"心智已经稳固迁移到工具调用场景。
- 三个测试问题全部跑通，包括第三个强制两轮工具调用的问题（先查天气再加 7 度）。

## Implications

- 可以进入第 4 课（工具报错处理 + 危险操作确认）。前置技能齐备：工具声明、`tool_use`/`tool_result` 往返、`stop_reason` 判断。
- 术语表已收录本课新术语：工具声明、`tool_use` 块、`tool_result` 块、`tool_use_id`、`stop_reason`。
- 回考素材新增一项：字段名 `tool_use_id` 的由来（配对用的是 `.id`，字段名却不叫 `id`）。
