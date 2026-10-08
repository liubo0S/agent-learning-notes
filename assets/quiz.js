/* ==========================================================================
   quiz.js — 可复用的「回忆式测验」组件（零依赖）
   即时反馈：点击选项立刻判定、立刻给出解释。这是课程的主反馈回路。

   用法：
   <div class="quiz" data-title="回顾测验">
     <script type="application/json">
     [
       {
         "q":       "题干，可含 <code>行内 HTML</code>",
         "options": ["选项一", "选项二", "选项三", "选项四"],
         "answer":  0,
         "why":     "为什么对 / 为什么其他选项错"
       }
     ]
     </script>
   </div>

   约定：
   - "answer" 是**原始** options 数组的下标；渲染时会随机打乱顺序，
     所以正确答案的位置不会成为线索。
   - 各选项应保持相同的字数与格式，避免通过长度猜答案。
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.quiz').forEach(mountQuiz);
});

function mountQuiz(root) {
  var src = root.querySelector('script[type="application/json"]');
  if (!src) return;

  var questions;
  try {
    questions = JSON.parse(src.textContent);
  } catch (e) {
    root.textContent = '测验数据解析失败：' + e.message;
    return;
  }

  render();

  function render() {
    var answered = 0;
    var correct = 0;

    root.innerHTML = '';

    var head = el('div', 'quiz-head');
    var title = el('span', 'quiz-title');
    title.textContent = root.dataset.title || '回顾测验';
    var score = el('span', 'quiz-score');
    score.setAttribute('aria-live', 'polite');
    score.textContent = '0 / ' + questions.length;
    head.append(title, score);
    root.append(head);

    questions.forEach(function (item, qi) {
      var block = el('div', 'quiz-q');

      var prompt = el('p', 'quiz-prompt');
      prompt.innerHTML = '<span class="n">' + (qi + 1) + '.</span>' + item.q;
      block.append(prompt);

      var opts = el('div', 'quiz-opts');
      var order = shuffled(item.options.length);
      var locked = false;

      order.forEach(function (originalIndex) {
        var btn = el('button', 'quiz-opt');
        btn.type = 'button';
        btn.textContent = item.options[originalIndex];
        btn.addEventListener('click', function () {
          if (locked) return;
          locked = true;
          answered++;

          var isRight = originalIndex === item.answer;
          if (isRight) correct++;

          opts.querySelectorAll('.quiz-opt').forEach(function (b) {
            b.disabled = true;
          });
          btn.classList.add(isRight ? 'is-correct' : 'is-wrong');

          // 答错时也把正确答案标出来 —— 反馈必须闭环
          if (!isRight) {
            opts.querySelectorAll('.quiz-opt').forEach(function (b) {
              if (b.textContent === item.options[item.answer]) {
                b.classList.add('is-correct');
              }
            });
          }

          if (item.why) {
            var why = el('div', 'quiz-why');
            why.innerHTML = (isRight ? '✓ ' : '✗ ') + item.why;
            block.append(why);
          }

          score.textContent = correct + ' / ' + questions.length;
          if (answered === questions.length) finish(correct);
        });
        opts.append(btn);
      });

      block.append(opts);
      root.append(block);
    });
  }

  function finish(correct) {
    var foot = el('div', 'quiz-foot');
    var msg = el('span');
    var n = questions.length;
    msg.textContent =
      correct === n ? '全对。这些已经进了长期记忆的候选区 —— 隔几天我会再考一次。'
      : correct >= n - 1 ? '接近满分。错的那一条值得回到课文里重看一遍。'
      : '答错的部分不是失败，是这节课真正的收获所在 —— 直接来问我。';
    var again = el('button', 'quiz-reset');
    again.type = 'button';
    again.textContent = '重做一次';
    again.addEventListener('click', render);
    foot.append(msg, again);
    root.append(foot);
  }
}

/* --- 小工具 -------------------------------------------------------------- */

function el(tag, className) {
  var node = document.createElement(tag);
  if (className) node.className = className;
  return node;
}

/** 返回 0..n-1 的随机排列（Fisher–Yates） */
function shuffled(n) {
  var a = Array.from({ length: n }, function (_, i) { return i; });
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}
