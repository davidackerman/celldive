# CELLDIVE

CELLDIVE is a single-file browser game for exploring real cell reconstructions from the public OpenOrganelle / CellMap archive.

Play it here:

https://davidackerman.github.io/cellgame/

## Run Locally

Open `cellgame.html` in a browser. There is no build step.

The game loads Three.js from a CDN and streams public CellMap/OpenOrganelle mesh data directly in the browser.

## Controls

- `W` / `S`: thrust and brake
- `A` / `D`: steer or carve
- Drag: look around
- `Shift`: boost
- `Space`: analyze nearby organelles, or jump while boarding
- `X`: board or detach
- `V`: toggle avatar view
- `K`: switch avatar
- `[` / `]`: resize avatar

## Files

- `cellgame.html`: the playable game
- `cellgame_old.html`: older prototype
- `mesh_probe.html`: mesh loading/debug harness
- `fetch_mesh.py`: mesh utility script
