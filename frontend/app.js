

const BACKEND_URL = "http://localhost:8000";


window.addEventListener("load", async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/status`);
    const data = await response.json();

    const filesList = document.getElementById("files-list");

    if (data.curriculum_files && data.curriculum_files.length > 0) {
      filesList.innerHTML = data.curriculum_files
        .map(f => `<span class="file-badge">
                     <span class="status-dot"></span>${f}
                   </span>`)
        .join("");
    } else {
      filesList.innerHTML = `<span class="loading-files">No curriculum loaded</span>`;
    }
  } catch (err) {
    document.getElementById("files-list").innerHTML =
      `<span class="loading-files">Cannot connect to server</span>`;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("question-input");

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  });


  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });
});


async function sendQuestion() {
  const input = document.getElementById("question-input");
  const question = input.value.trim();
  if (!question) return;

  input.value = "";
  input.style.height = "auto";

  const btn = document.getElementById("send-btn");
  btn.disabled = true;

  addMessage("user", question);
  const thinkingId = addThinking();

  try {
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question }),
    });

    const data = await response.json();
    removeThinking(thinkingId);

    if (response.ok) {
      addBotMessage(data.answer, data.sources);
    } else {
      addMessage("bot", `${data.detail || "Something went wrong. Please try again."}`);
    }

  } catch (err) {
    removeThinking(thinkingId);
    addMessage("bot", " Cannot connect to the server. Make sure the backend is running!");
  }

  btn.disabled = false;
  input.focus();
}


function addMessage(role, text) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = `message ${role === "user" ? "user-message" : "bot-message"}`;

  const avatar = role === "user" ? "👤" : "🦉";

  div.innerHTML = `
    <div class="avatar">${avatar}</div>
    <div class="bubble"><p>${escapeHtml(text)}</p></div>
  `;

  chatBox.appendChild(div);
  scrollToBottom();
}


function addBotMessage(answer, sources) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.className = "message bot-message";


  let sourcesHtml = "";
  if (sources && sources.length > 0) {
    const sourceItems = sources.map(s => `
      <div class="source-item">
        <span class="source-icon">📄</span>
        <span class="source-info">
          <span class="source-file">${s.file}</span>
          — Page ${s.page}
        </span>
        <span class="source-score">score: ${s.score}</span>
      </div>
    `).join("");

    sourcesHtml = `
      <div class="sources-box">
        <div class="sources-title">📎 Sources from your curriculum</div>
        ${sourceItems}
      </div>
    `;
  }

  const paragraphs = answer
    .split("\n")
    .filter(p => p.trim())
    .map(p => `<p>${escapeHtml(p)}</p>`)
    .join("");

  div.innerHTML = `
    <div class="avatar">🦉</div>
    <div class="bubble">
      ${paragraphs}
      ${sourcesHtml}
    </div>
  `;

  chatBox.appendChild(div);
  scrollToBottom();
}


function addThinking() {
  const chatBox = document.getElementById("chat-box");
  const id = "thinking-" + Date.now();

  const div = document.createElement("div");
  div.className = "message bot-message";
  div.id = id;
  div.innerHTML = `
    <div class="avatar">🦉</div>
    <div class="bubble">
      <div class="spinner-container">
        <div class="spinner"></div>
        <span class="spinner-text">Searching your curriculum...</span>
      </div>
    </div>
  `;

  chatBox.appendChild(div);
  scrollToBottom();
  return id;
}

function removeThinking(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function clearChat() {
  const chatBox = document.getElementById("chat-box");
  const messages = chatBox.querySelectorAll(".message");
  messages.forEach((msg, index) => {
    if (index !== 0) msg.remove();
  });
}

function scrollToBottom() {
  const main = document.querySelector("main");
  main.scrollTop = main.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
