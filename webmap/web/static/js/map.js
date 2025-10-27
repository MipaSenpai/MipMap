// app/web/static/js/map.js

let map = null;

document.getElementById("loadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("jsonFile");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a JSON file");
    return;
  }

  const status = document.getElementById("status");
  status.textContent = "Uploading...";

  try {
    const text = await file.text();
    const worldData = JSON.parse(text);

    const res = await fetch("/api/v1/worlds", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(worldData),
    });

    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);

    const { world_id } = await res.json();

    window.currentWorld = worldData;
    initMap(world_id);
    status.textContent = "✅ Loaded!";
  } catch (err) {
    status.textContent = "❌ " + err.message;
    console.error(err);
  }
});

function initMap(worldId) {
  if (map) {
    map.setTarget(null);
  }

  // Создаём пользовательскую проекцию
  const extent = [-20000, -20000, 20000, 20000]; // достаточно большой
  const pixelProjection = new ol.proj.Projection({
    code: "pixel",
    units: "pixels",
    extent: extent,
  });

  // Источник с указанием проекции
  const tileSource = new ol.source.XYZ({
    url: `/api/v1/tiles/${worldId}/{z}/{x}/{y}.png`,
    tileSize: 256,
    projection: pixelProjection, // ← КЛЮЧЕВОЙ момент
    maxZoom: 4,
  });

  const layer = new ol.layer.Tile({ source: tileSource });

  map = new ol.Map({
    target: "map",
    layers: [layer],
    view: new ol.View({
      projection: pixelProjection,
      center: [0, 0],
      zoom: 0,
      minZoom: 0,
      maxZoom: 4,
    }),
  });

  // Авто-центрирование БЕЗ setTimeout
  autoCenterMap();
}

function autoCenterMap() {
  if (!window.currentWorld || !map) return;

  const blocks = window.currentWorld.blocks;
  const xs = blocks.map((b) => b.x);
  const zs = blocks.map((b) => -b.z); // инвертируем Z

  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minZ = Math.min(...zs);
  const maxZ = Math.max(...zs);

  const centerX = (minX + maxX) / 2;
  const centerZ = (minZ + maxZ) / 2;

  const width = maxX - minX;
  const height = maxZ - minZ;
  const maxDim = Math.max(width, height);

  let zoom = 0;
  if (maxDim > 0) {
    // На zoom=0: 1 блок = 16px → 256px = 16 блоков
    // Нужно, чтобы весь мир поместился в ~512px (2 тайла)
    const blocksPerTile = 16; // при zoom=0
    const tilesNeeded = maxDim / blocksPerTile;
    zoom = Math.max(0, Math.floor(Math.log2(4 / tilesNeeded))); // 4 = 2x2 тайла
  }

  map.getView().setCenter([centerX * 16, centerZ * 16]);
  map.getView().setZoom(zoom);
}
