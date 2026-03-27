// ── Config ──
const GATEWAY_URL = "ws://localhost:8000/ws";

// ── Canvas ──
const canvas = document.getElementById("drawingCanvas");
const ctx    = canvas.getContext("2d");
let isDrawing = false;
let lastX = 0, lastY = 0;
let currentColor = "#f0f0f0";
let currentSize  = 4;
let isEraser     = false;
let strokeCount  = 0;

function resizeCanvas() {
  const wrap = canvas.parentElement;
  canvas.width  = wrap.offsetWidth;
  canvas.height = wrap.offsetHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

// ── WebSocket ──
let socket = null;

function connect() {
  socket = new WebSocket(GATEWAY_URL);

  socket.onopen = () => {
    setConnected(true);
    toast("Connected to RAFT cluster", "success");
    pollLeader();
  };

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === "stroke") {
      drawStroke(data.x1, data.y1, data.x2, data.y2, data.color, data.width);
    }
    if (data.type === "leader_info") {
      updateLeader(data.leader_id);
    }
    if (data.type === "clear") {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      toast("Canvas cleared", "info");
    }
  };

  socket.onclose = () => {
    setConnected(false);
    toast("Disconnected — retrying...", "error");
    setTimeout(connect, 2000);
  };

  socket.onerror = () => socket.close();
}

// ── Draw ──
function drawStroke(x1, y1, x2, y2, color, width) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = color;
  ctx.lineWidth   = width;
  ctx.lineCap     = "round";
  ctx.lineJoin    = "round";
  ctx.stroke();
}

function sendStroke(x1, y1, x2, y2) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({
    type: "stroke",
    x1, y1, x2, y2,
    color: isEraser ? "#0a0c10" : currentColor,
    width: isEraser ? currentSize * 3 : currentSize,
  }));
  strokeCount++;
  document.getElementById("strokeCount").textContent = strokeCount;
}

// ── Mouse events ──
canvas.addEventListener("mousedown", (e) => {
  isDrawing = true;
  [lastX, lastY] = [e.offsetX, e.offsetY];
});

canvas.addEventListener("mousemove", (e) => {
  moveCursorLabel(e.offsetX, e.offsetY);
  if (!isDrawing) return;
  const x2 = e.offsetX, y2 = e.offsetY;
  drawStroke(lastX, lastY, x2, y2,
    isEraser ? "#0a0c10" : currentColor,
    isEraser ? currentSize * 3 : currentSize
  );
  sendStroke(lastX, lastY, x2, y2);
  [lastX, lastY] = [x2, y2];
});

canvas.addEventListener("mouseup",    () => { isDrawing = false; });
canvas.addEventListener("mouseleave", () => {
  isDrawing = false;
  hideCursorLabel();
});
canvas.addEventListener("mouseenter", () => showCursorLabel());

// ── Touch events ──
canvas.addEventListener("touchstart", (e) => {
  e.preventDefault();
  const t = e.touches[0], r = canvas.getBoundingClientRect();
  isDrawing = true;
  lastX = t.clientX - r.left;
  lastY = t.clientY - r.top;
}, { passive: false });

canvas.addEventListener("touchmove", (e) => {
  e.preventDefault();
  if (!isDrawing) return;
  const t = e.touches[0], r = canvas.getBoundingClientRect();
  const x2 = t.clientX - r.left, y2 = t.clientY - r.top;
  drawStroke(lastX, lastY, x2, y2,
    isEraser ? "#0a0c10" : currentColor,
    isEraser ? currentSize * 3 : currentSize
  );
  sendStroke(lastX, lastY, x2, y2);
  lastX = x2; lastY = y2;
}, { passive: false });

canvas.addEventListener("touchend", () => { isDrawing = false; });

// ── Cursor label ──
const cursorLabel = document.getElementById("cursorLabel");

function moveCursorLabel(x, y) {
  cursorLabel.style.left = x + "px";
  cursorLabel.style.top  = y + "px";
}
function showCursorLabel() { cursorLabel.classList.add("visible"); }
function hideCursorLabel() { cursorLabel.classList.remove("visible"); }

// ── Tool buttons ──
const penTool    = document.getElementById("penTool");
const eraserTool = document.getElementById("eraserTool");

penTool.addEventListener("click", () => {
  isEraser = false;
  penTool.classList.add("active");
  eraserTool.classList.remove("active");
  canvas.style.cursor = "crosshair";
  document.getElementById("cursorText").textContent = "You";
});

eraserTool.addEventListener("click", () => {
  isEraser = true;
  eraserTool.classList.add("active");
  penTool.classList.remove("active");
  canvas.style.cursor = "cell";
  document.getElementById("cursorText").textContent = "Eraser";
});

// ── Color swatches ──
document.querySelectorAll(".swatch[data-color]").forEach(btn => {
  btn.addEventListener("click", () => {
    currentColor = btn.dataset.color;
    isEraser = false;
    penTool.classList.add("active");
    eraserTool.classList.remove("active");
    document.querySelectorAll(".swatch").forEach(s => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("colorPicker").value = currentColor;
  });
});

document.getElementById("colorPicker").addEventListener("input", (e) => {
  currentColor = e.target.value;
  isEraser = false;
  penTool.classList.add("active");
  eraserTool.classList.remove("active");
  document.querySelectorAll(".swatch").forEach(s => s.classList.remove("active"));
});

// ── Brush size ──
const brushSlider = document.getElementById("brushSize");
const sizeValue   = document.getElementById("sizeValue");
const sizePreview = document.getElementById("sizePreview");

brushSlider.addEventListener("input", (e) => {
  currentSize = parseInt(e.target.value);
  sizeValue.textContent = currentSize + "px";
  const dot = sizePreview.querySelector("::after");
  sizePreview.style.setProperty("--sz", currentSize + "px");
  // Update pseudo-element via a CSS variable trick
  sizePreview.dataset.size = currentSize;
  const sz = Math.min(currentSize, 20);
  sizePreview.style.cssText = `width:20px;height:20px;display:flex;align-items:center;justify-content:center;`;
  sizePreview.innerHTML = `<span style="width:${sz}px;height:${sz}px;border-radius:50%;background:var(--text2);display:block;transition:all 0.2s"></span>`;
});

// Initialise size preview
sizePreview.innerHTML = `<span style="width:4px;height:4px;border-radius:50%;background:var(--text2);display:block"></span>`;

// ── Clear ──
document.getElementById("clearBtn").addEventListener("click", () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  strokeCount = 0;
  document.getElementById("strokeCount").textContent = "0";
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "clear" }));
  }
  toast("Canvas cleared", "info");
});

// ── Status UI ──
function setConnected(connected) {
  const chip = document.getElementById("statusChip");
  const label = document.getElementById("chipLabel");
  if (connected) {
    chip.classList.add("connected");
    label.textContent = "Connected";
  } else {
    chip.classList.remove("connected");
    label.textContent = "Disconnected";
    document.getElementById("leaderLabel").textContent = "No Leader";
    setNodesDown();
  }
}

function updateLeader(leaderId) {
  document.getElementById("leaderLabel").textContent = leaderId || "No Leader";
  updateNodeUI(leaderId);
}

function updateNodeUI(leaderId) {
  const nodes = {
    "replica1": document.getElementById("node1"),
    "replica2": document.getElementById("node2"),
    "replica3": document.getElementById("node3"),
  };
  Object.entries(nodes).forEach(([id, el]) => {
    el.classList.remove("leader", "follower", "down");
    if (id === leaderId) {
      el.classList.add("leader");
    } else {
      el.classList.add("follower");
    }
  });
  // Pulse animation on leader change
  const pulse = document.getElementById("raftPulse");
  pulse.classList.remove("animate");
  void pulse.offsetWidth;
  pulse.classList.add("animate");
}

function setNodesDown() {
  ["node1","node2","node3"].forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove("leader","follower");
    el.classList.add("down");
  });
}

// ── Poll leader from gateway ──
async function pollLeader() {
  try {
    const res  = await fetch("http://localhost:8000/health");
    const data = await res.json();
    if (data.leader) {
      const parts = data.leader.split("/");
      const id    = parts[parts.length - 1].split(":")[0];
      updateLeader(id);
    }
  } catch (e) {
    // gateway not reachable
  }
  setTimeout(pollLeader, 2000);
}

// ── Toast ──
function toast(msg, type = "info") {
  const container = document.getElementById("toastContainer");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => {
    el.style.animation = "toastOut 0.3s ease forwards";
    setTimeout(() => el.remove(), 300);
  }, 2500);
}

// ── Splash screen ──
const splash     = document.getElementById("splash");
const splashFill = document.getElementById("splashFill");
const splashHint = document.getElementById("splashHint");
const app        = document.getElementById("app");

const hints = [
  "Electing leader...",
  "Syncing log entries...",
  "Establishing quorum...",
  "Connecting replicas...",
  "Ready.",
];

let progress = 0;
let hintIdx  = 0;

const splashInterval = setInterval(() => {
  progress += Math.random() * 22 + 8;
  if (progress > 100) progress = 100;
  splashFill.style.width = progress + "%";

  if (hintIdx < hints.length - 1 && progress > (hintIdx + 1) * 20) {
    hintIdx++;
    splashHint.textContent = hints[hintIdx];
  }

  if (progress >= 100) {
    clearInterval(splashInterval);
    setTimeout(() => {
      splash.classList.add("hidden");
      app.classList.add("visible");
      connect();
    }, 400);
  }
}, 180);