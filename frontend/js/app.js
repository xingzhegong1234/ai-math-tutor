/**
 * AI 考研数学助教 — Frontend App
 * Communicates with the FastAPI backend to provide math tutoring via MiMo API.
 */

const API_BASE = 'http://localhost:8000/api';

// ─── State ─────────────────────────────────────────────────────
const state = {
  conversations: [],
  currentConvId: null,
  currentMessages: [],
  mode: 'solve',
  reasoning: false,
  filter: 'all',
  sending: false,
  hasMoreMessages: false,
};

// ─── DOM refs ──────────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const sidebar = {
  list:  () => $('#conversationList'),
  tabs:  () => $$('.tab'),
  newBtn: () => $('#newChatBtn'),
};

const chat = {
  header:  () => $('#chatTitle'),
  container: () => $('#messageContainer'),
  input:   () => $('#messageInput'),
  sendBtn: () => $('#sendBtn'),
  bookmarkBtn: () => $('#bookmarkBtn'),
  deleteBtn:   () => $('#deleteChatBtn'),
  imageInput:  () => $('#imageUpload'),
  imagePreview: () => $('#imagePreview'),
  previewImg:  () => $('#previewImg'),
  removeImageBtn: () => $('#removeImage'),
};

const modeBtns = () => $$('.mode-btn');
const reasoningCheck = () => $('#reasoningCheck');

// ─── API calls ─────────────────────────────────────────────────
async function apiGet(url) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`);
  return res.json();
}

async function apiDelete(url) {
  const res = await fetch(`${API_BASE}${url}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`DELETE ${url} failed: ${res.status}`);
  return res.json();
}

async function sendChat(message, convId, mode, reasoning, imageFile) {
  const formData = new FormData();
  if (convId) formData.append('conversation_id', String(convId));
  formData.append('message', message);
  formData.append('mode', mode);
  formData.append('reasoning', String(reasoning));
  if (imageFile) formData.append('image', imageFile);

  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `请求失败: ${res.status}`);
  }
  return res.json();
}

// ─── Render helpers ────────────────────────────────────────────
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function renderMarkdown(text) {
  // Use marked to render markdown
  let html = marked.parse(text, { breaks: true, gfm: true });
  return html;
}

function renderMath(html) {
  // Wrap the html in a temp element, run KaTeX auto-render, return innerHTML
  const el = document.createElement('div');
  el.innerHTML = html;
  if (window.renderMathInElement) {
    try {
      renderMathInElement(el, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true },
        ],
        throwOnError: false,
      });
    } catch (_) {}
  }
  return el.innerHTML;
}

function formatTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr.replace(' ', 'T') + '+08:00');
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

// ─── Message rendering ─────────────────────────────────────────
function addMessageToDOM(role, content, time) {
  const container = chat.container();
  // Remove welcome
  container.querySelector('.welcome')?.remove();

  const div = document.createElement('div');
  div.className = `message ${role}`;

  let rendered = renderMarkdown(content);
  rendered = renderMath(rendered);

  div.innerHTML = `
    <div class="message-bubble">${rendered}</div>
    <div class="message-time">${time ? formatTime(time) : ''}</div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function showTyping() {
  const container = chat.container();
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.id = 'typingIndicator';
  div.innerHTML = `<div class="message-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function clearMessages() {
  chat.container().innerHTML = '';
}

function scrollToBottom() {
  chat.container().scrollTop = chat.container().scrollHeight;
}

// ─── Conversation list ─────────────────────────────────────────
function renderConversationList() {
  const list = sidebar.list();
  const filtered = state.filter === 'bookmarked'
    ? state.conversations.filter(c => c.bookmarked)
    : state.conversations;

  if (filtered.length === 0) {
    list.innerHTML = `<div class="empty-list">${state.filter === 'bookmarked' ? '还没有收藏的对话' : '还没有对话，点击"＋新对话"开始'}</div>`;
    return;
  }

  list.innerHTML = filtered.map(c => `
    <div class="conversation-item ${c.id === state.currentConvId ? 'active' : ''}"
         data-id="${c.id}">
      <div class="conv-title">${escapeHtml(c.title)}</div>
      <div class="conv-meta">${formatTime(c.updated_at)}</div>
      ${c.bookmarked ? '<span class="conv-bookmark">⭐</span>' : ''}
    </div>
  `).join('');

  // Click to switch conversation
  list.querySelectorAll('.conversation-item').forEach(el => {
    el.addEventListener('click', () => {
      loadConversation(parseInt(el.dataset.id));
    });
  });
}

// ─── Conversations CRUD ────────────────────────────────────────
async function loadConversations() {
  try {
    state.conversations = await apiGet('/conversations');
    renderConversationList();
  } catch (e) {
    console.error('加载对话列表失败:', e);
  }
}

async function loadConversation(convId) {
  try {
    state.currentConvId = convId;
    const data = await apiGet(`/conversations/${convId}`);
    state.currentMessages = data.messages;
    state.currentConvId = convId;

    // Update header
    chat.header().textContent = data.conversation.title;
    chat.bookmarkBtn().textContent = data.conversation.bookmarked ? '⭐' : '☆';
    chat.bookmarkBtn().classList.toggle('bookmarked', !!data.conversation.bookmarked);

    // Render messages
    clearMessages();
    let lastUserMsg = null;
    data.messages.forEach(msg => {
      if (msg.role === 'user') lastUserMsg = msg;
      addMessageToDOM(msg.role, msg.content, msg.created_at);
    });

    renderConversationList();
    scrollToBottom();
  } catch (e) {
    console.error('加载对话失败:', e);
  }
}

async function newConversation() {
  state.currentConvId = null;
  state.currentMessages = [];
  clearMessages();

  // Re-create welcome
  chat.container().innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">📐</div>
      <h1>AI 考研数学助教</h1>
      <p>上传题目截图或输入数学问题，获得详细解答</p>
      <div class="welcome-modes">
        <div class="mode-card" data-mode="solve"><strong>✏️ 解题</strong><span>输入题目，获得完整解题步骤</span></div>
        <div class="mode-card" data-mode="check"><strong>✅ 批改</strong><span>上传你的解题过程，AI 帮你检查</span></div>
        <div class="mode-card" data-mode="similar"><strong>📝 类似题</strong><span>基于当前题目生成同类变式</span></div>
        <div class="mode-card" data-mode="concept"><strong>📖 概念</strong><span>解释数学概念、定理和公式</span></div>
      </div>
    </div>
  `;

  // Click mode cards
  document.querySelectorAll('.mode-card').forEach(card => {
    card.addEventListener('click', () => {
      const mode = card.dataset.mode;
      setMode(mode);
      chat.input().focus();
    });
  });

  chat.header().textContent = 'AI 考研数学助教';
  chat.bookmarkBtn().textContent = '☆';
  chat.bookmarkBtn().classList.remove('bookmarked');
  renderConversationList();
}

// ─── Send message ──────────────────────────────────────────────
async function handleSend() {
  if (state.sending) return;

  const message = chat.input().value.trim();
  const imageFile = chat.imageInput().files?.[0];
  if (!message && !imageFile) return;

  state.sending = true;
  chat.sendBtn().disabled = true;

  const currentMode = state.mode;
  const currentReasoning = reasoningCheck().checked;

  // Show user message immediately
  addMessageToDOM('user', message || '(上传了图片)');
  showTyping();

  // Clear input
  chat.input().value = '';
  clearImagePreview();

  try {
    const result = await sendChat(
      message || '(请根据图片解题)',
      state.currentConvId,
      currentMode,
      currentReasoning,
      imageFile,
    );

    removeTyping();

    state.currentConvId = result.conversation_id;
    addMessageToDOM('assistant', result.reply, new Date().toISOString());

    // Refresh conversation list
    await loadConversations();
  } catch (e) {
    removeTyping();
    // Show error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message assistant';
    errorDiv.innerHTML = `<div class="message-bubble" style="border-color: var(--danger); color: var(--danger);">
      ❌ 请求失败: ${escapeHtml(e.message)}
    </div>`;
    chat.container().appendChild(errorDiv);
    scrollToBottom();
  } finally {
    state.sending = false;
    chat.sendBtn().disabled = false;
    chat.input().focus();
  }
}

// ─── Mode switching ────────────────────────────────────────────
function setMode(mode) {
  state.mode = mode;
  modeBtns().forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });
}

// ─── Image preview ─────────────────────────────────────────────
function handleImageSelect(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    chat.previewImg().src = e.target.result;
    chat.imagePreview().classList.remove('hidden');
  };
  reader.readAsDataURL(file);
}

function clearImagePreview() {
  chat.imagePreview().classList.add('hidden');
  chat.previewImg().src = '';
  chat.imageInput().value = '';
}

// ─── Bookmark / Delete ─────────────────────────────────────────
async function handleBookmark() {
  if (!state.currentConvId) return;
  try {
    const res = await apiGet(`/conversations/${state.currentConvId}/bookmark`);
    // Actually it's a POST... let me use fetch directly
    const r = await fetch(`${API_BASE}/conversations/${state.currentConvId}/bookmark`, { method: 'POST' });
    const data = await r.json();
    chat.bookmarkBtn().textContent = data.bookmarked ? '⭐' : '☆';
    chat.bookmarkBtn().classList.toggle('bookmarked', !!data.bookmarked);
    await loadConversations();
  } catch (e) {
    console.error('收藏失败:', e);
  }
}

async function handleDelete() {
  if (!state.currentConvId) return;
  if (!confirm('确定要删除这个对话吗？')) return;
  try {
    await apiDelete(`/conversations/${state.currentConvId}`);
    await newConversation();
    await loadConversations();
  } catch (e) {
    console.error('删除失败:', e);
  }
}

// ─── Keyboard shortcuts ────────────────────────────────────────
function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

// ─── Init ──────────────────────────────────────────────────────
async function init() {
  await loadConversations();

  // New chat
  sidebar.newBtn().addEventListener('click', newConversation);

  // Tab switching
  sidebar.tabs().forEach(tab => {
    tab.addEventListener('click', () => {
      sidebar.tabs().forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.filter = tab.dataset.filter;
      renderConversationList();
    });
  });

  // Mode buttons
  modeBtns().forEach(btn => {
    btn.addEventListener('click', () => setMode(btn.dataset.mode));
  });

  // Send
  chat.sendBtn().addEventListener('click', handleSend);
  chat.input().addEventListener('keydown', handleInputKeydown);

  // Image upload
  chat.imageInput().addEventListener('change', (e) => {
    handleImageSelect(e.target.files?.[0]);
  });
  chat.removeImageBtn().addEventListener('click', clearImagePreview);

  // Bookmark & delete
  chat.bookmarkBtn().addEventListener('click', handleBookmark);
  chat.deleteBtn().addEventListener('click', handleDelete);

  // Welcome mode cards
  document.querySelectorAll('.mode-card').forEach(card => {
    card.addEventListener('click', () => {
      const mode = card.dataset.mode;
      setMode(mode);
      chat.input().focus();
    });
  });
}

// Start when DOM ready
document.addEventListener('DOMContentLoaded', init);
