const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const viewAllFaqsBtn = document.getElementById('viewAllFaqs');
const faqModal = document.getElementById('faqModal');
const closeModalBtn = document.getElementById('closeModal');
const faqList = document.getElementById('faqList');

function timeNow() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendMessage({ role, text, score = null }) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  const metaRow = document.createElement('div');
  metaRow.className = 'meta-row';

  const ts = document.createElement('span');
  ts.className = 'timestamp';
  ts.textContent = timeNow();
  metaRow.appendChild(ts);

  if (score !== null) {
    const pill = document.createElement('span');
    pill.className = 'confidence-pill';
    pill.textContent = `match ${Math.round(score * 100)}%`;
    metaRow.appendChild(pill);
  }

  wrap.appendChild(bubble);
  wrap.appendChild(metaRow);
  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot typing-indicator';
  wrap.id = 'typingIndicator';
  wrap.innerHTML = `<div class="bubble"><span></span><span></span><span></span></div>`;
  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

async function sendMessage(text) {
  appendMessage({ role: 'user', text });
  showTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    hideTyping();
    appendMessage({ role: 'bot', text: data.answer, score: data.score ?? null });
  } catch (err) {
    hideTyping();
    appendMessage({ role: 'bot', text: 'Something went wrong reaching the server. Please make sure app.py is running.' });
  }
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = '';
  sendMessage(text);
});

document.querySelectorAll('.suggestion-chip').forEach((chip) => {
  chip.addEventListener('click', () => sendMessage(chip.dataset.q));
});

// FAQ modal
viewAllFaqsBtn.addEventListener('click', async () => {
  faqList.innerHTML = '<p style="font-size:13px;color:#5a6274;">Loading...</p>';
  faqModal.classList.remove('hidden');
  try {
    const res = await fetch('/api/faqs');
    const faqs = await res.json();
    faqList.innerHTML = '';
    faqs.forEach((f) => {
      const item = document.createElement('div');
      item.className = 'faq-item';
      item.innerHTML = `<h4>${f.question}</h4><p>${f.answer}</p>`;
      item.addEventListener('click', () => {
        faqModal.classList.add('hidden');
        sendMessage(f.question);
      });
      faqList.appendChild(item);
    });
  } catch (err) {
    faqList.innerHTML = '<p>Could not load FAQs.</p>';
  }
});

closeModalBtn.addEventListener('click', () => faqModal.classList.add('hidden'));
faqModal.addEventListener('click', (e) => {
  if (e.target === faqModal) faqModal.classList.add('hidden');
});

// Greet on load
window.addEventListener('DOMContentLoaded', () => {
  appendMessage({
    role: 'bot',
    text: "Hi! I'm the CodeAlpha FAQ Bot. Ask me anything about the internship — tasks, certificates, submissions, and more.",
  });
});
