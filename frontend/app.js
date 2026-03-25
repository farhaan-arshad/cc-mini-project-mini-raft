// WebSocket client + drawing logic
// --- Canvas Setup ---
const canvas = document.getElementById("drawingCanvas");
const ctx = canvas.getContext("2d");

const colorPicker = document.getElementById("colorPicker");
const brushSize = document.getElementById("brushSize");
const clearBtn = document.getElementById("clearBtn");
const connectionStatus = document.getElementById("connectionStatus");
const leaderStatus = document.getElementById("leaderStatus");

// Resize canvas to fill available space
function resizeCanvas() {
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

// --- Drawing State ---
let isDrawing = false;
let lastX = 0;
let lastY = 0;

// --- WebSocket ---
const GATEWAY_URL = "ws://localhost:8000/ws";
let socket = null;

function connect() {
  socket = new WebSocket(GATEWAY_URL);

  socket.onopen = () => {
    console.log("[WS] Connected to gateway");
    setStatus("connected", "Connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "stroke") {
      drawStroke(data.x1, data.y1, data.x2, data.y2, data.color, data.width);
    }

    if (data.type === "leader_info") {
      leaderStatus.textContent = `Leader: ${data.leader_id}`;
    }

    if (data.type === "clear") {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  socket.onclose = () => {
    console.log("[WS] Disconnected. Retrying in 2s...");
    setStatus("disconnected", "Disconnected");
    leaderStatus.textContent = "Leader: Unknown";
    leaderStatus.className = "badge neutral";
    setTimeout(connect, 2000);
  };

  socket.onerror = (err) => {
    console.error("[WS] Error:", err);
    socket.close();
  };
}

function setStatus(state, label) {
  connectionStatus.textContent = label;
  connectionStatus.className = `badge ${state}`;
}

// --- Send Stroke to Gateway ---
function sendStroke(x1, y1, x2, y2) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({
    type: "stroke",
    x1, y1, x2, y2,
    color: colorPicker.value,
    width: parseInt(brushSize.value),
  }));
}

// --- Draw on Canvas ---
function drawStroke(x1, y1, x2, y2, color, width) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.stroke();
}

// --- Mouse Events ---
canvas.addEventListener("mousedown", (e) => {
  isDrawing = true;
  [lastX, lastY] = [e.offsetX, e.offsetY];
});

canvas.addEventListener("mousemove", (e) => {
  if (!isDrawing) return;
  const x2 = e.offsetX;
  const y2 = e.offsetY;
  drawStroke(lastX, lastY, x2, y2, colorPicker.value, parseInt(brushSize.value));
  sendStroke(lastX, lastY, x2, y2);
  [lastX, lastY] = [x2, y2];
});

canvas.addEventListener("mouseup", () => { isDrawing = false; });
canvas.addEventListener("mouseleave", () => { isDrawing = false; });

// --- Touch Events (mobile support) ---
canvas.addEventListener("touchstart", (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();
  isDrawing = true;
  lastX = touch.clientX - rect.left;
  lastY = touch.clientY - rect.top;
});

canvas.addEventListener("touchmove", (e) => {
  e.preventDefault();
  if (!isDrawing) return;
  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();
  const x2 = touch.clientX - rect.left;
  const y2 = touch.clientY - rect.top;
  drawStroke(lastX, lastY, x2, y2, colorPicker.value, parseInt(brushSize.value));
  sendStroke(lastX, lastY, x2, y2);
  lastX = x2;
  lastY = y2;
});

canvas.addEventListener("touchend", () => { isDrawing = false; });

// --- Clear Button ---
clearBtn.addEventListener("click", () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "clear" }));
  }
});

// --- Start ---
connect();