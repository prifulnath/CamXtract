const video = document.getElementById("video");
const protocol = location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${location.host}/ws`);

let pc;
let stream;
let currentFacingMode = "environment";
let isSending = false;

async function initCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: currentFacingMode },
            audio: false
        });
        video.srcObject = stream;
        video.setAttribute("playsinline", "true");
        video.setAttribute("autoplay", "true");
        video.muted = true; // Required for iOS autoplay
        video.onloadedmetadata = () => {
            video.play().catch(e => console.warn(e));
        };
    } catch (error) {
        alert(`Camera error: ${error.name} - ${error.message}`);
    }
}

async function startPeerConnection() {
    if (!stream) return; // Camera not ready
    if (pc) pc.close(); // Close any old connection

    pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    stream.getTracks().forEach(track => pc.addTrack(track, stream));

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            ws.send(JSON.stringify({ type: "ice", data: event.candidate }));
        }
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    ws.send(JSON.stringify({ type: "offer", data: offer }));
}

ws.onopen = () => {
    ws.send(JSON.stringify({ type: "register_sender" }));
};

ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);

    if (message.type === "wait") {
        const overlay = document.getElementById("status-overlay");
        overlay.style.display = "flex";
        overlay.innerText = message.message;

        // Ensure camera shuts off if we are pushed to waiting mode
        if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
        isSending = false;
    }

    if (message.type === "start_sending") {
        document.getElementById("status-overlay").style.display = "none";
        isSending = true;
        initCamera();  // Start the physical camera now that we are the active sender
    }

    // Completely ignore WebRTC negotiations if we are strictly in waiting mode!
    if (!isSending) return;

    if (message.type === "viewer_ready") {
        // Now that the viewer is connected, create & send the offer!
        startPeerConnection();
    }

    if (message.type === "answer" && pc) {
        await pc.setRemoteDescription(message.data);
    }

    if (message.type === "ice" && pc) {
        try {
            await pc.addIceCandidate(message.data);
        } catch (e) { console.error("Error adding ice candidate:", e); }
    }
};

// Flip camera function
document.getElementById("flip-btn").addEventListener("click", async () => {
    if (!isSending) return; // Prevent flipping if we're waiting for access

    currentFacingMode = currentFacingMode === "environment" ? "user" : "environment";

    // Stop existing camera track before requesting a new one
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: currentFacingMode },
            audio: false
        });
        video.srcObject = stream;
        video.setAttribute("playsinline", "true");
        video.setAttribute("autoplay", "true");
        video.muted = true;
        video.onloadedmetadata = () => {
            video.play().catch(e => console.warn(e));
        };

        // If WebRTC is already connected, dynamically swap the video track
        if (pc) {
            const videoSender = pc.getSenders().find(sender => sender.track && sender.track.kind === 'video');
            if (videoSender) {
                videoSender.replaceTrack(stream.getVideoTracks()[0]);
            }
        }
    } catch (error) {
        alert(`Camera error: ${error.name} - ${error.message}`);
    }
});