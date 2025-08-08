document.addEventListener('DOMContentLoaded', () => {
    const bubble = document.getElementById('chat-bubble');
    const popup = document.getElementById('chat-popup');
    const closeBtn = document.getElementById('close-chat');
    const form = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('message');
    const sendBtn = document.getElementById('send-btn');
  
    if (!bubble || !popup) {
      console.error('Elements manquants : #chat-bubble ou #chat-popup introuvable.');
      return;
    }
  
    // Initial state: popup hidden, bubble visible
    popup.classList.add('hidden');
    bubble.setAttribute('aria-expanded', 'false');
  
    // Toggle: cliquer sur la bulle ouvre/ferme la boîte (la bulle reste visible)
    bubble.addEventListener('click', () => {
      const wasHidden = popup.classList.contains('hidden');
      if (wasHidden) {
        popup.classList.remove('hidden');
        bubble.setAttribute('aria-expanded', 'true');
        input.focus();
        scrollToBottom();
      } else {
        popup.classList.add('hidden');
        bubble.setAttribute('aria-expanded', 'false');
        bubble.focus();
      }
    });
  
    // Close button: ferme la boîte (la bulle reste visible)
    closeBtn.addEventListener('click', () => {
      popup.classList.add('hidden');
      bubble.setAttribute('aria-expanded', 'false');
      bubble.focus();
    });
  
    // Escape key to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !popup.classList.contains('hidden')) {
        popup.classList.add('hidden');
        bubble.setAttribute('aria-expanded', 'false');
        bubble.focus();
      }
    });
  
    // Helper: escape HTML
    function escapeHtml(unsafe) {
      return unsafe
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }
  
    // Append messages
    function appendUser(msg) {
      const el = document.createElement('div');
      el.className = 'message user';
      el.innerHTML = `<strong>Vous:</strong> ${escapeHtml(msg)}`;
      chatBox.appendChild(el);
      scrollToBottom();
    }
  
    function appendAssistant(msg) {
      const el = document.createElement('div');
      el.className = 'message assistant';
      el.innerHTML = `<strong>Assistant:</strong> ${escapeHtml(msg)}`;
      chatBox.appendChild(el);
      scrollToBottom();
    }
  
    function scrollToBottom() {
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  
    function setLoading(state) {
      sendBtn.disabled = !!state;
      sendBtn.textContent = state ? '…' : 'Envoyer';
    }
  
    // Send message
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      appendUser(text);
      setLoading(true);
  
      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
  
        let data;
        try {
          data = await res.json();
        } catch (err) {
          const txt = await res.text();
          appendAssistant(`Erreur serveur inattendue: ${res.status} ${res.statusText} — ${txt}`);
          return;
        }
  
        const reply = data && data.response ? data.response : 'Pas de réponse.';
        appendAssistant(reply);
  
      } catch (err) {
        appendAssistant(`Erreur réseau: ${err.message}`);
      } finally {
        setLoading(false);
        input.focus();
      }
    });
  });
  