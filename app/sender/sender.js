// ── State ──────────────────────────────────────────────────────────────────────
const video = document.getElementById("video");
const protocol = location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${location.host}/ws`);

// Detect iOS Safari — resolution constraints crop the sensor on iPhone/iPad
const IS_IOS = /iP(hone|od|ad)/.test(navigator.userAgent) &&
               /WebKit/.test(navigator.userAgent) &&
               !/CriOS|FxiOS/.test(navigator.userAgent);

let peerConnections = new Map(); // viewerId → RTCPeerConnection
let stream;
let currentFacingMode = "environment";
let isSending = false;
let torchOn = false;
let pendingViewers = [];  // viewer IDs that arrived before camera was ready

// Camera config loaded from server
let camConfig = {
    resolution: "1920x1080",
    preferred_fps: 30,
    codec_preference: "VP9",
    use_ideal: true,
    fallback_resolutions: ["1280x720", "854x480"],
    zoom: 1.0,
    exposure_compensation: 0.0,
    torch: false,
    facing_mode: "environment",
    max_bitrate_mbps: 8
};

// ── Config helpers ────────────────────────────────────────────────────────────

async function loadCamConfig() {
    try {
        const res = await fetch("/api/camera-config");
        if (res.ok) {
            camConfig = await res.json();
            currentFacingMode = camConfig.facing_mode || "environment";
            torchOn = camConfig.torch || false;
        }
    } catch (e) {
        console.warn("Could not load camera config, using defaults.", e);
    }
}

async function saveCameraState() {
    try {
        const track = stream?.getVideoTracks()[0];
        const settings = track ? track.getSettings() : {};
        const payload = {
            ...camConfig,
            resolution: settings.width && settings.height
                ? `${settings.width}x${settings.height}`
                : camConfig.resolution,
            preferred_fps: Math.round(settings.frameRate || camConfig.preferred_fps),
            zoom: settings.zoom || camConfig.zoom,
            exposure_compensation: settings.exposureCompensation !== undefined
                ? settings.exposureCompensation
                : camConfig.exposure_compensation,
            torch: torchOn,
            facing_mode: currentFacingMode,
        };
        await fetch("/api/camera-config", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        console.warn("Could not save camera state:", e);
    }
}

// ── getUserMedia constraint builder ───────────────────────────────────────────

function buildConstraints(resStr, fps, useIdeal, facingMode) {
    // 'native' = fully unconstrained — lets camera use its full native resolution/FOV
    if (resStr === "native") {
        return {
            video: { facingMode: facingMode, frameRate: { ideal: fps } },
            audio: false
        };
    }
    const [w, h] = resStr.split("x").map(Number);
    const mode = useIdeal ? "ideal" : "exact";
    return {
        video: {
            width: { [mode]: w },
            height: { [mode]: h },
            frameRate: { ideal: fps },
            facingMode: facingMode
        },
        audio: false
    };
}

// ── Camera initialisation ─────────────────────────────────────────────────────

async function initCamera() {
    await loadCamConfig();

    // iOS Safari: resolution constraints crop the sensor — always use native mode.
    // Desktop / Android: try configured resolution, fall back down the list,
    // final safety net is always unconstrained native.
    const attempts = IS_IOS
        ? ["native"]
        : [camConfig.resolution, ...camConfig.fallback_resolutions, "native"];

    for (const res of attempts) {
        try {
            stream = await navigator.mediaDevices.getUserMedia(
                buildConstraints(res, camConfig.preferred_fps, camConfig.use_ideal, currentFacingMode)
            );
            console.log(`✅ Camera opened: ${res === "native" ? "native (unconstrained)" : res}`);
            break;
        } catch (e) {
            console.warn(`⚠️ ${res} failed (${e.name}), trying next...`);
            stream = null;
        }
    }

    if (!stream) {
        alert("No compatible camera found. Please check camera permissions.");
        return;
    }

    video.srcObject = stream;
    video.setAttribute("playsinline", "true");
    video.setAttribute("autoplay", "true");
    video.muted = true;
    video.onloadedmetadata = () => video.play().catch(e => console.warn(e));

    // Restore persisted controls
    await restorePersistedControls();
}

// ── Restore persisted camera controls ────────────────────────────────────────

async function restorePersistedControls() {
    if (camConfig.zoom && camConfig.zoom > 1.0) {
        applyZoom(camConfig.zoom);
    }
    if (camConfig.torch) {
        await applyTorch(true);
    }
    if (camConfig.exposure_compensation !== undefined && camConfig.exposure_compensation !== 0) {
        await applyExposure(camConfig.exposure_compensation);
    }
}

// ── Camera control implementations ───────────────────────────────────────────

function applyZoom(level) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities ? track.getCapabilities() : {};
    if (caps.zoom) {
        const clamped = Math.min(Math.max(level, caps.zoom.min), caps.zoom.max);
        track.applyConstraints({ advanced: [{ zoom: clamped }] }).catch(console.warn);
        camConfig.zoom = clamped;
        saveCameraState();
    }
}

async function applyTorch(on) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities ? track.getCapabilities() : {};
    if (caps.torch) {
        await track.applyConstraints({ advanced: [{ torch: on }] }).catch(console.warn);
        torchOn = on;
        camConfig.torch = on;
        saveCameraState();
    }
}

async function applyExposure(compensation) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities ? track.getCapabilities() : {};
    if (caps.exposureCompensation) {
        const clamped = Math.min(
            Math.max(compensation, caps.exposureCompensation.min),
            caps.exposureCompensation.max
        );
        await track.applyConstraints({ advanced: [{ exposureCompensation: clamped }] }).catch(console.warn);
        camConfig.exposure_compensation = clamped;
        saveCameraState();
    }
}

async function switchResolution(resStr) {
    const [w, h] = resStr.split("x").map(Number);
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    try {
        await track.applyConstraints({ width: { ideal: w }, height: { ideal: h } });
        camConfig.resolution = resStr;
        // Update the live WebRTC track
        if (pc) {
            const sender = pc.getSenders().find(s => s.track?.kind === "video");
            if (sender) await sender.replaceTrack(stream.getVideoTracks()[0]);
        }
        await saveCameraState();
        console.log(`✅ Resolution switched to: ${resStr}`);
    } catch (e) {
        console.warn("Could not switch resolution:", e);
    }
}

async function switchFps(fps) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    try {
        await track.applyConstraints({ frameRate: { ideal: fps } });
        camConfig.preferred_fps = fps;
        await saveCameraState();
    } catch (e) {
        console.warn("Could not switch FPS:", e);
    }
}

// ── Handle remote camera_control messages from PC ─────────────────────────────

async function handleCameraControl(action, value) {
    switch (action) {
        case "zoom":       applyZoom(value);                   break;
        case "torch":      await applyTorch(value);            break;
        case "exposure":   await applyExposure(value);         break;
        case "resolution": await switchResolution(value);      break;
        case "fps":        await switchFps(value);             break;
        case "flip":       document.getElementById("flip-btn").click(); break;
        default: console.warn("Unknown camera_control action:", action);
    }
}

// ── Codec preference (SDP manipulation) ───────────────────────────────────────

function preferCodec(sdp, codec) {
    const lines = sdp.split("\r\n");
    const mLineIndex = lines.findIndex(l => l.startsWith("m=video"));
    if (mLineIndex < 0) return sdp;

    const codecPayloads = lines
        .filter(l => new RegExp(`a=rtpmap:(\\d+) ${codec}`, "i").test(l))
        .map(l => l.match(/a=rtpmap:(\d+)/)[1]);

    if (codecPayloads.length === 0) return sdp; // Codec not supported, skip

    const mParts = lines[mLineIndex].split(" ");
    const otherPayloads = mParts.slice(3).filter(p => !codecPayloads.includes(p));
    lines[mLineIndex] = [...mParts.slice(0, 3), ...codecPayloads, ...otherPayloads].join(" ");
    return lines.join("\r\n");
}

// ── Bitrate / encoding parameters ────────────────────────────────────────────

async function applyEncodingParams(videoSender) {
    if (!videoSender) return;
    const params = videoSender.getParameters();
    if (!params.encodings || params.encodings.length === 0) {
        params.encodings = [{}];
    }
    const [w] = camConfig.resolution.split("x").map(Number);
    const is4K = w >= 3840;
    const isHD = w >= 1920;
    const maxBps = is4K  ? 20_000_000
                 : isHD  ?  8_000_000
                          :  3_000_000;

    params.encodings[0].maxBitrate = Math.min(maxBps, (camConfig.max_bitrate_mbps || 8) * 1_000_000);
    params.encodings[0].maxFramerate = camConfig.preferred_fps;
    params.encodings[0].priority = "high";

    try {
        await videoSender.setParameters(params);
    } catch (e) {
        console.warn("Could not set encoding params:", e);
    }
}

// ── Adaptive Bitrate loop ─────────────────────────────────────────────────────

function startABRLoop(pc, viewerId) {
    const abr = setInterval(async () => {
        if (!pc || pc.connectionState === "closed" || !peerConnections.has(viewerId)) {
            clearInterval(abr);
            return;
        }
        try {
            const stats = await pc.getStats(null);
            stats.forEach(report => {
                if (report.type !== "outbound-rtp" || report.kind !== "video") return;
                const sender = pc.getSenders().find(s => s.track?.kind === "video");
                if (!sender) return;
                const params = sender.getParameters();
                if (!params.encodings?.length) return;
                const currentMax = params.encodings[0].maxBitrate || 8_000_000;
                // Gently scale bitrate within safe bounds
                const targetBps = Math.min(20_000_000, Math.max(500_000, currentMax));
                params.encodings[0].maxBitrate = targetBps;
                sender.setParameters(params).catch(() => {});
            });
        } catch (e) { /* ignore */ }
    }, 3000);
}

// ── Per-viewer RTCPeerConnection ────────────────────────────────────────────

async function startPeerConnectionForViewer(viewerId) {
    if (!stream) return;

    // Close any existing PC for this viewer
    if (peerConnections.has(viewerId)) {
        peerConnections.get(viewerId).close();
    }

    const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });
    peerConnections.set(viewerId, pc);

    stream.getTracks().forEach(track => pc.addTrack(track, stream));

    // Set RTP priority for all senders
    pc.getSenders().forEach(sender => {
        const params = sender.getParameters();
        if (params.encodings) {
            params.encodings.forEach(enc => { enc.priority = "high"; });
            sender.setParameters(params).catch(() => {});
        }
    });

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            ws.send(JSON.stringify({ type: "ice", data: event.candidate }));
        }
    };

    pc.onicegatheringstatechange = () => {
        console.log("ICE Gathering:", pc.iceGatheringState);
    };

    const offer = await pc.createOffer();

    // Apply codec preference
    const pref = camConfig.codec_preference || "VP9";
    if (pref !== "auto") {
        offer.sdp = preferCodec(offer.sdp, pref);
    }

    await pc.setLocalDescription(offer);

    // Trickle ICE: send the offer immediately — do NOT wait for full gathering
    ws.send(JSON.stringify({ type: "offer", data: pc.localDescription }));

    // Apply encoding params once the sender is wired up
    const videoSender = pc.getSenders().find(s => s.track?.kind === "video");
    await applyEncodingParams(videoSender);

    // Start adaptive bitrate
    startABRLoop(pc);
}

// ── WebSocket events ──────────────────────────────────────────────────────────

ws.onopen = () => {
    ws.send(JSON.stringify({ type: "register_sender" }));
};

ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);

    if (message.type === "ping") {
        ws.send(JSON.stringify({ type: "pong" }));
        return;
    }

    if (message.type === "wait") {
        const overlay = document.getElementById("status-overlay");
        overlay.style.display = "flex";
        overlay.innerText = message.message;
        if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
        isSending = false;
        return;
    }

    if (message.type === "start_sending") {
        document.getElementById("status-overlay").style.display = "none";
        isSending = true;
        await initCamera();

        if (!stream) return; // camera failed even after all fallbacks

        // Standby: low FPS until a viewer connects (saves power)
        const track = stream.getVideoTracks()[0];
        if (track) {
            track.applyConstraints({ frameRate: { max: 5 } }).catch(() => {});
        }

        // Connect any viewers that joined while camera was initialising
        if (pendingViewers.length > 0) {
            const pending = [...pendingViewers];
            pendingViewers = [];
            if (track) {
                track.applyConstraints({ frameRate: { ideal: camConfig.preferred_fps } }).catch(() => {});
            }
            for (const vid of pending) {
                await startPeerConnectionForViewer(vid);
            }
        }
        return;
    }

    if (message.type === "timeout") {
        document.getElementById("status-overlay").style.display = "flex";
        document.getElementById("status-overlay").innerText = message.message || "Connection timed out.";
        return;
    }

    // Ignore signalling if we are not active sender
    if (!isSending) return;

    // ── Multi-viewer events ──────────────────────────────────────────────────

    if (message.type === "viewer_joined") {
        const viewerId = message.viewer_id;
        if (!stream) {
            // Camera not ready yet — queue the viewer
            pendingViewers.push(viewerId);
            return;
        }
        // Restore full FPS (at least one viewer now active)
        const track = stream.getVideoTracks()[0];
        if (track) {
            track.applyConstraints({ frameRate: { ideal: camConfig.preferred_fps } }).catch(() => {});
        }
        await startPeerConnectionForViewer(viewerId);
        return;
    }

    if (message.type === "viewer_left") {
        const viewerId = message.viewer_id;
        const pc = peerConnections.get(viewerId);
        if (pc) { pc.close(); peerConnections.delete(viewerId); }
        // If no more viewers, go to standby FPS
        if (peerConnections.size === 0 && stream) {
            const track = stream.getVideoTracks()[0];
            if (track) track.applyConstraints({ frameRate: { max: 5 } }).catch(() => {});
        }
        return;
    }

    // ── WebRTC signalling — route by viewer_id ───────────────────────────────

    if (message.type === "answer") {
        const pc = peerConnections.get(message.viewer_id);
        if (pc) await pc.setRemoteDescription(message.data);
        return;
    }

    if (message.type === "ice") {
        const pc = peerConnections.get(message.viewer_id);
        if (pc) {
            try { await pc.addIceCandidate(message.data); }
            catch (e) { console.error("ICE error:", e); }
        }
        return;
    }

    if (message.type === "camera_control") {
        await handleCameraControl(message.action, message.value);
        return;
    }
};

document.getElementById("flip-btn").addEventListener("click", async () => {
    if (!isSending) return;

    currentFacingMode = currentFacingMode === "environment" ? "user" : "environment";

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }

    try {
        stream = await navigator.mediaDevices.getUserMedia(
            buildConstraints(
                IS_IOS ? "native" : (camConfig.resolution || "1920x1080"),
                camConfig.preferred_fps,
                camConfig.use_ideal,
                currentFacingMode
            )
        );
        video.srcObject = stream;
        video.setAttribute("playsinline", "true");
        video.setAttribute("autoplay", "true");
        video.muted = true;
        video.onloadedmetadata = () => video.play().catch(e => console.warn(e));

        // Hot-swap track on ALL active peer connections
        const newTrack = stream.getVideoTracks()[0];
        for (const pc of peerConnections.values()) {
            const videoSender = pc.getSenders().find(s => s.track?.kind === "video");
            if (videoSender && newTrack) {
                await videoSender.replaceTrack(newTrack);
            }
        }

        camConfig.facing_mode = currentFacingMode;
        await saveCameraState();
    } catch (error) {
        alert(`Camera error: ${error.name} - ${error.message}`);
    }
});