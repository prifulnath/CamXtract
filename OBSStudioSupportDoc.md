# CamXtract → OBS Studio Integration Specification

This document describes how to make **CamXtract** usable as a source inside OBS Studio.
It covers architecture, streaming protocols, implementation steps, and edge cases.

---

# 🎯 Goal

Enable CamXtract to be added as a source in OBS Studio via:

1. Browser Source (Web-based stream)
2. Media Source (RTMP / HLS stream)
3. Virtual Camera (advanced, optional)
4. WebRTC (future enhancement)

---

# 🧩 Supported Integration Methods

## 1️⃣ Browser Source (Recommended - Easiest)

### 📌 How it works

OBS loads a webpage that renders the live stream from CamXtract.

### 🔗 Example URL

```
https://<server-ip>:8000/obs.html
```

### 🛠 Implementation

#### Frontend (`obs.html`)

* Minimal UI (no controls)
* Auto-connect to stream
* Fullscreen video element

```html
<video id="stream" autoplay playsinline></video>

<script>
const ws = new WebSocket("wss://<server-ip>:8000/ws");

ws.onmessage = (event) => {
  // attach stream to video
};
</script>
```

#### Backend (FastAPI)

* WebSocket endpoint:

```
/ws
```

* Sends video frames or WebRTC signaling

---

### ⚙️ OBS Configuration

In OBS Studio:

* Source → Browser
* URL: `https://<server-ip>:8000/obs.html`
* Width: 1280
* Height: 720
* Enable:

  * Shutdown source when not visible ❌
  * Refresh browser when scene becomes active ✅

---

### ✅ Pros

* Easy to implement
* No extra encoding needed
* Works in local network

### ❌ Cons

* Slight latency
* Depends on browser rendering

---

## 2️⃣ RTMP Streaming (Professional Method)

### 📌 How it works

CamXtract pushes stream to an RTMP server, OBS pulls it.

---

### 🛠 Architecture

```
Mobile Sender → CamXtract Server → RTMP Server → OBS Studio
```

---

### 🧰 Setup RTMP Server

Use:

* Nginx + RTMP module

Example config:

```
rtmp {
  server {
    listen 1935;
    chunk_size 4096;

    application live {
      live on;
      record off;
    }
  }
}
```

---

### 📤 CamXtract Push Stream

Use FFmpeg:

```bash
ffmpeg -i input_stream \
  -c:v libx264 \
  -preset veryfast \
  -f flv rtmp://localhost/live/stream
```

---

### 📥 OBS Configuration

* Source → Media Source
* Input:

```
rtmp://<server-ip>/live/stream
```

---

### ✅ Pros

* Low latency
* Industry standard
* High compatibility

### ❌ Cons

* Requires extra server setup
* More complex

---

## 3️⃣ HLS Streaming (Fallback / Compatibility)

### 📌 How it works

CamXtract generates `.m3u8` playlist and `.ts` segments.

---

### 🛠 Implementation

#### Generate HLS via FFmpeg:

```bash
ffmpeg -i input_stream \
  -c:v libx264 \
  -hls_time 2 \
  -hls_list_size 3 \
  -f hls stream.m3u8
```

#### Serve via FastAPI:

```
/hls/stream.m3u8
```

---

### 📥 OBS Usage

* Source → Media Source
* Input:

```
http://<server-ip>:8000/hls/stream.m3u8
```

---

### ✅ Pros

* Stable
* Works over HTTP

### ❌ Cons

* High latency (5–15 sec)

---

## 4️⃣ Virtual Camera (Advanced)

### 📌 How it works

CamXtract acts as a virtual webcam device.

---

### 🛠 Implementation Options

#### Windows:

* Use OBS Virtual Camera plugin OR DirectShow driver

#### Approach:

* Pipe frames → virtual camera device

Tools:

* OBS Virtual Camera
* v4l2loopback (Linux)

---

### 📥 OBS Usage

* Source → Video Capture Device
* Select: "CamXtract Virtual Camera"

---

### ✅ Pros

* Native camera input
* Works in all apps

### ❌ Cons

* Complex to implement
* OS-specific

---

## 🔐 Security Considerations

* Use HTTPS (self-signed allowed for local)
* Token-based stream access:

```
/obs.html?token=abc123
```

* Restrict IP access (local network only)
* Rate limit connections

---

## ⚡ Performance Optimization

* Use hardware encoding (NVENC / VAAPI)
* Reduce resolution for OBS preview
* Adaptive bitrate for unstable networks
* Limit max viewers

---

## 🧪 Testing Checklist

* [ ] Stream loads in browser
* [ ] OBS Browser Source works
* [ ] RTMP stream connects
* [ ] Latency under acceptable range
* [ ] Multiple viewers supported
* [ ] Mobile sender reconnect works

---

## 🚨 Edge Cases

* Self-signed SSL blocking OBS browser
* Mobile switching networks
* Multiple senders conflict
* High CPU usage during encoding
* NAT issues for remote access

---

## 📁 Suggested Folder Structure

```
CamXtract/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── stream.py
│   │   ├── obs.py
│   ├── services/
│   │   ├── encoder.py
│   │   ├── websocket.py
│
├── frontend/
│   ├── obs.html
│   ├── viewer.html
│   ├── sender.html
│
├── streaming/
│   ├── hls/
│   ├── rtmp/
│
├── config/
│   ├── server.yaml
│
```

---

## 🚀 Recommended Approach (For Your Project)

Start with:

1. Browser Source (fastest to implement)
2. Then add RTMP (for production-level streaming)

---

# ✅ Final Outcome

After implementation, users can:

* Add CamXtract directly into OBS
* Stream mobile camera into OBS scenes
* Use it for recording / streaming / monitoring

---

# 📌 End of Document
