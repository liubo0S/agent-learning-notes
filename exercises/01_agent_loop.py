"""
第 1 课 · Agent 的心脏是一个 while 循环
配套课程： lessons/0001-agent-loop.html

这个文件不联网、不需要 API key、不需要装任何依赖。
模型是假的，因为今天要学的不是「怎么调 API」，而是 Agent 的骨架。

运行： python3 exercises/01_agent_loop.py
"""

# ==========================================================
# 第 1 层 · 工具：Agent 真正能做的事
# 就是普通 Python 函数，没有任何魔法。
# ==========================================================


def get_weather(city):
    """假装查了天气。真实版本这里会发一个 HTTP 请求。"""
    return f"{city}今天晴，26 度"


def add(a, b):
    return a + b


# TODO 1 ── 把上面两个函数注册进这张表。
#   键是模型会说出的工具名（字符串），值是函数本身（不要加括号）。
#   TS 类比： const TOOLS = { get_weather, add }
TOOLS = {
    "get_weather": get_weather,
    "add": add,
}


# ==========================================================
# 第 2 层 · 假模型
# 真实模型读完整个对话历史，再决定下一步做什么。
# 这里把「下一步」按调用顺序写死了，好让你专注在循环上。
# ==========================================================

FAKE_RESPONSES = [
    {"type": "tool_use", "name": "get_weather", "args": {"city": "杭州"}},
    {"type": "tool_use", "name": "add", "args": {"a": 26, "b": 4}},
    {"type": "text", "text": "杭州今天晴，26 度；再加 4 度是 30 度。"},
]


def fake_model(history):
    if len(history) >= len(FAKE_RESPONSES):
        raise RuntimeError("模型被调用的次数超过预设：你的循环大概忘了 break")
    return FAKE_RESPONSES[len(history)]


# ==========================================================
# 第 3 层 · Agent 循环 ← 今天的主角
# ==========================================================


def run_agent():
    history = []

    while True:
        step = fake_model(history)

        # TODO 2 ── 如果模型说完了（step["type"] 等于 "text"）：
        #   打印  print("[回答]", step["text"])  然后 break 跳出循环。

        if step["type"] == "text":
            print("[回答]", step["text"])
            break

        # TODO 3 ── 否则模型想调工具，四步：
        #   a. 取出函数    fn = TOOLS[step["name"]]
        #   b. 带参数调用  result = fn(**step["args"])
        #      （** 就是 TS 的展开运算符，把 dict 展开成命名参数）
        #   c. 打印结果    print("[工具]", step["name"], "->", result)
        #   d. 记进历史    history.append(result)
        #      少了这一步，循环永远不会前进。

        fn = TOOLS[step["name"]]
        result = fn(**step["args"])
        print("[工具]", step["name"], "->", result)

        history.append(result)

        # raise SystemExit("请先完成 TODO 2 和 TODO 3，然后删掉这一行")


run_agent()
