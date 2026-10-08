"""
第 2 课 · 第一次真的调用 Claude
配套课程： lessons/0002-first-real-call.html

运行前提（课程里有详细步骤）：
  1. 已激活虚拟环境      → 提示符前面出现 (.venv)
  2. 已装好 SDK          → pip install anthropic
  3. 已配好供应商        → 先跑 python3 exercises/00_check_env.py 确认

运行： python3 exercises/02_first_call.py

这个文件会真的发出 3 次请求，花掉的钱远不到一分。
"""

import os

import anthropic

# 模型名从环境变量来，方便换供应商。练手一律用便宜的一档。
#   Anthropic 官方 / 兼容中转 → claude-haiku-4-5
#   Kimi                      → kimi-k3
# 挑模型是成本控制的第一道闸门。
MODEL = os.environ.get("LESSON_MODEL") or "claude-haiku-4-5"

# 启动就检查，比让 SDK 在半路抛一长串栈要友好得多
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("没找到 ANTHROPIC_API_KEY。先跑 exercises/00_check_env.py 排查。")

# 不传参数，SDK 默认读 ANTHROPIC_API_KEY 和 ANTHROPIC_BASE_URL 两个环境变量。
# 所以换供应商不需要改这里的任何一行代码。
client = anthropic.Anthropic()


def ask(messages):
    """发一次请求。返回 (回复文本, (输入 token, 输出 token))。"""

    # TODO 1 ── 真的把请求发出去。三个必填参数：
    #   resp = client.messages.create(
    #       model=MODEL,
    #       max_tokens=800,
    #       messages=messages,
    #   )
    #   （给 800 而不是 300：思考型模型的 thinking 也算输出 token，
    #     给太小会在产出正式文本前就被截断。）
    resp = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=messages,
    )

    if resp is None:
        raise SystemExit("TODO 1 还没完成：ask() 里没有真的发出请求。")

    # TODO 2 ── 取出文本。
    #   resp.content 是一个「内容块」的列表，块有好几种类型：
    #     text      普通文字      → 有 .text
    #     thinking  思考过程      → 有 .thinking，**没有 .text**
    #     tool_use  工具调用请求  → 有 .name / .input
    #
    #   所以不能写 resp.content[0].text：思考型模型会把 thinking 块放在最前面，
    #   那样会直接报 AttributeError。要按类型筛出文本块再拼起来：
    #
    #     text = "".join(b.text for b in resp.content if b.type == "text")
    #
    #   TS 类比：
    #     content.filter(b => b.type === "text").map(b => b.text).join("")
    text = "".join(b.text for b in resp.content if b.type == "text")

    # TODO 3 ── 取出用量。resp.usage 上有 input_tokens 和 output_tokens。
    used = (resp.usage.input_tokens, resp.usage.output_tokens)

    return text, used


# ==========================================================
# 实验 A · 一次普通的调用
# ==========================================================

q1 = "用一句话说明 Python 里 list 和 tuple 的区别。"
a1, u1 = ask([{"role": "user", "content": q1}])

print("── A 普通调用 ──")
print("问:", q1)
print("答:", a1)
print(f"   用量  输入={u1[0]}  输出={u1[1]}\n")


# ==========================================================
# 实验 B · 不带历史，问一个依赖上文的问题
# 这里不用你动手，跑一下，看它是不是完全听不懂。
# ==========================================================

q2 = "那前者的常见用途是什么？"
a2, u2 = ask([{"role": "user", "content": q2}])

print("── B 不带历史 ──")
print("问:", q2)
print("答:", a2)
print(f"   用量  输入={u2[0]}  输出={u2[1]}   ← 输入很少\n")


# ==========================================================
# 实验 C · 把历史补全，问同一个问题
# ==========================================================

a3, u3 = ask(
    [
        {"role": "user", "content": q1},
        {"role": "assistant", "content": a1},
        {"role": "user", "content": q2},
    ]
)

print("── C 带上历史 ──")
print("问:", q2, "（同一个问题）")
print("答:", a3)
print(f"   用量  输入={u3[0]}  输出={u3[1]}   ← 输入明显变多\n")


# ==========================================================
# 自动对照：这就是今天要带走的结论
# ==========================================================

if u2[0] and u3[0]:
    print("=" * 52)
    print(f"同一个问题，带历史时的输入 token 是不带时的 {u3[0] / u2[0]:.1f} 倍。")
    print("模型没有记忆。每一轮你都要把全部历史重新发一遍，")
    print("所以对话越长，每一轮就越贵。这是报价时必须算进去的东西。")
    print("=" * 52)
else:
    print("（TODO 3 还没完成，所以看不到用量对比）")
