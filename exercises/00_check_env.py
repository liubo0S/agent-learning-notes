"""
环境自检 · 跑课程练习之前先跑这个
配套课程： lessons/0002-first-real-call.html

两段检查：
  1. 基础连通 —— Python、SDK、密钥、base_url、模型，发一个最小请求
  2. 工具调用 —— 第 3 课要用 tools 参数，有些第三方端点不支持，提前探明

后面任何一节课报错，第一步都回来跑这个，能省掉大半排查时间。

运行： python3 exercises/00_check_env.py
"""

import os
import sys

print("=" * 58)
print("环境自检")
print("=" * 58)

print("Python 版本 :", sys.version.split()[0])

try:
    import anthropic
except ImportError:
    raise SystemExit(
        "✗ 没找到 anthropic 包。\n"
        "  依次执行： source .venv/bin/activate  然后  pip install anthropic"
    )

print("SDK 版本    :", anthropic.__version__)

key = os.environ.get("ANTHROPIC_API_KEY")
base = os.environ.get("ANTHROPIC_BASE_URL")
model = os.environ.get("LESSON_MODEL") or "claude-haiku-4-5"

if not key:
    raise SystemExit(
        "✗ 环境变量 ANTHROPIC_API_KEY 没设置。\n"
        '  执行： export ANTHROPIC_API_KEY="你的key"'
    )

# 只打印头尾，中间遮掉。密钥不该完整出现在任何日志里。
masked = f"{key[:6]}…{key[-4:]}" if len(key) > 12 else "（太短，确认没粘错）"
print(f"API key     : 已设置 {masked}，共 {len(key)} 字符")
print("base_url    :", base or "（未设置，走 Anthropic 官方）")
print("模型        :", model)

client = anthropic.Anthropic()
print("实际请求地址 :", client.base_url)


def text_of(resp):
    """从内容块列表里挑出文本块拼起来。

    块有好几种类型：
      text      普通文字      → .text
      thinking  思考过程      → .thinking（注意它没有 .text）
      tool_use  工具调用请求  → .name / .input
    思考型模型（比如 kimi-k3）会把 thinking 块放在最前面，
    所以绝不能假设 content[0] 就是文本。必须按类型筛。

    TS 类比： content.filter(b => b.type === "text").map(b => b.text).join("")
    """
    return "".join(b.text for b in resp.content if b.type == "text")


def explain(e):
    """把异常翻译成人话。"""
    if isinstance(e, anthropic.AuthenticationError):
        return (
            "认证失败（401）。三种常见原因：\n"
            "     1. key 无效或已撤销\n"
            "     2. key 和 base_url 不匹配（拿 Kimi 的 key 打了官方地址，或反过来）\n"
            "     3. 第三方中转要求的 key 格式不同"
        )
    if isinstance(e, anthropic.NotFoundError):
        return (
            f"404。模型名 '{model}' 这家供应商不认，\n"
            "     或者 base_url 多写了 /v1/messages（应该只填到根路径）。"
        )
    if isinstance(e, anthropic.APIConnectionError):
        return "连不上。base_url 拼错了，或这个域名从你的网络访问不到。"
    return f"{type(e).__name__}"


# ==========================================================
# 第 1 段 · 基础连通
# ==========================================================

print("\n" + "-" * 58)
print("[1/2] 基础连通")
print("-" * 58)

try:
    resp = client.messages.create(
        model=model,
        max_tokens=512,  # 思考型模型的 thinking 也算输出，给小了会在产出文本前就截断
        messages=[{"role": "user", "content": "回复两个字：收到"}],
    )
    print("  回复包含的块:", [b.type for b in resp.content])
    print("  模型回复    :", text_of(resp).strip() or "（没有文本块，可能被截断）")
    print(f"  用量        : 输入={resp.usage.input_tokens} 输出={resp.usage.output_tokens}")
    print(f"  停止原因    : {resp.stop_reason}")
    print("✓ 基础连通没问题。")
except Exception as e:
    print("✗", explain(e))
    print("  服务端原话:", getattr(e, "body", None) or e)
    raise SystemExit("\n基础连通就失败了，先解决这个，工具检测跳过。")


# ==========================================================
# 第 2 段 · 工具调用（第 3 课要用）
# ==========================================================

print("\n" + "-" * 58)
print("[2/2] 工具调用支持")
print("-" * 58)

PROBE_TOOL = {
    "name": "get_weather",
    "description": "查询某个城市当前的天气。当用户问到天气时使用。",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名，例如「杭州」"}
        },
        "required": ["city"],
    },
}

try:
    resp = client.messages.create(
        model=model,
        max_tokens=512,
        tools=[PROBE_TOOL],
        messages=[{"role": "user", "content": "杭州现在天气怎么样？"}],
    )
    kinds = [b.type for b in resp.content]
    print("  回复包含的块:", kinds)
    print(f"  停止原因    : {resp.stop_reason}")

    if "tool_use" in kinds:
        call = next(b for b in resp.content if b.type == "tool_use")
        print(f"  模型要求调用: {call.name}，参数 {call.input}")
        print(f"  配对用的 id : {call.id}")
        print("✓ 支持工具调用。第 3 课可以正常做。")
    else:
        print("⚠️  这次没触发工具调用。")
        print("   可能只是模型选择不用工具，不一定代表端点不支持。")
        print("   第 3 课如果反复失败，换成 Anthropic 官方或兼容中转再试。")

except Exception as e:
    print("✗", explain(e))
    print("  服务端原话:", getattr(e, "body", None) or e)
    print("\n  这家供应商可能不支持 tools 参数。第 3 课需要换供应商，")
    print("  改两个环境变量就行，Python 代码不用动。")
    raise SystemExit(1)


print("\n" + "=" * 58)
print("两段检查都通过，可以开始上课了。")
print("=" * 58)
