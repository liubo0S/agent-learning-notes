"""
第 3 课 · 让真模型自己决定调哪个工具
配套课程： lessons/0003-real-tool-loop.html

这一课把前两课接起来：
    第 1 课的循环骨架  +  第 2 课的真实调用  =  一个真正的 Agent

运行前先跑： python3 exercises/00_check_env.py
运行：       python3 exercises/03_real_tool_loop.py
"""

import os

import anthropic

MODEL = os.environ.get("LESSON_MODEL") or "claude-haiku-4-5"

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("没找到 ANTHROPIC_API_KEY。先跑 exercises/00_check_env.py 排查。")

client = anthropic.Anthropic()


# ==========================================================
# 第 1 层 · 工具的实现
# 和第 1 课一模一样，就是普通函数。这一层没有任何变化。
# ==========================================================


def get_weather(city):
    return f"{city}今天晴，26 度"


def add(a, b):
    return a + b


TOOLS = {
    "get_weather": get_weather,
    "add": add,
}


# ==========================================================
# 第 2 层 · 工具的声明  ← 今天的新东西
#
# 模型看不到你的 Python 代码，它只能看到这份声明。
# 关键认知：description 不是注释，它是提示词的一部分。
# 模型完全靠它来判断「现在该不该用这个工具」。
# 声明写得含糊，模型就选错工具，而这不是代码 bug，是提示词问题。
# ==========================================================

WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": "查询某个城市当前的天气。当用户问到天气、气温、冷热时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名，例如「杭州」"},
        },
        "required": ["city"],
    },
}

# TODO 1 ── 照上面的样子，给 add 写一份声明。
#   · name 必须和 TOOLS 里的键完全一致，否则查表会 KeyError
#   · a 和 b 都是数字，JSON Schema 里的类型名写 "number"
#   · description 要写清楚「什么时候该用它」，这比写「它做什么」有用得多
ADD_SCHEMA = {
    "name": "add",
    "description": "两数相加算总和。当用户问到加法、总和时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "a": {"type":"number", "description": "一个数字，例如「999」"},
            "b": {"type":"number", "description": "一个数字，例如「123」"},
        },
        "required":["a","b"],
    }
}

TOOL_SCHEMAS = [WEATHER_SCHEMA, ADD_SCHEMA]


# ==========================================================
# 第 3 层 · Agent 循环
# 和第 1 课同一个形状。唯一的变化：fake_model 换成了真的 Claude。
# ==========================================================


def run_agent(question, max_turns=6):
    messages = [{"role": "user", "content": question}]

    # 轮数硬上限。第 1 课考过：这是除「模型说完了」之外的第二个出口。
    # 少了它，模型一旦卡在「反复调同一个工具」，就会一直烧钱。
    for turn in range(1, max_turns + 1):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        print(f"\n  ── 第 {turn} 轮 ──")
        print("     stop_reason:", resp.stop_reason)
        print("     块          :", [b.type for b in resp.content])
        print(f"     输入 token  : {resp.usage.input_tokens}")

        # ── 出口一：模型不再要求调工具，说明它要给最终答案了 ──
        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            print("\n  [最终回答]", text.strip())
            print(f"  （共 {turn} 轮）")
            return

        # TODO 2 ── 筛出这一轮所有的 tool_use 块。
        #   和第 2 课筛 text 块是同一个写法，只把类型换成 "tool_use"：
        #     calls = [b for b in resp.content if b.type == "tool_use"]
        calls = [b for b in resp.content if b.type == "tool_use"]

        if not calls:
            raise SystemExit("TODO 2 还没完成：没筛出 tool_use 块。")

        # TODO 3 ── 把模型这一轮的完整回复原样放回 messages。
        #   ⚠️ 这一步最容易漏。漏了模型就「不记得」自己刚才要求调什么工具，
        #      服务端会直接报 400，说 tool_result 找不到对应的 tool_use。
        #   注意是 resp.content 整个列表，不要只放 tool_use 块。
        #     messages.append({"role": "assistant", "content": resp.content})

        messages.append({"role": "assistant", "content": resp.content })

        # TODO 4 ── 执行每个工具，把结果拼成 tool_result 块。
        results = []
        for call in calls:
            fn = TOOLS[call.name]
            output = fn(**call.input)
            print(f"     [执行] {call.name}({call.input}) -> {output}")

            #   每个 tool_result 必须带 tool_use_id，靠它和请求配对。
            #   content 要求字符串，所以数字结果要 str() 一下。
            #     results.append(
            #         {
            #             "type": "tool_result",
            #             "tool_use_id": call.id,
            #             "content": str(output),
            #         }
            #     )
            results.append(
                {
                    "type":"tool_result",
                    "tool_use_id":call.id,
                    "content":str(output),
                }
            )

        if not results:
            raise SystemExit("TODO 4 还没完成：没构造出 tool_result。")

        # 工具结果用 role="user" 发回去。这点反直觉，但想想就通了：
        # 结果不是模型说的话，所以不能算 assistant。
        messages.append({"role": "user", "content": results})

    # ── 出口二：轮数用光，强制停止 ──
    print(f"\n  ⚠️ 到了 {max_turns} 轮上限还没收手，强制停止。")


# ==========================================================
# 试三个问题。
# 注意第三个：它需要模型先查天气，再拿查到的温度去调 add。
# 那是真正的多轮工具调用，也是 Agent 和「一次函数调用」的分界线。
# ==========================================================

QUESTIONS = [
    "杭州今天天气怎么样？",
    "3847 加 2915 等于多少？",
    "杭州今天几度？在那个温度上再加 7 度是多少？",
]

for q in QUESTIONS:
    print("\n" + "=" * 58)
    print("问题:", q)
    print("=" * 58)
    run_agent(q)
