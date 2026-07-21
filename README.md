# CELLDIVE

CELLDIVE is a single-file browser game for exploring real cell reconstructions from the public OpenOrganelle / CellMap archive.

Play it here:

https://davidackerman.github.io/celldive/

## Run Locally

Open `celldive.html` in a browser. There is no build step.

The game loads Three.js from a CDN and streams public CellMap/OpenOrganelle mesh data directly in the browser.

## Controls

Pick **flight** (free-fly, no gravity) or **jetpack** (gravity + fuel-limited thrust + a
mesh-cutting laser) before diving in — switch either way anytime from the in-dive menu.

- Mouse: look around (`Esc` releases the cursor anytime)
- `W` / `A` / `S` / `D`: move (fly/strafe in flight mode; thrust/carve while boarding or
  walking a surface)
- `R` / `F`: up / down (flight mode)
- `Shift`: boost, or analyze the nearest organelle when held
- `Space`: jetpack thrust (jetpack mode), or jump while boarding/walking
- Click: fire the laser (jetpack mode)
- `X`: mount/detach a skateboard, or latch onto a surface to walk it
- Scroll: adjust the torch's brightness
- `Tab`: open the menu — organelle layers, detail level, narration, guided tour, avatar,
  and more
- `V`: toggle third-person view
- `K`: switch avatar
- `[` / `]`: resize avatar

## Files

- `celldive.html`: the playable game
- `celldive_old.html`: older prototype
- `mesh_probe.html`: mesh loading/debug harness
- `fetch_mesh.py`: mesh utility script
