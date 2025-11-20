<p align="center">
  <img src="https://raw.githubusercontent.com/MipaSenpai/MipMap/3b0047e8171538722cf673a29f67d11bebbc4075/webmap/web/static/assets/icon.svg" width="120" alt="MipMap Logo">
</p>

<h1 align="center">🗺️ MipMap</h1>
<p align="center">
  <strong>Interactive online map for Minecraft Bedrock servers</strong>
</p>

<p align="center">
  <a href="https://github.com/MipaSenpai/MipMap/stargazers">
    <img src="https://img.shields.io/github/stars/MipaSenpai/MipMap?style=for-the-badge&logo=github&color=8A2BE2&logoColor=white" />
  </a>
  <a href="https://github.com/MipaSenpai/MipMap/issues">
    <img src="https://img.shields.io/github/issues/MipaSenpai/MipMap?style=for-the-badge&logo=github&color=4B0082&logoColor=white" />
  </a>
  <a href="https://github.com/MipaSenpai/MipMap/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-9400D3?style=for-the-badge&logoColor=white" />
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-7C83FD?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=18&pause=1000&color=8A2BE2&center=true&vCenter=true&width=600&lines=Watch+your+world+come+alive+in+real+time;From+Overworld+to+the+End;Every+chunk%2C+every+player%2C+every+moment;Built+for+Endstone+and+LeviLamina+Made+for+explorers." alt="Typing SVG" />
</p>

---

## 🎬 See It In Action

<p align="center">
  <img src=".github/images/demo.gif" alt="MipMap Demo" width="800">
</p>

<p align="center">
  <sub>🗺️ Real-time rendering • 🎨 Depth shading • 👥 Player tracking</sub>
</p>

---

## ✨ What is MipMap?

MipMap transforms your Minecraft Bedrock server into a **living, breathing web map**. As players explore, the world renders itself automatically — no commands, no waiting, just pure real-time magic.

**Two parts. One vision:**

🎮 **Plugin** — Captures chunk data as your world loads and streams it to the web  
🌐 **Web Server** — Generates beautiful map tiles and serves an interactive interface

> 💜 **The map that grows with your world.**  
> No manual rendering. No restarts. Just exploration.

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🔄 Real-Time Updates
Chunks appear on the map **instantly** as they load in-game. Watch your world expand as players explore.

### 🌍 Multi-Dimensional
Navigate between **Overworld**, **Nether**, and **The End** with a single click. Each dimension, beautifully rendered.

### 👥 Player Tracking
See **who's online**, **where they are**, and even their **Minecraft skins** — all live on the map.

</td>
<td width="50%">

### 🎨 Dynamic Lighting
Blocks rendered with **depth-aware shading**, ambient occlusion, and custom color palettes. Your world never looked this good.

### ⚡ Batch Loading
Pre-render entire regions with `/loadmap` command. Perfect for showcasing builds or preparing for events.

### 🐳 Docker Ready
One command. One container. Your map is live in seconds.

</td>
</tr>
</table>

---

## 📦 Installation

### Step 1️⃣: Install the Plugin

Download the latest plugin file from [Releases](https://github.com/MipaSenpai/MipMap/releases) and place it in your server's `plugins` folder. Restart the server.

**For LeviLamina**: You need to have [LeviStone](https://github.com/LiteLDev/LeviStone) installed.

---

### Step 2️⃣: Launch the Web Server

#### 🐳 Option A: Docker (Recommended)

```bash
cd webmap
docker build -t mipmap-webmap .
docker run -d --name mipmap-webmap -p 8000:8000 mipmap-webmap
```

✅ **Done!** Visit `http://localhost:8000`

---

#### 🐍 Option B: Local with Uvicorn

```bash
cd webmap
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

✅ **Done!** Visit `http://localhost:8000`

---

## 🎮 Usage

### Commands

| Command | Description |
|---------|-------------|
| `/loadmap` | Start loading with default area from config |
| `/loadmap <minX> <minZ> <maxX> <maxZ>` | Start loading with custom coordinates |
| `/loadmap status` | Check current loading progress and remaining areas |
| `/loadmap help` | Display command usage |

---

## ⚙️ Configuration

### Plugin Settings

Edit `plugins/mipmap/config.toml`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `sendPlayers` | `boolean` | `true` | Enable player position tracking |
| `api.chunks` | `string` | `"http://localhost:8000/api/chunks-data"` | Chunks data endpoint |
| `api.players` | `string` | `"http://localhost:8000/api/players-data"` | Players data endpoint |
| `mapLoading.batchSize` | `int` | `100` | Number of chunks to process per batch |
| `mapLoading.maxAreas` | `int` | `10` | Maximum concurrent loading areas |
| `blacklist.blocks` | `array` | `["air", "water", ...]` | Blocks to skip when finding surface |

---

### Web Server Settings

Edit `webmap/core/config.py`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `MAP_SIZE` | `int` | `2000` | Map viewport size in pixels (width/height) |
| `MAP_UPDATE_INTERVAL` | `int` | `5000` | Player position update interval (milliseconds) |
| `MAP_DEFAULT_WORLD` | `string` | `"Overworld"` | Default dimension to display on load |
| `GENERATE_ZOOM_INTERVAL` | `int` | `300` | Zoom level generation interval (seconds) |

**Example:**
```python
MAP_SIZE = 3000  # Larger viewport for bigger screens
MAP_UPDATE_INTERVAL = 3000  # Update players every 3 seconds
MAP_DEFAULT_WORLD = "Nether"  # Start in the Nether
```

---

### Web Server Data Structure

```
webmap/data/
├── worlds/              # 🌍 World data organized by dimension
│   ├── Overworld/
│   │   └── tiles/       # 🖼️ Generated PNG tiles
│   │       ├── zoom-0/
│   │       ├── zoom-1/
│   │       └── zoom-2/
│   ├── Nether/
│   │   └── tiles/
│   └── TheEnd/
│       └── tiles/
├── skins/               # 👤 Player skin cache
│   └── default.png
└── failedTextures.json  # 🚫 Failed texture loading log
```

---

## 📡 API Reference

### `POST /api/chunks`

Receives chunk data from the plugin.

**Request Body:**
```json
{
  "chunk": {
    "dimension": "Overworld",
    "blocks": [
      {
        "name": "minecraft:grass_block",
        "coordinates": [64, 72, -32]
      },
      {
        "name": "minecraft:stone",
        "coordinates": [64, 71, -32]
      }
    ]
  }
}
```

---

### `POST /api/players`

Receives player position data.

**Request Body:**
```json
{
  "players": [
    {
      "name": "Steve",
      "skin": "89504e47...",  // Hex-encoded PNG
      "skinShape": [64, 64, 4],
      "dimension": "Overworld",
      "x": 123.45,
      "y": 64.0,
      "z": -67.89
    }
  ]
}
```

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Pillow-8A2BE2?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/Leaflet.js-199900?style=for-the-badge&logo=leaflet&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

---

## 🗓️ Roadmap

- [x] 🌍 Overworld rendering
- [x] ⚡ Real-time chunk updates
- [x] 👥 Player tracking with skins
- [x] 📦 Batch loading command
- [x] 🐳 Docker deployment
- [x] 🌌 The End dimension support
- [ ] 🔥 Nether dimension support
- [ ] 🎨 Custom dimension API

---

## 🤝 Contributing

Contributions are welcome! Fork the repo, make your changes, and open a Pull Request.

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>✨ MipMap - where each block finds its place. ✨</sub>
</p>
