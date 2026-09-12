const inputBox = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const chatArea = document.getElementById("chatArea");
const historyContainer = document.querySelector(".history");
const pdfUpload = document.getElementById("pdfUpload");

// Handle Enter vs Shift+Enter
inputBox.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    if (event.shiftKey) {
      return; // allow newline
    } else {
      event.preventDefault();
      sendBtn.click(); // send message
    }
  }
});

// Send button logic
sendBtn.addEventListener("click", async () => {
  const userMessage = inputBox.value.trim();
  if (!userMessage) return;

  // Show user message
  const userDiv = document.createElement("div");
  userDiv.classList.add("message", "user");
  userDiv.innerHTML = `<div class="profile user">You</div><div class="text">${userMessage}</div>`;
  chatArea.appendChild(userDiv);

  inputBox.value = "";

  // Show AI "typing dots"
  const aiDiv = document.createElement("div");
  aiDiv.classList.add("message", "assistant");
  aiDiv.innerHTML = `<div class="profile ai">AI</div><div class="text typing">...</div>`;
  chatArea.appendChild(aiDiv);
  chatArea.scrollTop = chatArea.scrollHeight;

  // Fetch response from backend
  const res = await fetch("/chat_api", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage })
  });
  const data = await res.json();

  const answer = data.response;
  const textDiv = aiDiv.querySelector(".text");
  textDiv.classList.remove("typing");
  textDiv.innerHTML = "";

  // ✅ Detect Mermaid flowchart blocks
  if (answer.includes("```mermaid")) {
    const mermaidCode = answer.match(/```mermaid([\s\S]*?)```/)[1];
    textDiv.innerHTML = `<div class="mermaid">${mermaidCode}</div>`;
    if (window.mermaid) {
      window.mermaid.init(undefined, textDiv.querySelectorAll(".mermaid"));
    }
  } else {
    // Normal typing effect
    let i = 0;
    const typingInterval = setInterval(() => {
      textDiv.innerHTML += answer.charAt(i);
      i++;
      chatArea.scrollTop = chatArea.scrollHeight;
      if (i >= answer.length) clearInterval(typingInterval);
    }, 6);
  }

  // 🔥 Update history dynamically
  updateHistory(data.history);
});

// Function to update sidebar history
function updateHistory(history) {
  historyContainer.innerHTML = ""; // clear old items
  history.forEach((item) => {
    const div = document.createElement("div");
    div.classList.add("history-item");
    div.textContent = item;
    div.addEventListener("click", () => {
      inputBox.value = item;
      inputBox.focus();
    });
    historyContainer.appendChild(div);
  });
}

// =========================
// PDF Upload Logic
// =========================
pdfUpload.addEventListener("change", async () => {
  const file = pdfUpload.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  // Show uploading message
  const userDiv = document.createElement("div");
  userDiv.classList.add("message", "user");
  userDiv.innerHTML = `<div class="profile user">You</div><div class="text">📂 Uploading PDF: <strong>${file.name}</strong>...</div>`;
  chatArea.appendChild(userDiv);

  try {
    const res = await fetch("/upload_pdf", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    // 🎉 Attractive AI confirmation
    const aiDiv = document.createElement("div");
    aiDiv.classList.add("message", "assistant");
    aiDiv.innerHTML = `
      <div class="profile ai">AI</div>
      <div class="text">
        ✅ <strong>Success!</strong><br>
        Your file <em>${file.name}</em> has been uploaded.<br>
        🚀 The <span style="color:#4CAF50;font-weight:bold;">Knowledge Base</span> is now trained and ready to answer questions!
      </div>
    `;
    chatArea.appendChild(aiDiv);

    chatArea.scrollTop = chatArea.scrollHeight;
  } catch (err) {
    console.error("Upload error:", err);
    const aiDiv = document.createElement("div");
    aiDiv.classList.add("message", "assistant");
    aiDiv.innerHTML = `<div class="profile ai">AI</div><div class="text">❌ PDF upload failed. Please try again.</div>`;
    chatArea.appendChild(aiDiv);
  }
});
