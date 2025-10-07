## Frontend (MapLibre) Notes

### Current limitations
- Interpretation is not accurate: the model sometimes flies to New York regardless of input. This is due to LLM function-calling heuristics and prompt constraints.
- UI needs enhancements: basic input-only interface; lacks controls for layers, history, errors, and better basemap choices.

### Next steps
- Tighten prompts and tool specs to improve argument extraction (e.g., coordinates parsing and validation).
- Add better UI: basemap picker, quick actions, layer list, error toasts, and history.
- Wire more actions (terrain with real DEM tiles, COG via tile service, paint/layout editors).


