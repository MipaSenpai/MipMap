// Дожидаемся полной загрузки DOM
document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map", {
    crs: L.CRS.Simple,
    minZoom: 1,
    maxZoom: 5,
    zoomControl: false,
  });

  L.control.zoom({ position: "bottomright" }).addTo(map);
  map.setView([0, 0], 2);

  L.tileLayer("api/tiles/{z}/{x}/{y}", {
    minZoom: 1,
    maxZoom: 5,
    tileSize: 256,
    noWrap: true,
    continuousWorld: true,
    attribution: null,
  }).addTo(map);

  // Обновление координат по клику
  map.on("click", (e) => {
    const x = Math.round(e.latlng.lng);
    const z = Math.round(e.latlng.lat);
    document.getElementById("coords").textContent = `x: ${x}, z: ${z}`;
  });

  // Копирование координат при клике
  const coordsEl = document.getElementById("coords");
  coordsEl.addEventListener("click", async (e) => {
    e.stopPropagation(); // Предотвращаем всплытие события
    e.preventDefault(); // Предотвращаем стандартное поведение

    const text = coordsEl.textContent;
    try {
      await navigator.clipboard.writeText(text);
      // Визуальная обратная связь
      const originalColor = coordsEl.style.color;
      coordsEl.style.color = "#4caf50"; // зелёный
      setTimeout(() => {
        coordsEl.style.color = originalColor;
      }, 400);
    } catch (err) {
      console.error("Не удалось скопировать координаты:", err);
      alert("Не удалось скопировать координаты. Попробуйте вручную.");
    }
  });
});
