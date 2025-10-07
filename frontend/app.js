/* global maplibregl */
(function () {
  const backendBase = window.__BACKEND_BASE__ || 'http://localhost:8082';

  const BASEMAPS = {
    liberty: 'https://demotiles.maplibre.org/style.json',
    streets: 'https://demotiles.maplibre.org/style.json',
    satellite: 'https://demotiles.maplibre.org/style.json'
  };

  const map = new maplibregl.Map({
    container: 'map',
    style: BASEMAPS.liberty,
    center: [0, 20],
    zoom: 2,
    pitch: 0,
    projection: 'mercator'
  });

  const markers = [];

  function log(line) {
    const el = document.getElementById('log');
    const item = document.createElement('div');
    item.textContent = line;
    el.prepend(item);
  }

  function removeLayerAndSource(name) {
    if (map.getLayer(name)) {
      map.removeLayer(name);
    }
    if (map.getSource(name)) {
      map.removeSource(name);
    }
  }

  function dispatchAction(result) {
    if (!result || typeof result !== 'object') return;
    const action = result.action;
    const payload = result.payload || {};
    if (!action) return;

    try {
      switch (action) {
        case 'fly_to': {
          const { longitude, latitude, zoom } = payload;
          const opts = { center: [longitude, latitude] };
          if (typeof zoom === 'number') opts.zoom = zoom;
          map.flyTo(opts);
          break;
        }
        case 'zoom_to': {
          const { zoom } = payload;
          if (typeof zoom === 'number' || typeof zoom === 'string') {
            map.setZoom(Number(zoom));
          }
          break;
        }
        case 'create_map': {
          const { center, zoom, style, projection } = payload;
          if (style && BASEMAPS[style]) {
            map.setStyle(BASEMAPS[style]);
          }
          if (projection === 'globe' || projection === 'mercator') {
            const setProj = () => {
              try { map.setProjection(projection); } catch (e) {}
            };
            if (map.isStyleLoaded()) setProj(); else map.once('styledata', setProj);
          }
          if (Array.isArray(center) && center.length === 2) {
            map.setCenter(center);
          }
          if (typeof zoom === 'number') {
            map.setZoom(zoom);
          }
          break;
        }
        case 'add_basemap': {
          const { name } = payload;
          const styleUrl = (name && BASEMAPS[name]) || BASEMAPS.liberty;
          map.setStyle(styleUrl);
          break;
        }
        case 'add_vector': {
          const { data, name } = payload;
          const sourceId = name || 'vector-geojson';
          removeLayerAndSource(sourceId);
          map.addSource(sourceId, {
            type: 'geojson',
            data: data,
          });
          map.addLayer({
            id: sourceId,
            type: 'fill',
            source: sourceId,
            paint: { 'fill-color': '#088', 'fill-opacity': 0.5 },
          });
          break;
        }
        case 'remove_layer': {
          const { name } = payload;
          if (name) removeLayerAndSource(name);
          break;
        }
        case 'add_marker': {
          const { lng_lat, popup } = payload;
          const m = new maplibregl.Marker().setLngLat(lng_lat).addTo(map);
          markers.push(m);
          if (popup) {
            const p = new maplibregl.Popup({ offset: 25 }).setText(popup);
            m.setPopup(p);
          }
          break;
        }
        case 'set_pitch': {
          const { pitch } = payload;
          if (typeof pitch === 'number') map.setPitch(pitch);
          break;
        }
        case 'set_opacity': {
          const { name, opacity } = payload;
          if (name && map.getLayer(name) && typeof opacity === 'number') {
            map.setPaintProperty(name, 'fill-opacity', opacity);
          }
          break;
        }
        case 'set_paint_property': {
          const { name, property, value } = payload;
          if (name && map.getLayer(name) && typeof value === 'string') {
            map.setPaintProperty(name, property, value);
          }
          break;
        }
        case 'set_layout_property': {
          const { name, property, value } = payload;
          if (name && map.getLayer(name) && typeof value === 'string') {
            map.setLayoutProperty(name, property, value);
          }
          break;
        }
        case 'get_layer_names': {
          const style = map.getStyle();
          const ids = (style.layers || []).map((l) => l.id);
          log('Layers: ' + ids.join(', '));
          break;
        }
        case 'set_terrain': {
          const demId = 'dem';
          if (!map.getSource(demId)) {
            map.addSource(demId, {
              type: 'raster-dem',
              tiles: [
                'https://demotiles.maplibre.org/terrain-tiles/{z}/{x}/{y}.png'
              ],
              tileSize: 256,
              encoding: 'mapbox'
            });
          }
          map.setTerrain({ source: demId, exaggeration: Number(payload.exaggeration || 1.0) });
          break;
        }
        case 'remove_terrain': {
          try { map.setTerrain(null); } catch (e) {}
          break;
        }
        case 'add_cog_layer': {
          // Expecting a tile URL for now; raw COG rendering is out-of-scope.
          const { url, name } = payload;
          if (!url) {
            log('Missing tile url for add_cog_layer');
            break;
          }
          const id = name || 'raster-cog';
          removeLayerAndSource(id);
          map.addSource(id, {
            type: 'raster',
            tiles: [url],
            tileSize: 256,
          });
          map.addLayer({ id, type: 'raster', source: id });
          break;
        }
        case 'chat_response': {
          log('Chat: ' + (payload && payload.message));
          break;
        }
        default:
          log('Unknown action: ' + action);
      }
    } catch (e) {
      log('Dispatch error: ' + (e && e.message ? e.message : String(e)));
    }
  }

  const form = document.getElementById('chat-form');
  const input = document.getElementById('query');
  const history = [];

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;
    try {
      const res = await fetch(backendBase + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, history }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const json = await res.json();
      dispatchAction(json);
      // Keep a minimal history
      history.push({ role: 'user', content: query });
      input.value = '';
    } catch (err) {
      log('Request error: ' + (err && err.message ? err.message : String(err)));
    }
  });
})();


