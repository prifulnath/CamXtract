const video = document.getElementById("video");
const statusDiv = document.getElementById("status");
const protocol = location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${location.host}/ws`);

let pc;

function createPeerConnection() {
    if (pc) pc.close();

    pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    pc.oniceconnectionstatechange = () => {
        console.log("ICE State:", pc.iceConnectionState);
        if (pc.iceConnectionState === "connected") {
            statusDiv.style.display = "none";
        } else if (pc.iceConnectionState === "disconnected") {
            statusDiv.style.display = "block";
            statusDiv.innerText = "Stream disconnected.";
        }
    };

    pc.ontrack = (event) => {
        console.log("Video track received!");
        video.srcObject = event.streams[0];

        // Force play after metadata loads to ensure browser doesn't pause it
        video.onloadedmetadata = () => {
            video.play().catch(e => console.error("Autoplay prevented:", e));
        };
    };

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            ws.send(JSON.stringify({ type: "ice", data: event.candidate }));
        }
    };
}

ws.onopen = () => {
    console.log("WebSocket connected. Registering as viewer.");
    ws.send(JSON.stringify({ type: "register_viewer" }));
    ws.send(JSON.stringify({ type: "viewer_ready" }));
};

ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);

    if (message.type === "offer") {
        console.log("Received Offer, sending Answer...");
        statusDiv.innerText = "Connecting...";

        createPeerConnection();
        await pc.setRemoteDescription(message.data);

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        ws.send(JSON.stringify({ type: "answer", data: answer }));
    }

    if (message.type === "ice" && pc) {
        try {
            await pc.addIceCandidate(message.data);
        } catch (e) { console.error("Error adding ice candidate:", e); }
    }
};