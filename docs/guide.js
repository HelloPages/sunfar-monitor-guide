"use strict";

const find = (selector) => document.querySelector(selector);
const all = (selector) => Array.from(document.querySelectorAll(selector));
const boxes = all(".product");
const tilesById = new Map(all(".tile").map((tile) => [tile.dataset.key, tile]));
const search = find("#query");
const groupButtons = all("[data-group]");
const status = find("#announcement");
let activeGroup = "";

function normalized(value) {
  return value.normalize("NFKC").toLowerCase().replace(/[\s—–_-]+/g, "");
}

const searchable = boxes.map((box) => {
  const { textContent } = box.querySelector(".product-cover");
  return { box, terms: normalized(textContent) };
});

function filterModels() {
  const query = normalized(search.value);
  let shown = 0;
  for (const { box, terms } of searchable) {
    const matchesGroup = !activeGroup || box.dataset.family === activeGroup;
    const visible = matchesGroup && terms.includes(query);
    box.hidden = !visible;
    tilesById.get(box.dataset.key).hidden = !visible;
    if (visible) shown++;
  }
  find("#results").textContent = `${shown}個銷售配置`;
  find("#empty").hidden = shown !== 0;
  find("#lessons").hidden = shown === 0;
  groupButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.group === activeGroup)));
}

function resetFilter() {
  search.value = "";
  activeGroup = "";
  filterModels();
}

for (const button of groupButtons) {
  button.addEventListener("click", () => {
    activeGroup = button.dataset.group;
    filterModels();
  });
}
search.addEventListener("input", filterModels);
find("#reset-filter").addEventListener("click", () => {
  resetFilter();
  search.focus();
});

function revealTarget() {
  const target = document.getElementById(location.hash.slice(1));
  if (!target?.classList.contains("product")) return;
  if (target.hidden) resetFilter();
  target.scrollIntoView({ block: "start" });
  target.focus({ preventScroll: true });
}

window.addEventListener("hashchange", revealTarget);
revealTarget();

for (const button of all(".copy")) {
  button.addEventListener("click", async () => {
    const model = button.dataset.model;
    try {
      await navigator.clipboard.writeText(model);
      button.textContent = "已複製";
      status.textContent = `已複製型號${model}`;
    } catch {
      const text = button.closest(".product").querySelector(".model");
      const range = document.createRange();
      range.selectNodeContents(text);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
      button.textContent = "長按複製型號";
      status.textContent = `已選取型號${model}，可長按複製`;
    }
  });
}

const { questions } = JSON.parse(find("#guide-data").textContent);
const prompt = find("#quiz-question");
const choices = find("#quiz-choices");
const feedback = find("#quiz-feedback");
const progress = find("#quiz-progress");
const scoreLabel = find("#quiz-score");
const next = find("#quiz-next");
const review = find("#quiz-review");
let current = 0;
let score = 0;

function showQuestion(focus = false) {
  choices.replaceChildren();
  feedback.textContent = "";
  next.hidden = true;
  review.hidden = true;
  scoreLabel.textContent = `答對${score}題`;
  const question = questions[current];
  if (!question) {
    progress.textContent = `已完成${questions.length}題`;
    prompt.textContent = `本次答對${score}／${questions.length}題`;
    feedback.textContent = "可重新作答，或回到機款速查再複習。";
    prompt.focus();
    return;
  }
  progress.textContent = `第${current + 1}題，共${questions.length}題`;
  prompt.textContent = question.prompt;
  for (const [index, item] of question.choices.entries()) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item.name;
    button.addEventListener("click", () => answer(index, question));
    choices.append(button);
  }
  if (focus) prompt.focus();
}

function answer(index, question) {
  const correct = index === question.answer;
  if (correct) score++;
  scoreLabel.textContent = `答對${score}題`;
  const buttons = Array.from(choices.querySelectorAll("button"));
  buttons.forEach((button) => { button.disabled = true; });
  buttons[question.answer].classList.add("right");
  if (!correct) buttons[index].classList.add("wrong");
  feedback.textContent = `${correct ? "答對了。" : "可先示範" + question.choices[question.answer].name + "。"}${question.reason}`;
  review.href = "#" + question.choices[question.answer].id;
  review.hidden = false;
  next.textContent = current === questions.length - 1 ? "看練習結果" : "下一題";
  next.hidden = false;
  next.focus({ preventScroll: true });
}

next.addEventListener("click", () => {
  current++;
  showQuestion(true);
});
find("#quiz-reset").addEventListener("click", () => {
  current = score = 0;
  showQuestion(true);
});
showQuestion();
