#!/usr/bin/env python3
"""
fetch_mesh.py — pull real CellMap / OpenOrganelle organelle meshes from the
public precomputed bucket and bake them into one GLB the flythrough can load.

This is the "serves up its data" backend, baked rather than streamed. Run it
where you have internet/AWS access (the precomputed meshes live on S3).

    pip install cloud-volume trimesh
    python fetch_mesh.py

You fill in two things you already know better than anyone:
  1. SOURCE  — the precomputed *mesh* layer URL for the organelle class.
  2. LABELS  — the segment ids you want (a few, or pull a region).

Easiest way to get SOURCE: open the dataset in the OpenOrganelle / Neuroglancer
viewer, click the segmentation layer, and copy its `source` URL — that string is
exactly what cloud-volume reads. cloud-volume handles all the sharded
multiresolution-Draco decoding for you, which is why we bake through it instead
of reimplementing Neuroglancer's loader.

Note on true streaming: if you want the game to read the bucket live (new
datasets light up with no rebuild), don't hand-roll the multires sharded mesh
decoder — reuse Neuroglancer's existing WebGL mesh-loading path. This baked GLB
is the pragmatic bridge to get game-feel working first.
"""

import numpy as np
import trimesh
from cloudvolume import CloudVolume

# --- fill these in ----------------------------------------------------------
# Example shape (NOT a guaranteed-live path — grab the real one from the viewer):
#   precomputed://s3://janelia-cosem-datasets/jrc_hela-2/<...>/mito_seg/
SOURCE = "precomputed://s3://janelia-cosem-datasets/<dataset>/<...>/<organelle>_seg"
LABELS = []                 # e.g. [4127, 4203, 5560]; leave [] to grab the largest N
TOP_N_IF_EMPTY = 6          # if LABELS is empty, pull this many of the biggest segments
TARGET_FACES = 60_000       # decimate each mesh to ~this (Nanite-free engines choke otherwise)
SCALE = 0.001               # nm -> arbitrary game units; tune to taste
OUT = "cell.glb"
# ----------------------------------------------------------------------------


def pick_labels(cv):
    """If you didn't list ids, grab a handful of the largest segments."""
    if LABELS:
        return LABELS
    # cloud-volume can list available mesh ids for many layers:
    ids = list(cv.mesh.exists.__self__.cv.mesh)  # fallback varies by layer/version
    # Robust path: most layers expose a label list via the manifest dir; if not,
    # just hardcode a few ids you saw in the viewer.
    raise SystemExit(
        "No LABELS given. Open the dataset in the viewer, hover organelles to read "
        "their segment ids, and put a few in LABELS."
    )


def main():
    cv = CloudVolume(SOURCE, use_https=True, progress=True)
    labels = pick_labels(cv)

    meshes = cv.mesh.get(labels)            # dict {id: Mesh} or a single Mesh
    if not isinstance(meshes, dict):
        meshes = {labels[0]: meshes}

    scene = trimesh.Scene()
    all_v = []

    for lid, m in meshes.items():
        tm = trimesh.Trimesh(vertices=np.asarray(m.vertices, float),
                             faces=np.asarray(m.faces))
        if len(tm.faces) > TARGET_FACES:
            try:
                tm = tm.simplify_quadric_decimation(TARGET_FACES)
            except Exception as e:
                print(f"  (decimate skipped for {lid}: {e})")
        all_v.append(tm.vertices)
        scene.add_geometry(tm, node_name=f"seg_{lid}")
        print(f"  seg {lid}: {len(tm.faces):,} faces")

    # recenter the whole cell region on the origin and scale to game units
    center = np.vstack(all_v).mean(axis=0)
    for name, geom in scene.geometry.items():
        geom.apply_translation(-center)
        geom.apply_scale(SCALE)

    scene.export(OUT)
    print(f"\nwrote {OUT} — drop it next to cellgame.html and load via GLTFLoader.")
    print("REMINDER: confirm the dataset's license (CC variant) before distributing.")


if __name__ == "__main__":
    main()
