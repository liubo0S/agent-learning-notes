"""
第 5 课 · 历史裁剪与结构化日志
配套课程： lessons/0005-trim-and-log.html

第 4 课处理了"工具报错""危险操作确认"。这一课处理第 3 课末尾剩下的两个问题：
    · 历史涨到超过上下文窗口怎么办 → 裁剪（trim_history）
    · 循环里怎么插日志而不把代码写乱 → 结构化日志（log()）

运行前先跑： python3 exercises/00_check_env.py
运行：       python3 exercises/05_trim_and_log.py
"""

import json
import os

import anthropic

MODEL = os.environ.get("LESSON_MODEL") or "claude-haiku-4-5"

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("没找到 ANTHROPIC_API_KEY。先跑 exercises/00_check_env.py 排查。")

client = anthropic.Anthropic()


# ==========================================================
# 结构化日志
#
# print() 能看，但没法喂给日志系统（ELK、CloudWatch、随便哪个）。
# 换成"一行一个 JSON"，格式不变，去处变了：以后接真实项目时，
# 把这一行的 print 换成你的日志库调用，代码结构完全不用动。
# ==========================================================


def log(event, **fields):
    print(json.dumps({"event": event, **fields}, ensure_ascii=False))


# ==========================================================
# 第 1 层 · 工具的实现（和第 4 课一样，不再是新知识）
# ==========================================================


def get_weather(city):
    return f"{city}今天晴，26 度"


def add(a, b):
    return a + b


def divide(a, b):
    return a / b


TOOLS = {
    "get_weather": get_weather,
    "add": add,
    "divide": divide,
}


# ==========================================================
# 第 2 层 · 工具的声明（和第 4 课一样）
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

ADD_SCHEMA = {
    "name": "add",
    "description": "计算两个数字相加。需要做加法运算时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "第一个加数"},
            "b": {"type": "number", "description": "第二个加数"},
        },
        "required": ["a", "b"],
    },
}

DIVIDE_SCHEMA = {
    "name": "divide",
    "description": "计算两个数字相除。需要做除法运算时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "被除数"},
            "b": {"type": "number", "description": "除数"},
        },
        "required": ["a", "b"],
    },
}

TOOL_SCHEMAS = [WEATHER_SCHEMA, ADD_SCHEMA, DIVIDE_SCHEMA]


# ==========================================================
# 历史裁剪
#
# 心智模型：messages[0] 是最初的问题，永远保留。
# 后面的每一"轮"是 (assistant, user) 一对，assistant 那条带 tool_use，
# user 那条带对应的 tool_result。这两条必须一起留下或一起砍掉，
# 砍掉半对会导致 tool_result 找不到配对的 tool_use，直接 400。
#
# 所以裁剪单位是"一对"，不是"一条"。
# ==========================================================


def trim_history(messages, limit):
    # TODO 1 ── 如果 messages 已经不超过 limit，原样返回。
    #   否则：保留 messages[0]（最初的问题），
    #   从 messages[1:] 开始，每次砍掉最早的一对（两条），
    #   直到总长度不超过 limit，或者已经没有整对可砍了。
    #
    #   head = messages[:1]
    #   body = messages[1:]
    #   while len(head) + len(body) > limit and len(body) >= 2:
    #       body = body[2:]
    #   return head + body
    ...  # 替换成完整实现


MAX_HISTORY_MESSAGES = 3  # 故意设得很小，让你在几轮之内就能亲眼看到裁剪发生


# ==========================================================
# 第 3 层 · Agent 循环
# 骨架和第 4 课一样，多了两处：调用前裁剪、关键节点打结构化日志。
# ==========================================================


def run_agent(question, max_turns=6):
    messages = [{"role": "user", "content": question}]

    for turn in range(1, max_turns + 1):
        before = len(messages)
        messages = trim_history(messages, MAX_HISTORY_MESSAGES)

        # TODO 2 ── 如果这次裁剪真的削减了长度，记一条日志。
        #   log("trimmed", turn=turn, before=before, after=len(messages))
        ...  # 替换成日志调用（只在 before != len(messages) 时记）

        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        print(f"\n  ── 第 {turn} 轮 ──")
        print("     stop_reason:", resp.stop_reason)
        print("     消息条数    :", len(messages))

        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            print("\n  [最终回答]", text.strip())
            print(f"  （共 {turn} 轮）")
            return

        calls = [b for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for call in calls:
            try:
                output = TOOLS[call.name](**call.input)
                is_error = False
            except Exception as e:
                output = f"工具执行失败：{e}"
                is_error = True

            # TODO 3 ── 每次执行工具都记一条日志。
            #   log("tool_call", turn=turn, name=call.name, input=call.input,
            #       output=str(output), is_error=is_error)
            ...  # 替换成日志调用

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": str(output),
                    "is_error": is_error,
                }
            )

        messages.append({"role": "user", "content": results})

    print(f"\n  ⚠️ 到了 {max_turns} 轮上限还没收手，强制停止。")


# ==========================================================
# 试两个问题。第二个需要三次工具调用，MAX_HISTORY_MESSAGES=3
# 会让你在这一个问题里就看到至少一次真实的裁剪。
# ==========================================================

QUESTIONS = [
    "杭州今天天气怎么样？",
    "杭州今天几度？在那个温度上再加 7 度，然后再除以 3，结果是多少？",
]

for q in QUESTIONS:
    print("\n" + "=" * 58)
    print("问题:", q)
    print("=" * 58)
    run_agent(q)
