const video = document.getElementById("video");
const statusDiv = document.getElementById("status");
const protocol = location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${location.host}/ws`);

let pc;
let myViewerId = null;   // assigned by server on register_viewer
let torchOn = false;

// ── WebSocket helpers ─────────────────────────────────────────────────────────

function sendControl(action, value) {
    ws.send(JSON.stringify({ type: "camera_control", action, value }));
}

// ── Peer connection ───────────────────────────────────────────────────────────

function createPeerConnection() {
    if (pc) pc.close();

    pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    pc.oniceconnectionstatechange = () => {
        console.log("ICE State:", pc.iceConnectionState);
        if (pc.iceConnectionState === "connected") {
            statusDiv.style.display = "none";
        } else if (pc.iceConnectionState === "disconnected" || pc.iceConnectionState === "failed") {
            statusDiv.style.display = "block";
            statusDiv.innerText = "Stream disconnected. Waiting for camera...";
        }
    };

    pc.ontrack = (event) => {
        console.log("✅ Video track received!");
        video.srcObject = event.streams[0];

        // Ultra-low latency: minimise jitter buffer
        if (event.receiver && "playoutDelayHint" in event.receiver) {
            event.receiver.playoutDelayHint = 0;
        }

        video.onloadedmetadata = () => {
            video.play().catch(e => console.error("Autoplay prevented:", e));
        };
    };

    pc.onicecandidate = (event) => {
        if (event.candidate && myViewerId) {
            // Always include our viewer_id so sender routes ICE to the right PC
            ws.send(JSON.stringify({
                type: "ice",
                viewer_id: myViewerId,
                data: event.candidate
            }));
        }
    };
}

// ── WebSocket events ──────────────────────────────────────────────────────────

ws.onopen = () => {
    console.log("WebSocket connected. Registering as viewer.");
    ws.send(JSON.stringify({ type: "register_viewer" }));
    // Do NOT send viewer_ready — server sends viewer_joined to sender automatically
};

ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);

    if (message.type === "ping") {
        ws.send(JSON.stringify({ type: "pong" }));
        return;
    }

    if (message.type === "rejected") {
        statusDiv.style.display = "block";
        statusDiv.innerText = message.message || "Maximum viewers reached. Try again later.";
        return;
    }

    if (message.type === "viewer_registered") {
        // Server assigned us a viewer ID — include it in all future messages
        myViewerId = message.viewer_id;
        console.log("Registered as viewer:", myViewerId);
        return;
    }

    if (message.type === "timeout") {
        statusDiv.style.display = "block";
        statusDiv.innerText = message.message || "Connection timed out.";
        return;
    }

    if (message.type === "offer") {
        console.log("Received Offer, sending Answer...");
        statusDiv.innerText = "Connecting...";

        createPeerConnection();
        await pc.setRemoteDescription(message.data);

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        // Always include viewer_id so sender routes the answer to the right PC
        ws.send(JSON.stringify({
            type: "answer",
            viewer_id: myViewerId,
            data: answer
        }));
        return;
    }

    if (message.type === "ice" && pc) {
        try {
            await pc.addIceCandidate(message.data);
        } catch (e) { console.error("Error adding ICE candidate:", e); }
        return;
    }
};

// ── Power optimisation: pause video when tab is hidden ────────────────────────

document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        video.pause();
    } else {
        video.play().catch(() => {});
    }
});

// ── PC Remote Control wiring ──────────────────────────────────────────────────

document.getElementById("btn-flip").addEventListener("click", () => {
    sendControl("flip", null);
});

document.getElementById("btn-torch").addEventListener("click", () => {
    torchOn = !torchOn;
    const btn = document.getElementById("btn-torch");
    btn.textContent = torchOn ? "🔦 Torch: ON" : "🔦 Torch: OFF";
    btn.classList.toggle("active", torchOn);
    sendControl("torch", torchOn);
});

document.getElementById("zoom-slider").addEventListener("input", (e) => {
    document.getElementById("zoom-value").textContent = parseFloat(e.target.value).toFixed(1) + "×";
    sendControl("zoom", parseFloat(e.target.value));
});

document.getElementById("exposure-slider").addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    document.getElementById("exposure-value").textContent = (val >= 0 ? "+" : "") + val.toFixed(1);
    sendControl("exposure", val);
});

document.getElementById("res-select").addEventListener("change", (e) => {
    sendControl("resolution", e.target.value);
});

document.getElementById("fps-select").addEventListener("change", (e) => {
    sendControl("fps", parseInt(e.target.value, 10));
});