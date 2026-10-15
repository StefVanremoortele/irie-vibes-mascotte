# Irie Vibes mascot

An experimental animated woofer mascot for the Irie Vibes dub and reggae festival website. We shape and rig the character in Blender, export GLB files, and play the dance with Three.js alongside music in a browser. See [VISION.md](VISION.md) for the direction of the project.

## Try the web preview

From the repository root, run:

```powershell
python -m http.server 8000
```

Open <http://localhost:8000/>; the root page forwards to `web/`. Press play on the audio control. Drag to turn the model and scroll to zoom. The preview uses `irie-vibes-openmind.glb`; its dance follows the playback position of `openmindaudio.mp3`, including when you pause or seek. The first strong beat is about 0.97 seconds into the song. You can also serve the `web/` folder on its own and open the server's root URL.

The page loads a pinned Three.js release from a CDN, so the browser needs an internet connection. Serve the project over HTTP; opening `web/index.html` directly from Explorer will not reliably load the model.

## Explore the Blender scene

Open `blender/projects/irie-vibes-openmind.blend` in Blender and press **Space** to play. The MP3 is packed into this file. The character shifts weight between planted feet, lifts the free foot slightly, leans back, and alternates raised arms on the beat.

The armature's **Leg IK blend** custom property is `1` for grounded playback. Set it to `0` to pose the thigh and shin bones directly. **IK blend** controls hand IK separately and starts at `0` so the arm animation plays. The `hand_ik.*`, `foot_ik.*`, `elbow_pole.*`, and `knee_pole.*` bones are posing controls. In Pose Mode, select a bone and press **R** to try a rotation; press **Esc** to cancel it.

## Project layout

| Path | Contents |
| --- | --- |
| `assets/models/source/` | Original `irie-vibes-peeking.glb`, OBJ, and its MTL palette |
| `assets/models/exports/` | Earlier GLB exports kept for comparison |
| `blender/projects/` | Editable Blender scenes |
| `blender/scripts/` | Repeatable scene and export builders |
| `blender/backups/` | Earlier Blender save backups |
| `web/` | Self-contained Three.js preview and its `assets/` folder with the current GLB and MP3 |
| `docs/previews/` | Rendered stills from earlier experiments |
| `docs/archives/` | Supplied project archives kept for reference |

## Scene versions

| Version | Blender project | Export | Purpose |
| --- | --- | --- | --- |
| Animated | `irie-vibes-animated.blend` | `assets/models/exports/irie-vibes-animated.glb` | Earlier 70 BPM dance rebuilt from the OBJ |
| Poseable | `irie-vibes-poseable.blend` | `assets/models/exports/irie-vibes-poseable.glb` | Rig rebuilt from the original GLB, with named action slots |
| Open Mind | `irie-vibes-openmind.blend` | `web/assets/models/irie-vibes-openmind.glb` | Current grounded dance at a 77.5 BPM half-time pulse |

All projects are in `blender/projects/`. The poseable and Open Mind versions have five visible meshes and a 29-bone armature. The source GLB has no objects named `*_outline`, so the builders preserve its colored materials and rim details.

The `toprock`, `headspin`, `windmill`, `freeze`, and `bass_drop` actions are prepared slots, not finished dance clips. The current dance is an eight-beat loop. It follows a measured pulse of this one track; it does not analyze arbitrary music live.

## Rebuild the Blender files

Run these from the repository root with Blender 5.2 installed at the path shown:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python .\blender\scripts\build_mascot.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python .\blender\scripts\build_poseable.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python .\blender\scripts\build_openmind.py
```

Each script reads its source model from `assets/models/source/` and writes its `.blend` to `blender/projects/`. The Open Mind builder reads the MP3 from `web/assets/audio/` and exports its GLB to `web/assets/models/`. Deploy the entire `web/` folder to keep its asset paths intact. The GLB contains the animation and rig, but audio is a separate file on the web.
