from typing import Any, Dict, List, Optional, Union

# Note: The '@tool' decorator is removed as the tool registration will be handled by the ADK.
# The leafmap import is also removed as these tools no longer directly interact with a map object.

class MapTools:
    """Collection of tools that return JSON instructions for a mapping client."""

    def __init__(self):
        """Initialize map tools. The session is no longer needed in this stateless backend."""
        pass

    def create_map(
        self,
        center_lat: float = 20.0,
        center_lon: float = 0.0,
        zoom: int = 2,
        style: str = "liberty",
        projection: str = "globe",
    ) -> Dict[str, Any]:
        """Instruction to create or reset a map with specified parameters."""
        return {
            "action": "create_map",
            "payload": {
                "center": [center_lon, center_lat],
                "zoom": zoom,
                "style": style,
                "projection": projection,
            },
        }

    def add_basemap(self, name: str) -> Dict[str, Any]:
        """Instruction to add a basemap to the map by name."""
        return {"action": "add_basemap", "payload": {"name": name}}

    def add_vector(self, data: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Instruction to add a vector dataset to the map."""
        return {"action": "add_vector", "payload": {"data": data, "name": name}}

    def fly_to(self, longitude: float, latitude: float, zoom: int = 12) -> Dict[str, Any]:
        """Instruction to fly to a specific geographic location."""
        return {
            "action": "fly_to",
            "payload": {"longitude": longitude, "latitude": latitude, "zoom": zoom},
        }

    def add_cog_layer(
        self,
        url: str,
        name: Optional[str] = None,
        opacity: float = 1.0,
        bands: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Instruction to add a Cloud Optimized GeoTIFF (COG) layer to the map."""
        return {
            "action": "add_cog_layer",
            "payload": {"url": url, "name": name, "opacity": opacity, "bands": bands},
        }

    def remove_layer(self, name: str) -> Dict[str, Any]:
        """Instruction to remove a layer from the map by name."""
        return {"action": "remove_layer", "payload": {"name": name}}

    def add_overture_3d_buildings(self, **kwargs: Any) -> Dict[str, Any]:
        """Instruction to add 3D buildings from Overture Maps to the map."""
        return {"action": "add_overture_3d_buildings", "payload": kwargs}

    def set_pitch(self, pitch: float) -> Dict[str, Any]:
        """Instruction to set the pitch of the map."""
        return {"action": "set_pitch", "payload": {"pitch": pitch}}

    def set_paint_property(self, name: str, prop: str, value: Any) -> Dict[str, Any]:
        """Instruction to set the paint property of a layer."""
        return {
            "action": "set_paint_property",
            "payload": {"name": name, "prop": prop, "value": value},
        }

    def set_layout_property(self, name: str, prop: str, value: Any) -> Dict[str, Any]:
        """Instruction to set the layout property of a layer."""
        return {
            "action": "set_layout_property",
            "payload": {"name": name, "prop": prop, "value": value},
        }

    def set_color(self, name: str, color: str) -> Dict[str, Any]:
        """Instruction to set the color of a layer."""
        return {"action": "set_color", "payload": {"name": name, "color": color}}

    def set_opacity(self, name: str, opacity: float) -> Dict[str, Any]:
        """Instruction to set the opacity of a layer."""
        return {"action": "set_opacity", "payload": {"name": name, "opacity": opacity}}

    def set_visibility(self, name: str, visible: bool) -> Dict[str, Any]:
        """Instruction to set the visibility of a layer."""
        return {"action": "set_visibility", "payload": {"name": name, "visible": visible}}

    def add_marker(
        self, lng_lat: List[Union[float, float]], popup: Optional[str] = None
    ) -> Dict[str, Any]:
        """Instruction to add a marker to the map."""
        return {"action": "add_marker", "payload": {"lng_lat": lng_lat, "popup": popup}}

    def zoom_to(self, zoom: float) -> Dict[str, Any]:
        """Instruction to zoom the map to a specified zoom level."""
        return {"action": "zoom_to", "payload": {"zoom": zoom}}

    def get_layer_names(self) -> Dict[str, Any]:
        """Instruction to get the names of all layers on the map."""
        return {"action": "get_layer_names", "payload": {}}

    def set_terrain(self, exaggeration: float = 1.0) -> Dict[str, Any]:
        """Instruction to add terrain visualization to the map."""
        return {"action": "set_terrain", "payload": {"exaggeration": exaggeration}}

    def remove_terrain(self) -> Dict[str, Any]:
        """Instruction to remove terrain visualization from the map."""
        return {"action": "remove_terrain", "payload": {}}
