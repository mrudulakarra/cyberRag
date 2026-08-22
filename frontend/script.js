/**
 * CyberRAG — Cybersecurity Assistance Chatbot
 * Vanilla JavaScript Single-Page App Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    initCanvasAnimation();
    checkSystemStatus();
    loadKnowledgeBaseDocs();
});

// --- NAVIGATION & ROUTER ---
function navigateTo(viewName) {
    const landingView = document.getElementById("landing-view");
    const chatView = document.getElementById("chat-view");

    if (viewName === "chat") {
        landingView.classList.remove("active");
        chatView.classList.add("active");
        window.scrollTo(0, 0);
        document.getElementById("chat-input").focus();
    } else {
        chatView.classList.remove("active");
        landingView.classList.add("active");
        window.scrollTo(0, 0);
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.querySelector(".sidebar-backdrop");
    sidebar.classList.toggle("open");
    if (backdrop) backdrop.classList.toggle("show");
}

// --- SYSTEM HEALTH & API STATS ---
async function checkSystemStatus() {
    const dot = document.getElementById("system-status-dot");
    const text = document.getElementById("system-status-text");
    const subtext = document.getElementById("system-status-subtext");
    const statChunks = document.getElementById("stat-chunks");
    const statDocs = document.getElementById("stat-docs");
    const statModel = document.getElementById("stat-model");

    try {
        const response = await fetch("/api/health");
        if (!response.ok) throw new Error("Backend unavailable");
        
        const data = await response.json();
        
        if (dot) dot.classList.remove("offline");
        if (text) text.innerText = "System Online";
        
        const modelName = data.model_name || "Gemini 3.6";
        const geminiStatus = data.gemini_configured ? `${modelName} Active` : "Offline Demo Mode";
        const chunkCount = data.vector_db?.total_chunks || 0;
        const docCount = data.vector_db?.unique_documents || 0;

        if (subtext) subtext.innerText = `ChromaDB (${chunkCount} chunks) • ${geminiStatus}`;
        if (statChunks) statChunks.innerText = chunkCount;
        if (statDocs) statDocs.innerText = docCount;
        if (statModel) statModel.innerText = modelName.replace("gemini-", "Gemini ").replace("-flash", "");

    } catch (err) {
        if (dot) dot.classList.add("offline");
        if (text) text.innerText = "Backend Offline";
        if (subtext) subtext.innerText = "FastAPI server disconnected";
        if (statChunks) statChunks.innerText = "0";
        if (statDocs) statDocs.innerText = "0";
    }
}

// --- KNOWLEDGE BASE MANAGEMENT ---
async function loadKnowledgeBaseDocs() {
    const container = document.getElementById("kb-files-list");
    if (!container) return;

    try {
        const response = await fetch("/api/documents");
        const data = await response.json();

        if (!data.files || data.files.length === 0) {
            container.innerHTML = `<div class="kb-loading">No documents found in knowledge base.</div>`;
            return;
        }

        container.innerHTML = data.files.map(file => {
            const kbSizeKb = Math.round(file.size_bytes / 1024);
            return `
                <div class="kb-file-item">
                    <div class="file-name">
                        <span class="file-ext">${file.extension}</span>
                        <span>${file.name}</span>
                    </div>
                    <span class="file-size">${kbSizeKb} KB</span>
                </div>
            `;
        }).join("");

    } catch (e) {
        container.innerHTML = `<div class="kb-loading" style="color:var(--accent-red)">Failed to load documents list.</div>`;
    }
}

function handleFileSelected(event) {
    const file = event.target.files[0];
    if (file) uploadFile(file);
}

async function uploadFile(file) {
    const statusDiv = document.getElementById("upload-status");
    if (!statusDiv) return;

    statusDiv.innerHTML = `<span style="color:var(--accent-cyan)">Uploading & indexing ${file.name}...</span>`;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Upload failed");

        statusDiv.innerHTML = `<span style="color:var(--accent-emerald)">✓ ${data.message} (${data.chunks_added} chunks added)</span>`;
        loadKnowledgeBaseDocs();
        checkSystemStatus();

    } catch (err) {
        statusDiv.innerHTML = `<span style="color:var(--accent-red)">✕ Upload failed: ${err.message}</span>`;
    }
}

// --- CHAT INTERACTION LOGIC ---

function sendQuickQuestion(questionText) {
    navigateTo('chat');
    const input = document.getElementById("chat-input");
    input.value = questionText;
    autoResizeTextarea(input);
    document.getElementById("chat-form").dispatchEvent(new Event("submit"));
}

function startNewChat() {
    const messagesContainer = document.getElementById("chat-messages");
    messagesContainer.innerHTML = `
        <div class="chat-welcome" id="chat-welcome">
            <div class="welcome-icon">
                <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="1.5" fill="none">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="M12 8v4"/>
                    <path d="M12 16h.01"/>
                </svg>
            </div>
            <h2>Welcome to CyberRAG</h2>
            <p>Your grounded cybersecurity learning assistant. Ask any question to retrieve knowledge chunks and generate student-friendly explanations.</p>
            <div class="welcome-cards">
                <div class="welcome-card" onclick="sendQuickQuestion('What is SQL Injection and how can developers prevent it?')">
                    <span class="wc-icon">🛡️</span>
                    <h4>What is SQL Injection?</h4>
                    <p>Learn mechanics, impact, and prepared statements defense.</p>
                </div>
                <div class="welcome-card" onclick="sendQuickQuestion('Explain the 3-way handshake of TCP step by step.')">
                    <span class="wc-icon">🌐</span>
                    <h4>TCP 3-Way Handshake</h4>
                    <p>SYN, SYN-ACK, and ACK sequence explained.</p>
                </div>
                <div class="welcome-card" onclick="sendQuickQuestion('What is OS Credential Dumping in MITRE ATT&CK?')">
                    <span class="wc-icon">⚔️</span>
                    <h4>LSASS Credential Dumping</h4>
                    <p>Mimikatz techniques, sub-techniques, and mitigations.</p>
                </div>
                <div class="welcome-card" onclick="sendQuickQuestion('What are the four phases of NIST Incident Response?')">
                    <span class="wc-icon">🚨</span>
                    <h4>Incident Response Lifecycle</h4>
                    <p>Preparation, Detection, Containment, and Post-Incident.</p>
                </div>
            </div>
        </div>
    `;
}

function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    }
}

function autoResizeTextarea(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 140) + "px";
}

async function handleChatSubmit(event) {
    event.preventDefault();
    const input = document.getElementById("chat-input");
    const question = input.value.trim();
    if (!question) return;

    // Clear input
    input.value = "";
    autoResizeTextarea(input);

    // Hide welcome screen if present
    const welcome = document.getElementById("chat-welcome");
    if (welcome) welcome.remove();

    // Append User Bubble
    appendUserMessage(question);

    // Show Typing Indicator
    showTypingIndicator("Searching cybersecurity vector store...");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });

        hideTypingIndicator();

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            appendBotErrorMessage(errData.detail || "CyberRAG backend is currently unavailable.");
            return;
        }

        const data = await response.json();
        appendBotMessage(data);

    } catch (error) {
        hideTypingIndicator();
        appendBotErrorMessage("CyberRAG backend is currently unavailable. Please verify the FastAPI server is running.");
    }
}

function appendUserMessage(text) {
    const container = document.getElementById("chat-messages");
    const row = document.createElement("div");
    row.className = "chat-row user-row";
    row.innerHTML = `
        <div class="avatar">You</div>
        <div class="bubble">${escapeHtml(text)}</div>
    `;
    container.appendChild(row);
    scrollToBottom();
}

function appendBotErrorMessage(errorText) {
    const container = document.getElementById("chat-messages");
    const row = document.createElement("div");
    row.className = "chat-row bot-row";
    row.innerHTML = `
        <div class="avatar">CR</div>
        <div class="bubble" style="border-color:var(--accent-red)">
            <p style="color:var(--accent-red); font-weight:600;">⚠️ CyberRAG Notice</p>
            <p>${escapeHtml(errorText)}</p>
        </div>
    `;
    container.appendChild(row);
    scrollToBottom();
}

function appendBotMessage(data) {
    const container = document.getElementById("chat-messages");
    const row = document.createElement("div");
    row.className = "chat-row bot-row";

    const formattedAnswer = renderMarkdown(data.answer);
    const stepsHtml = renderTransparencySteps(data.transparency_steps, data.elapsed_seconds);
    const sourcesHtml = renderSourcesDrawer(data.sources);

    row.innerHTML = `
        <div class="avatar">CR</div>
        <div class="bubble">
            <div class="bot-answer-text">${formattedAnswer}</div>
            ${stepsHtml}
            ${sourcesHtml}
        </div>
    `;

    container.appendChild(row);
    scrollToBottom();
}

function renderTransparencySteps(steps, elapsedSec) {
    if (!steps || steps.length === 0) return "";

    const id = "trans-" + Math.random().toString(36).substring(2, 7);
    const stepItems = steps.map(s => `
        <div class="step-item">
            <span class="step-check">[✓]</span>
            <div class="step-info">
                <span class="step-title-text">${escapeHtml(s.title)}</span>
                <span class="step-detail-text">${escapeHtml(s.detail)}</span>
            </div>
        </div>
    `).join("");

    return `
        <div class="transparency-drawer">
            <div class="transparency-header" onclick="toggleDrawer('${id}')">
                <span>⚡ RAG Pipeline Execution (${elapsedSec || 0.5}s)</span>
                <span id="icon-${id}">▼</span>
            </div>
            <div class="transparency-content" id="${id}" style="display:none;">
                ${stepItems}
            </div>
        </div>
    `;
}

function renderSourcesDrawer(sources) {
    if (!sources || sources.length === 0) return "";

    const id = "src-" + Math.random().toString(36).substring(2, 7);
    const sourceCards = sources.map(src => `
        <div class="source-card">
            <div class="source-meta">
                <span class="source-doc">📄 ${escapeHtml(src.source)} (${escapeHtml(src.page)})</span>
                <span class="source-score">${src.score_pct}% Match</span>
            </div>
            <div class="source-snippet">"${escapeHtml(src.text_snippet)}"</div>
        </div>
    `).join("");

    return `
        <div class="sources-drawer">
            <div class="sources-header" onclick="toggleDrawer('${id}')">
                <span>📚 Retrieved Knowledge Sources (${sources.length} Chunks)</span>
                <span id="icon-${id}">▼</span>
            </div>
            <div class="sources-content" id="${id}" style="display:none;">
                ${sourceCards}
            </div>
        </div>
    `;
}

function toggleDrawer(id) {
    const el = document.getElementById(id);
    const icon = document.getElementById("icon-" + id);
    if (!el) return;

    if (el.style.display === "none") {
        el.style.display = "flex";
        if (icon) icon.innerText = "▲";
    } else {
        el.style.display = "none";
        if (icon) icon.innerText = "▼";
    }
}

function showTypingIndicator(text) {
    const indicator = document.getElementById("typing-indicator");
    const label = document.getElementById("typing-text");
    if (label) label.innerText = text || "Processing query...";
    if (indicator) indicator.style.display = "flex";
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) indicator.style.display = "none";
}

function scrollToBottom() {
    const container = document.getElementById("chat-messages");
    if (container) {
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 50);
    }
}

// --- HELPER MARKDOWN PARSER ---
function renderMarkdown(text) {
    if (!text) return "";

    let html = escapeHtml(text);

    // Code blocks ```lang ... ```
    html = html.replace(/```([\s\S]*?)```/g, (match, p1) => {
        return `<pre><code>${p1.trim()}</code></pre>`;
    });

    // Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Blockquotes
    html = html.replace(/^&gt;\s?(.*$)/gim, '<blockquote style="border-left:3px solid var(--accent-cyan); padding-left:0.75rem; color:var(--text-secondary); margin:0.5rem 0;">$1</blockquote>');

    // Line breaks to paragraphs
    const paragraphs = html.split(/\n\n+/);
    return paragraphs.map(p => {
        p = p.trim();
        if (p.startsWith('<h') || p.startsWith('<pre') || p.startsWith('<block')) return p;
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join("");
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// --- CYBER CANVAS ANIMATION ---
function initCanvasAnimation() {
    const canvas = document.getElementById("cyber-canvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = Math.min(Math.floor(width / 20), 65);

    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            radius: Math.random() * 2 + 1,
            color: Math.random() > 0.5 ? "rgba(0, 240, 255, " : "rgba(0, 255, 157, "
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color + "0.6)";
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    const alpha = (1 - dist / 130) * 0.18;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = p.color + alpha + ")";
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
}
