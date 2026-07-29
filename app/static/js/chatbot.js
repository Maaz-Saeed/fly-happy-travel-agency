/* Fly Happy chatbot widget behaviour */
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("chatbot-toggle");
  var win = document.getElementById("chatbot-window");
  var closeBtn = document.getElementById("chatbot-close");
  var form = document.getElementById("chatbot-form");
  var input = document.getElementById("chatbot-input");
  var messages = document.getElementById("chatbot-messages");
  var badge = document.querySelector(".chatbot-badge");

  if (!toggle || !win) return;

  toggle.addEventListener("click", function () {
    win.classList.toggle("d-none");
    if (badge) badge.style.display = "none";
    if (!win.classList.contains("d-none")) input.focus();
  });
  closeBtn.addEventListener("click", function () { win.classList.add("d-none"); });

  function addMessage(text, sender) {
    var div = document.createElement("div");
    div.className = "msg " + sender;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function sendMessage(text) {
    if (!text.trim()) return;
    addMessage(text, "user");
    var typing = document.createElement("div");
    typing.className = "msg bot";
    typing.textContent = "Typing...";
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;

    fetch("/chatbot/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        typing.remove();
        addMessage(data.reply, "bot");
      })
      .catch(function () {
        typing.remove();
        addMessage("Sorry, I'm having trouble connecting. Please call us at the number in the footer.", "bot");
      });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value;
    input.value = "";
    sendMessage(text);
  });

  document.querySelectorAll(".quick-reply").forEach(function (btn) {
    btn.addEventListener("click", function () { sendMessage(btn.textContent); });
  });
});
