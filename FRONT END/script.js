const API = '/api/books';

// ── State ──
let books    = [];
let filtered = [];
let currentPage = 1;
let sortKey  = '';
let sortAsc  = true;
let editId   = null;   // id of the book being edited (null = new)

// ── Init ──
async function init() {
  await loadBooks();
  rebuildAuthorDropdown();
  renderSourceBars();
  applyFilters();
}

async function loadBooks() {
  try {
    const res = await fetch(API);
    books = await res.json();
  } catch (e) {
    showError('Could not connect to API. Make sure api.py is running on port 5000.');
  }
}

function showError(msg) {
  document.getElementById('tableBody').innerHTML =
    `<tr><td colspan="7"><div class="no-results">
       <i class="fas fa-circle-exclamation"></i>${msg}</div></td></tr>`;
}

// ── Hover Dropdown helpers ──
function selectHD(inputId, value, label, triggerId, menuId) {
  document.getElementById(inputId).value = value;
  document.getElementById(triggerId).innerHTML =
    `${label} <i class="fas fa-chevron-down hd-arrow"></i>`;
  document.querySelectorAll(`#${menuId} .hd-item`).forEach(item => {
    item.classList.toggle('selected', item.dataset.value === value);
  });
  applyFilters();
}

function resetHD(inputId, defaultLabel, triggerId, menuId) {
  document.getElementById(inputId).value = '';
  document.getElementById(triggerId).innerHTML =
    `${defaultLabel} <i class="fas fa-chevron-down hd-arrow"></i>`;
  document.querySelectorAll(`#${menuId} .hd-item`).forEach(item => {
    item.classList.toggle('selected', item.dataset.value === '');
  });
}

// ── Dropdowns / charts ──
function rebuildAuthorDropdown() {
  const authors = [...new Set(books.map(b => b.author))].sort();
  const currentVal = document.getElementById('filterAuthor').value;
  const menu = document.getElementById('menuAuthor');
  menu.innerHTML = `<div class="hd-item ${currentVal === '' ? 'selected' : ''}" data-value="" onclick="selectHD('filterAuthor','','All Authors','triggerAuthor','menuAuthor')">All Authors</div>`;
  authors.forEach(a => {
    const div = document.createElement('div');
    div.className = 'hd-item' + (currentVal === a ? ' selected' : '');
    div.dataset.value = a;
    div.textContent = a;
    div.onclick = () => selectHD('filterAuthor', a, a, 'triggerAuthor', 'menuAuthor');
    menu.appendChild(div);
  });

  const dl = document.getElementById('mAuthorList');
  dl.innerHTML = authors.map(a => `<option value="${a}">`).join('');
}

function renderSourceBars() {
  const counts = { 'Kuku FM': 0, 'Kindle Unlimited': 0, 'Pushtaka Digital Media': 0, 'Book': 0 };
  books.forEach(b => { if (counts[b.source] !== undefined) counts[b.source]++; });
  const max = Math.max(...Object.values(counts));
  const colors = { 'Kuku FM': '#4ade80', 'Kindle Unlimited': '#60a5fa', 'Pushtaka Digital Media': '#c084fc', 'Book': '#fb923c' };
  document.getElementById('sourceBars').innerHTML = Object.entries(counts).map(([src, cnt]) =>
    `<div class="source-bar" style="height:${Math.round(cnt / max * 36) + 4}px;background:${colors[src]};opacity:.7;" title="${src}: ${cnt}"></div>`
  ).join('');
}

function sourceDotClass(source) {
  if (source.includes('Kuku'))    return 'dot-kuku';
  if (source.includes('Kindle'))  return 'dot-kindle';
  if (source.includes('Pushtaka') || source.includes('Pustaka')) return 'dot-pustaka';
  if (source === 'Book')          return 'dot-book';
  return 'dot-other';
}

// ── Filtering / Sorting ──
function applyFilters() {
  const search    = document.getElementById('globalSearch').value.toLowerCase();
  const author    = document.getElementById('filterAuthor').value;
  const source    = document.getElementById('filterSource').value;
  const status    = document.getElementById('filterStatus').value;
  const featuring = document.getElementById('filterFeaturing').value.toLowerCase();

  filtered = books.filter(b => {
    if (author    && b.author !== author) return false;
    if (source    && !b.source.includes(source.split(' ')[0])) return false;
    if (status    && b.status !== status) return false;
    if (featuring && !(b.featuring || '').toLowerCase().includes(featuring)) return false;
    if (search    && !(b.title.toLowerCase().includes(search) ||
                       b.author.toLowerCase().includes(search) ||
                       (b.featuring || '').toLowerCase().includes(search))) return false;
    return true;
  });

  if (sortKey) {
    filtered.sort((a, b) => {
      const av = (a[sortKey] || '').toLowerCase();
      const bv = (b[sortKey] || '').toLowerCase();
      return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
    });
  }

  currentPage = 1;
  document.getElementById('resultCount').textContent = filtered.length;
  document.getElementById('statTotal').textContent    = books.length;
  document.getElementById('statAuthors').textContent  = new Set(books.map(b => b.author)).size;
  document.getElementById('statFinished').textContent = books.filter(b => b.status === 'Finished').length;

  renderTable();
  renderPagination();
}

function sortTable(key) {
  if (sortKey === key) sortAsc = !sortAsc;
  else { sortKey = key; sortAsc = true; }
  document.querySelectorAll('th[id^="th-"]').forEach(th => th.classList.remove('sorted'));
  const th = document.getElementById('th-' + key);
  if (th) {
    th.classList.add('sorted');
    th.querySelector('.sort-icon').textContent = sortAsc ? '↑' : '↓';
  }
  applyFilters();
}

function renderTable() {
  const perPage = parseInt(document.getElementById('perPage').value);
  const start   = (currentPage - 1) * perPage;
  const page    = filtered.slice(start, start + perPage);
  const tbody   = document.getElementById('tableBody');

  if (!page.length) {
    tbody.innerHTML = `<tr><td colspan="7"><div class="no-results">
      <i class="fas fa-search"></i>No books found matching your filters.</div></td></tr>`;
    return;
  }

  tbody.innerHTML = page.map((b, i) => `
    <tr>
      <td style="color:var(--muted);font-size:12px;">${start + i + 1}</td>
      <td class="title-cell"><div class="title-text">${escHtml(b.title)}</div></td>
      <td style="color:var(--text);font-size:13px;">${escHtml(b.author)}</td>
      <td>
        <div class="source-pill">
          <div class="source-dot ${sourceDotClass(b.source)}"></div>
          ${escHtml(b.source)}
        </div>
      </td>
      <td><span class="badge ${b.status === 'Finished' ? 'badge-finished' : 'badge-reading'}">${escHtml(b.status)}</span></td>
      <td>${b.featuring
        ? `<span class="featuring-text">${escHtml(b.featuring)}</span>`
        : `<span class="featuring-none">—</span>`}</td>
      <td class="action-cell">
        <button class="btn-row-edit" onclick="openEditModal(${b.id})"><i class="fas fa-pen"></i> Edit</button>
        <button class="btn-row-del"  onclick="deleteBook(${b.id})"><i class="fas fa-trash"></i></button>
      </td>
    </tr>`).join('');
}

function escHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderPagination() {
  const perPage = parseInt(document.getElementById('perPage').value);
  const total   = Math.ceil(filtered.length / perPage);
  document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${total || 1}`;

  const container = document.getElementById('pageBtns');
  let html = `<button class="page-btn" onclick="goPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>‹ Prev</button>`;

  let pages = [];
  if (total <= 7) { for (let i = 1; i <= total; i++) pages.push(i); }
  else {
    pages = [1];
    if (currentPage > 3) pages.push('…');
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(total - 1, currentPage + 1); i++) pages.push(i);
    if (currentPage < total - 2) pages.push('…');
    pages.push(total);
  }

  pages.forEach(p => {
    if (p === '…') html += `<span class="page-btn" style="cursor:default;">…</span>`;
    else html += `<button class="page-btn ${p === currentPage ? 'active' : ''}" onclick="goPage(${p})">${p}</button>`;
  });

  html += `<button class="page-btn" onclick="goPage(${currentPage + 1})" ${currentPage === total || total === 0 ? 'disabled' : ''}>Next ›</button>`;
  container.innerHTML = html;
}

function goPage(p) {
  const perPage = parseInt(document.getElementById('perPage').value);
  const total   = Math.ceil(filtered.length / perPage);
  if (p < 1 || p > total) return;
  currentPage = p;
  renderTable();
  renderPagination();
}

function clearFilters() {
  document.getElementById('globalSearch').value = '';
  resetHD('filterAuthor', 'All Authors', 'triggerAuthor', 'menuAuthor');
  resetHD('filterSource', 'All Sources', 'triggerSource', 'menuSource');
  resetHD('filterStatus', 'All Status',  'triggerStatus', 'menuStatus');
  document.getElementById('filterFeaturing').value = '';
  sortKey = ''; sortAsc = true;
  document.querySelectorAll('th[id^="th-"]').forEach(th => {
    th.classList.remove('sorted');
    th.querySelector('.sort-icon').textContent = '⇅';
  });
  applyFilters();
}

// ── CRUD ──
function openAddModal() {
  editId = null;
  document.getElementById('modalTitle').textContent = 'Add Book';
  document.getElementById('mTitle').value     = '';
  document.getElementById('mAuthor').value    = '';
  document.getElementById('mSource').value    = 'Kuku FM';
  document.getElementById('mStatus').value    = 'Finished';
  document.getElementById('mFeaturing').value = '';
  document.getElementById('modalOverlay').classList.add('open');
  document.getElementById('mTitle').focus();
}

function openEditModal(id) {
  const b = books.find(b => b.id === id);
  if (!b) return;
  editId = id;
  document.getElementById('modalTitle').textContent = 'Edit Book';
  document.getElementById('mTitle').value     = b.title;
  document.getElementById('mAuthor').value    = b.author;
  document.getElementById('mSource').value    = b.source;
  document.getElementById('mStatus').value    = b.status;
  document.getElementById('mFeaturing').value = b.featuring || '';
  document.getElementById('modalOverlay').classList.add('open');
  document.getElementById('mTitle').focus();
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

function handleOverlayClick(e) {
  if (e.target === document.getElementById('modalOverlay')) closeModal();
}

async function saveBook() {
  const title     = document.getElementById('mTitle').value.trim();
  const author    = document.getElementById('mAuthor').value.trim();
  const source    = document.getElementById('mSource').value;
  const status    = document.getElementById('mStatus').value;
  const featuring = document.getElementById('mFeaturing').value.trim();

  if (!title || !author) { alert('Title and Author are required.'); return; }

  const payload = { title, author, source, status, featuring };

  try {
    if (editId === null) {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const newBook = await res.json();
      books.push(newBook);
    } else {
      const res = await fetch(`${API}/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const updated = await res.json();
      const idx = books.findIndex(b => b.id === editId);
      if (idx !== -1) books[idx] = updated;
    }

    rebuildAuthorDropdown();
    renderSourceBars();
    applyFilters();
    closeModal();
  } catch (e) {
    alert('Error saving book. Check that api.py is running.');
  }
}

async function deleteBook(id) {
  const b = books.find(b => b.id === id);
  if (!b || !confirm(`Delete "${b.title}"?`)) return;

  try {
    await fetch(`${API}/${id}`, { method: 'DELETE' });
    books = books.filter(b => b.id !== id);
    rebuildAuthorDropdown();
    renderSourceBars();
    applyFilters();
  } catch (e) {
    alert('Error deleting book. Check that api.py is running.');
  }
}

init();

// ── Theme ──
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('booksTheme', theme);
  document.querySelectorAll('.theme-swatch').forEach(s => s.classList.remove('active'));
  const active = document.getElementById('swatch-' + theme);
  if (active) active.classList.add('active');
}

function openThemePicker() {
  document.getElementById('themeModalOverlay').classList.add('open');
}

function handleThemeOverlay(e) {
  if (e.target === document.getElementById('themeModalOverlay'))
    document.getElementById('themeModalOverlay').classList.remove('open');
}

// Load saved theme on startup
(function () {
  const saved = localStorage.getItem('booksTheme') || 'orange';
  setTheme(saved);
})();

// ── AI Chat ──
let chatHistory = [];
let chatOpen = false;

function toggleChat() {
  chatOpen = !chatOpen;
  document.getElementById('chatPanel').classList.toggle('open', chatOpen);
  document.getElementById('chatOverlay').classList.toggle('open', chatOpen);
  if (chatOpen) document.getElementById('chatInput').focus();
}

function appendBubble(role, text) {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-bubble ${role}`;
  const content = document.createElement('div');
  content.className = 'bubble-content';
  if (role === 'ai') {
    content.classList.add('markdown');
    content.innerHTML = marked.parse(text);
  } else {
    content.textContent = text;
  }
  div.appendChild(content);
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

function appendTyping() {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-bubble ai chat-typing';
  div.id = 'typingIndicator';
  div.innerHTML = `<div class="bubble-content">Thinking...</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.querySelector('.chat-send');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  input.disabled = true;
  sendBtn.disabled = true;

  appendBubble('user', message);
  appendTyping();

  chatHistory.push({ role: 'user', content: message });

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: chatHistory.slice(0, -1) })
    });
    const data = await res.json();
    removeTyping();

    if (data.error) {
      appendBubble('ai', `Error: ${data.error}`);
    } else {
      const reply = data.response || 'No response received.';
      chatHistory.push({ role: 'assistant', content: reply });
      appendBubble('ai', reply);
    }
  } catch (e) {
    removeTyping();
    appendBubble('ai', `Error: ${e.message}. Make sure api.py is running.`);
  }

  input.disabled = false;
  sendBtn.disabled = false;
  input.focus();
}
