# CELLDIVE — explore real cells from OpenOrganelle

A browser game: shrink to nanoscale and fly through a real FIB-SEM cell
reconstruction from Janelia's public **OpenOrganelle / CellMap** archive
(`s3://janelia-cosem-datasets`), analyzing its organelles.

## What's playable now — `celldive.html` (single self-contained file)

Open it in any browser (it loads Three.js r128 from a CDN; no build step).

- **Specimen-select screen** pulls the **live** dataset catalog straight from the
  public S3 bucket (`?list-type=2&delimiter=/`) — all ~93 real datasets with their
  real `thumbnail.jpg` previews. The bucket is CORS-open (`Allow-Origin: *`), so this
  works from any origin/iframe. Falls back to a baked-in id list if offline.
  Search + filter by tissue kind (cell / liver / neuron / muscle / tissue).
- **Dive loads REAL organelle meshes, live in the browser.** For any specimen with
  published meshes (badged **● real 3D** on the select screen), the game lists its
  `neuroglancer/mesh/<organelle>_seg/` layers, pulls the largest segments, decodes the
  `neuroglancer_multilod_draco` format **client-side** (manifest parse → coarse-LOD
  HTTP-Range fetch → Draco decode → nm vertex transform), and drops them into the dive in
  their **true relative spatial arrangement** (shared nm frame, recentred + scaled to the
  play volume). No baking, no server, no pipeline — genuine FIB-SEM geometry, any specimen.
  Verified on `jrc_hela-2`: 42 real meshes across 7 organelle classes, analyze loop works.
- **Dynamic LOD streaming (neuroglancer-style detail-on-approach).** Each segment starts at
  its coarsest LOD; `manageLOD()` runs each frame (throttled, nearest-first, concurrency-capped)
  and steps organelles one LOD finer as you approach, coarser as you leave — re-Range-fetching
  and re-decoding just that level, capped by a per-LOD byte budget so the finest never buries
  the GPU. Manifests/info are cached so swaps don't refetch. Verified: ~348K → ~3.2M triangles
  as you close on the nucleus; a "streaming higher detail…" indicator shows while it works.
- **The bus + external view.** First person is a clean cockpit-free view; press **V** to toggle
  a third-person chase cam showing a low-poly **school bus** (`makeBus()`) flying through the
  cell, banking into turns. Movement has real **momentum** (light damping, the bus coasts). The
  player rides `playerPos`; the camera attaches in 1st person and pulls back in 3rd.
- **ng-style layer panel.** Top-left panel lists every organelle type present with its colour
  swatch and a checkbox to **toggle that layer's visibility** (`layerMeshes` registry). Each
  real-mesh row also shows a **live LOD readout** ("LOD 5" → "LOD 2↓") so you can watch
  multiresolution working as you approach — concrete proof the multires stream is real.
- **Controllable torch.** A forward `SpotLight` lights whatever you look at; **mouse wheel**
  adjusts its brightness. (Also fixed a "feels like falling" illusion — the ambient dust field
  no longer auto-rotates, which was causing vection on a still camera.)
- **Ms. Frizzle narration + guided tour.** Free, local **Web Speech API** TTS (`narrate()`):
  drive near an organelle and it's narrated once (`proximityNarrate` + `FRIZZ` lines); press
  **T** / "take the tour" and the bus **auto-drives** between every organelle, narrating each
  (`updateTour`), cancel by grabbing the wheel. Toolbar toggles: 🔊 narration (N), 🧭 tour (T),
  🎨 unique colors (C), ☀️ shadows (H), 🚌 bus view (V).
- **ng-style unique segment colours.** Toggle colours every mesh by a hash of its **real
  neuroglancer segment id** (`segHue` — murmur3 mix), so a segment gets a stable distinct hue
  like in neuroglancer; off = colour-by-organelle-type.
- **Dynamic shadows** (optional, off by default for perf) — a scene `DirectionalLight`
  (`shadowLight`, sun-style from above) casts **object-on-object** shadows across the cell;
  meshes cast/receive, the bus casts too. (Unique-colour fix: the per-type **emissive** glow is
  recoloured to match, else it tinted every same-type mesh.) **Detail budget raised**
  (`LOD_BUDGET` 6 MB, 4 concurrent) to use more memory
  for finer meshes — note browsers don't expose ng's explicit GPU-memory knob, so this is the
  lever we have. The streaming chip is now debounced + LOD has hysteresis (no more popping).
- **Select screen:** a "● real 3D only" toggle (default **on**) filters to specimens whose
  meshes actually load; flip it off for the full archive.
- **Cargo Run (G / 🎯).** A simple 3-stop "**Go to** the ER → the Golgi → the cell membrane"
  route (the secretory pathway), narrated by Frizzle, with a compass + timer. Each stop has a
  tight reach + a brief dwell so stops can't chain-complete. `planQuest`/`updateCargoTick`.
  (No carried-orb HUD prop — removed as obtrusive.)
- **Analyze-anything (SPACE).** SPACE analyzes whichever organelle you're *nearest* to, in any
  order — not just the scripted objective. An in-progress scan is "sticky" (stays locked to its
  target while in widened reach) so drifting past others doesn't reset progress.
- **3D direction marker.** A reticle sprite (`marker`, depthTest off, constant screen size) floats
  at the active objective / cargo-run target and pulses — shows exactly where to go through any
  geometry (the 2D compass only encoded heading; this fixes vertical/ambiguous directions).
- **Whole-volume mesh sampling.** Layers can have *thousands* of instances (thymus `nucleus_seg`
  = **16,031** nuclei). The full id list is read cheaply from `…/<layer>/segment_properties/info`,
  then we **sample evenly across all ids** (not biggest-of-first-page) up to a per-dive budget
  (`MAX_MESHES=600`, split across layers) so the whole tissue is represented. HUD shows
  "N of M real meshes". Loading/​drawing all 16k separately isn't browser-feasible (that's what
  neuroglancer's sharded GPU streaming is for) — would need merged/instanced rendering.
  A **detail slider** (`resCap`) caps the finest LOD; dive starts at a 3/4 angle so volumes read
  as 3D, not a flat near-face. Datasets whose only meshes are hand-labeled
  **ground-truth crops** (`groundtruth/<crop>/<class>/`, e.g. sum159, kidney) now load too via a
  new **`neuroglancer_legacy_mesh`** decoder (`loadLegacy`: raw uint32 count · float32 positions ·
  uint32 indices — no Draco); these are single-LOD so `manageLOD` skips them.
- **Living Cell.** Generative **Web Audio** soundscape (M / 🎵): a warm **audible** chord drone
  (~110–330 Hz with slow detune shimmer — NOT sub-bass, which laptop speakers can't play) +
  a periodic heartbeat thump + an on/off confirmation chirp (`ensureAudio`/`blip`/`thump`/`chime`,
  master ramped, `resume()` on the toggle gesture). Plus **proximity audio**: a sonar **ping**
  that quickens and rises in pitch as you near the active target, and the drone's lowpass opens
  up as you close in. Organelle-traffic vesicles were removed. Deferred: minimap/radar + journal.
- **Procedural fallback** for specimens without published meshes: a cell interior **tailored
  to the dataset's biology** via `describe()` + `PROFILES` (liver → dense mito + peroxisomes +
  glycogen + lipid; neuron → synaptic-vesicle clouds + microtubules; HeLa → nucleus/ER/Golgi/
  lysosome; etc.), seeded by id so it's consistent run-to-run. The HUD labels which mode is
  active ("N real FIB-SEM meshes · CellMap" vs "procedural model · no published meshes").
- **Scan/analyze loop**: fly to an organelle (compass arrow + crosshair lock guide you),
  hold **SPACE** to analyze, and a data card pops with **scientifically accurate** facts
  from the `ORG` knowledge base — including what CellMap actually segments for that class.
  Analyze every organelle class → "specimen mapped" → **Open in OpenOrganelle** deep-links
  to the real viewer (`openorganelle.janelia.org/datasets/<id>`).
- Controls: drag-look + WASD fly + R/F up·down + Shift boost + **scroll** torch + **SPACE**
  analyze (iframe-safe — no Pointer Lock; core Three.js + the gstatic Draco decoder).

Verified end-to-end in headless Chrome: live catalog loads (93 cards), real meshes decode
and render (`jrc_hela-2` → 42 meshes), fly-to-lock + SPACE-analyze works in both real and
procedural mode, mesh-less specimens fall back cleanly.

`celldive_old.html` is the original procedural-only prototype. `mesh_probe.html` is a
standalone single-segment mesh-decode harness (useful for debugging the loader in isolation).

## How the in-browser mesh loader works (the core of it, in `celldive.html`)
The published meshes are neuroglancer **unsharded** `multilod_draco`. Per organelle layer:
`info` (transform + `vertex_quantization_bits`), and per segment a `<id>.index` manifest +
`<id>` data blob. The loader (`loadSegmentCoarse` / `parseManifest` / `dracoDecode`):
1. Parses the `.index` manifest: `chunk_shape`, `grid_origin`, `num_lods`, `lod_scales`,
   `vertex_offsets` (C-order `[num_lods,3]`), `num_fragments_per_lod`, then per LOD the
   fragment positions (C-order `[3,nf]`) and fragment byte-sizes.
2. Picks the **coarsest non-empty LOD** (tiny — a few KB) and HTTP-**Range**-fetches just
   that byte span from the `<id>` blob (S3 CORS allows `Range`).
3. **Draco-decodes** each fragment with the gstatic decoder (`DracoDecoderModule`, asm.js).
4. Transforms quantized verts to nm:
   `nm[j] = grid_origin[j] + vertex_offsets[lod][j] + chunk_shape[j]·2^lod·(fragPos[j] + q/(2^bits−1))`,
   then applies the `info.transform` (voxel→nm) matrix.
All segments across all layers share one nm frame, so recentring the combined set on its
centroid + a single fit-scale preserves the **real relative arrangement**. Coarse LOD keeps
triangle counts low (no decimation needed). Concurrency-pooled (`pool`, 8-wide); 40 s
timeout → procedural fallback.

## Next upgrades (optional)

### 1. LOD-on-approach / higher detail
Coarse LOD is blocky up close. Load a finer LOD for the nearest objective (the manifest
already has all LOD byte-ranges) or progressively refine as the player nears a mesh.

### 2. Real plasma-membrane shell from `pm_seg`
Skipped for now (the procedural membrane is used). `pm_seg` is the actual cell surface —
loading its coarse LOD as the enclosing membrane would make containment match real geometry.

### 3. Pull real per-specimen metadata into the dive
Each dataset has richer metadata than the id encodes (imaging resolution, sample prep,
publication). If a stable JSON metadata endpoint exists in the bucket, surface it on the
select card and in the HUD instead of inferring from the name.

### 4. `fetch_mesh.py` (now optional)
The baked-GLB path is superseded by live loading for the common case, but `fetch_mesh.py`
(cloud-volume → `cell.glb`) is still handy for offline/export or for layers the in-browser
loader doesn't cover. cloud-volume handles the sharded/multires decode; recenter + decimate
before export.

## Gotchas / constraints
- **License**: confirm the specific dataset's CC variant before distributing renders/meshes.
- **LOD choice**: the loader takes the coarsest LOD on purpose (cheap + low-poly). Pulling
  LOD 0 of a big mito (megabytes, 100k+ tris) would bury a non-Nanite web renderer.
- **Layer naming varies by dataset** — `MESH_LAYERS` maps the known `*_seg` names; datasets
  with other naming just fall back. Extend that table to cover more layers.
- **Sandbox/iframe**: keep the drag-look + WASD baseline; avoid Pointer Lock and non-cdnjs
  addon scripts if it must run embedded. (Draco decoder is on gstatic, not cdnjs — fine for
  most embeds, but self-host it if a strict CSP blocks gstatic.)
- The `?list-type=2` listings return ≤1000 keys; fine today (~94 datasets, <600 keys/layer),
  but paginate via `continuation-token` if a layer ever exceeds that.
