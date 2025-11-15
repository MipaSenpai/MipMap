class MipMapViewer {
  constructor() {
    this.config = {
      minZoom: 0,
      maxZoom: 4,
      tileSize: 256,
      updateInterval: 5000,
      defaultWorld: "Overworld",
      mapSize: 1000,
    };

    this.map = null;
    this.currentWorld = this.config.defaultWorld;
    this.currentTileLayer = null;
    this.playerMarkers = {};
    this.updateTimer = null;

    this.elements = {
      coords: document.getElementById("coords"),
      worldSelector: document.getElementById("worldSelector"),
    };

    this.init();
  }

  async init() {
    await this.loadConfig();
    this.initMap();
    this.initTileLayer();
    this.initEventListeners();
    this.startPlayerUpdates();
  }

  async loadConfig() {
    try {
      const response = await fetch("/api/config");
      const serverConfig = await response.json();
      
      this.config.mapSize = serverConfig.mapSize || this.config.mapSize;
      this.config.updateInterval = serverConfig.updateInterval || this.config.updateInterval;
      this.config.defaultWorld = serverConfig.defaultWorld || this.config.defaultWorld;
      this.currentWorld = this.config.defaultWorld;
    } catch (error) {
      console.error("Ошибка загрузки конфигурации:", error);
    }
  }

  initMap() {
    const size = this.config.mapSize;
    const bounds = [[-size, -size], [size, size]];
    
    this.map = L.map("map", {
      crs: L.CRS.Simple,
      minZoom: this.config.minZoom,
      maxZoom: this.config.maxZoom,
      zoomControl: false,
      maxBounds: bounds,
      maxBoundsViscosity: 1.0,
    });

    L.control.zoom({ position: "bottomright" }).addTo(this.map);
    this.map.setView([0, 0], 2);
    this.map.fitBounds(bounds);
  }

  initTileLayer() {
    this.currentTileLayer = L.tileLayer(
      `/api/tiles/${this.currentWorld}/{z}/{x}/{y}`,
      {
        minZoom: this.config.minZoom,
        maxZoom: this.config.maxZoom,
        tileSize: this.config.tileSize,
        noWrap: true,
        continuousWorld: true,
        attribution: null,
      }
    ).addTo(this.map);
  }

  initEventListeners() {
    this.map.on("click", (e) => this.handleMapClick(e));
    this.elements.coords.addEventListener("click", (e) => this.handleCoordsClick(e));
    
    const worldButtons = this.elements.worldSelector.querySelectorAll(".world-btn");
    worldButtons.forEach((btn) => {
      btn.addEventListener("click", () => this.switchWorld(btn.dataset.world));
    });
  }

  handleMapClick(e) {
    const x = Math.round(e.latlng.lng);
    const z = Math.round(e.latlng.lat);
    this.elements.coords.textContent = `x: ${x}, z: ${z}`;
  }

  async handleCoordsClick(e) {
    e.stopPropagation();
    e.preventDefault();

    try {
      await navigator.clipboard.writeText(this.elements.coords.textContent);
      this.elements.coords.classList.add("copied");
      setTimeout(() => this.elements.coords.classList.remove("copied"), 400);
    } catch (err) {
      console.error("Ошибка копирования:", err);
    }
  }

  switchWorld(newWorld) {
    if (newWorld === this.currentWorld) return;

    this.currentWorld = newWorld;
    this.map.removeLayer(this.currentTileLayer);
    this.initTileLayer();

    document.querySelectorAll(".world-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.world === newWorld);
    });

    this.filterPlayersByWorld();
  }

  async updatePlayers() {
    try {
      const bounds = this.map.getBounds();
      const params = new URLSearchParams({
        x_min: Math.floor(bounds.getSouthWest().lng),
        x_max: Math.ceil(bounds.getNorthEast().lng),
        z_min: Math.floor(bounds.getSouthWest().lat),
        z_max: Math.ceil(bounds.getNorthEast().lat),
      });

      const response = await fetch(`/api/players?${params}`);
      const data = await response.json();

      this.removeDisconnectedPlayers(data.players);
      this.updatePlayerMarkers(data.players);
    } catch (error) {
      console.error("Ошибка обновления игроков:", error);
    }
  }

  removeDisconnectedPlayers(activePlayers) {
    const activeNames = new Set(activePlayers.map((p) => p.name));
    
    Object.keys(this.playerMarkers).forEach((name) => {
      if (!activeNames.has(name)) {
        this.playerMarkers[name].remove();
        delete this.playerMarkers[name];
      }
    });
  }

  updatePlayerMarkers(players) {
    players.forEach((player) => {
      if (!player.name) return;
      
      const marker = this.playerMarkers[player.name];
      
      if (marker) {
        marker.setLatLng([player.z, player.x]);
        marker.playerData = player;
        
        if (marker.isPopupOpen()) {
          marker.setPopupContent(this.createPlayerPopup(player));
        }
        
        if (player.dimension === this.currentWorld) {
          if (!this.map.hasLayer(marker)) {
            marker.addTo(this.map);
          }
        } else {
          if (this.map.hasLayer(marker)) {
            this.map.removeLayer(marker);
          }
        }
      } else {
        this.createPlayerMarker(player);
      }
    });
  }

  filterPlayersByWorld() {
    Object.values(this.playerMarkers).forEach((marker) => {
      if (marker.playerData && marker.playerData.dimension === this.currentWorld) {
        if (!this.map.hasLayer(marker)) {
          marker.addTo(this.map);
        }
      } else {
        if (this.map.hasLayer(marker)) {
          this.map.removeLayer(marker);
        }
      }
    });
  }

  createPlayerMarker(player) {
    const iconUrl = `/api/players/${player.name}/skin.png`;
    const fallbackLetter = player.name ? player.name[0].toUpperCase() : "?";
    
    const icon = L.divIcon({
      html: `
        <div class="player-marker-container">
          <img src="${iconUrl}" 
               class="player-avatar" 
               onerror="this.style.display='none'; this.parentElement.querySelector('.player-avatar-wrapper').innerHTML='<div class=\\'player-fallback\\'>${fallbackLetter}</div>'">
          <span class="player-nickname">${player.name}</span>
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      className: "player-icon",
    });

    const marker = L.marker([player.z, player.x], { icon });
    marker.playerData = player;
    marker.bindPopup(this.createPlayerPopup(player));
    
    if (player.dimension === this.currentWorld) {
      marker.addTo(this.map);
    }
    
    this.playerMarkers[player.name] = marker;
  }

  createPlayerPopup(player) {
    return `
      <div class="player-popup">
        <div class="player-header">
          <img src="/api/players/${player.name}/skin.png" 
               class="popup-avatar" 
               width="32" 
               height="32"
               alt="${player.name}">
          <h3>${player.name}</h3>
        </div>
        <div class="player-coords">
          <div class="coord-item">
            <span class="coord-label">x:</span>
            <span class="coord-value">${Math.round(player.x)}</span>
          </div>
          <div class="coord-item">
            <span class="coord-label">y:</span>
            <span class="coord-value">${Math.round(player.y)}</span>
          </div>
          <div class="coord-item">
            <span class="coord-label">z:</span>
            <span class="coord-value">${Math.round(player.z)}</span>
          </div>
        </div>
      </div>
    `;
  }

  startPlayerUpdates() {
    this.updatePlayers();
    this.updateTimer = setInterval(() => this.updatePlayers(), this.config.updateInterval);
  }

  destroy() {
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
    if (this.map) {
      this.map.remove();
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new MipMapViewer();
});
