"""
第 4 课 · 让 Agent 扛得住真实世界
配套课程： lessons/0004-resilient-agent.html

第 3 课的 Agent 能跑，但很脆弱：
    · 工具抛异常 → 整个程序崩掉
    · 危险操作 → 没人确认就执行了

这一课把它补成能交付的样子。循环骨架还是那一个，只是执行工具那一步变严谨了。

运行前先跑： python3 exercises/00_check_env.py
运行：       python3 exercises/04_resilient_loop.py
"""

import os

import anthropic

MODEL = os.environ.get("LESSON_MODEL") or "claude-haiku-4-5"

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("没找到 ANTHROPIC_API_KEY。先跑 exercises/00_check_env.py 排查。")

client = anthropic.Anthropic()


# ==========================================================
# 第 1 层 · 工具的实现
# 前两个和第 3 课一样。新增两个专门用来触发今天要处理的两种失败：
#   divide      —— 除以 0 会抛异常，练「工具报错怎么办」
#   delete_note —— 危险操作（会真的"删掉"东西），练「执行前先问人」
# ==========================================================


def get_weather(city):
    return f"{city}今天晴，26 度"


def add(a, b):
    return a + b


def divide(a, b):
    return a / b  # b 是 0 时会抛 ZeroDivisionError，这是故意的


def delete_note(note_id):
    return f"笔记 {note_id} 已删除"  # 只是打印一句话，没有真的数据库


TOOLS = {
    "get_weather": get_weather,
    "add": add,
    "divide": divide,
    "delete_note": delete_note,
}

# 标记哪些工具属于"危险操作"：执行前必须先问人。
# 判断标准很简单：一旦执行，后果不可逆（删除、发送、下单、转账……）。
DANGEROUS = {"delete_note"}


# ==========================================================
# 第 2 层 · 工具的声明
# 和第 3 课的写法完全一样，这里不再是新知识。
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

DELETE_NOTE_SCHEMA = {
    "name": "delete_note",
    "description": "删除一条笔记。这是不可逆操作，只有用户明确要求删除时才使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "note_id": {"type": "integer", "description": "要删除的笔记 id"},
        },
        "required": ["note_id"],
    },
}

TOOL_SCHEMAS = [WEATHER_SCHEMA, ADD_SCHEMA, DIVIDE_SCHEMA, DELETE_NOTE_SCHEMA]


# ==========================================================
# 第 3 层 · Agent 循环
# 骨架和第 3 课一样。变化只在"执行工具"这一小块。
# ==========================================================


def run_agent(question, max_turns=6):
    messages = [{"role": "user", "content": question}]

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

        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            print("\n  [最终回答]", text.strip())
            print(f"  （共 {turn} 轮）")
            return

        calls = [b for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for call in calls:
            # TODO 1 ── 危险操作先问人。
            #   如果 call.name 在 DANGEROUS 里，用 input() 问一句确认，
            #   比如：f"  [需要确认] 要执行 {call.name}({call.input}) 吗？(y/n) "
            #   回答不是 y/Y 就把 confirmed 设成 False。
            #   不在 DANGEROUS 里的工具，confirmed 直接是 True，不用问。
            confirmed = True

            if call.name in DANGEROUS:
                reply = input(f"  [需要确认] 要执行 {call.name}({call.input}) 吗？(y/n) ")
                confirmed = reply.strip().lower() == "y"
        

            if not confirmed:
                # 用户拒绝了：不要真的执行工具，直接把这当成一次"失败"报回去。
                output = "用户拒绝执行此操作"
                is_error = True
            else:
                # TODO 2 ── 工具报错不能崩掉整个程序。
                #   用 try/except 包住执行：
                #     成功 → is_error = False
                #     异常 → output 设成一句包含异常信息的字符串，is_error = True
                #   写法参考协议速查（reference/tool-use-protocol.html）「工具报错怎么办」一节。
                ...  # 替换成 try/except
                try :
                    output = TOOLS[call.name](**call.input)
                    is_error = False
                except Exception as e:
                    output = f"工具执行失败：{e}"
                    is_error = True


            tag = "✗" if is_error else "✓"
            print(f"     [执行 {tag}] {call.name}({call.input}) -> {output}")

            # TODO 3 ── 构造 tool_result，记得带上 is_error。
            #   字段清单：type / tool_use_id / content / is_error
            results.append({
                "type":"tool_result",
                "tool_use_id":call.id,
                "content":str(output),
                "is_error":is_error,
            })

        if not results:
            raise SystemExit("TODO 1~3 还没完成：results 是空的。")

        messages.append({"role": "user", "content": results})

    print(f"\n  ⚠️ 到了 {max_turns} 轮上限还没收手，强制停止。")


# ==========================================================
# 试三个问题。
#   1. 普通问题，确认没有回归
#   2. 故意除以 0，看模型怎么应对一次工具报错
#   3. 要求删除笔记，你会被问是否确认——试着分别答 y 和 n
# ==========================================================

QUESTIONS = [
    "杭州今天天气怎么样？",
    "帮我算一下 10 除以 0 等于多少？",
    "帮我删除 id 是 42 的笔记",
]

for q in QUESTIONS:
    print("\n" + "=" * 58)
    print("问题:", q)
    print("=" * 58)
    run_agent(q)
