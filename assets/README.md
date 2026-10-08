# assets/ — 可复用组件

课程不是一次性文件。**先读这里，能复用就复用**，需要新东西时把它写成组件放进来，而不是内联进某一节课。

| 组件 | 作用 | 引用方式 |
|---|---|---|
| `lesson.css` | 全部课程与参考文档的共享样式。Tufte 风格、可打印、含测验样式 | `<link rel="stylesheet" href="../assets/lesson.css">` |
| `quiz.js` | 回忆式测验，点击即时判定 + 解释 + 打乱选项顺序 | `<script src="../assets/quiz.js" defer></script>` |

## quiz.js 约定

选项**必须**保持相同字数与格式。长度差异本身就是答案线索，会把回忆练习降级成模式匹配。`answer` 填原始数组下标，渲染时自动打乱位置。

## 尚未建成、迟早需要的组件

- `runner.js` — 浏览器内跑 Python（Pyodide），让代码练习的反馈回路从「切到终端」缩短到「点一下」
- `diagram.css` — Agent 循环 / 消息流的示意图样式
- `flashcards.js` — 跨课程的间隔复习卡组，服务于储存强度
