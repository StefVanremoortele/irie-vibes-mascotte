# Irie Vibes animated mascot

Open `irie-vibes-animated.blend` in Blender and press **Space** to play the 4-second loop. Select `Irie Vibes | Armature` and enter **Pose Mode** to edit the bones and their keyframes. The hips alternate sides on a 120 BPM beat, the upper body counters the sway, and the speaker cone punches forward on each bass hit. The shin bones bend toward the boots to keep them close to the floor.

`irie-vibes-animated.glb` contains the colored mesh and idle animation for a game engine or web viewer. `irie-vibes-peeking.mtl` also gives the original OBJ its color palette in other importers.

To rebuild after changing the OBJ or script:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python .\build_mascot.py
```

The rig has 20 bones and vertex weights on every mesh part. The curved arm and leg tubes blend across upper and lower bones; gloves, boots, facial details, and speaker components have rigid weights. The build script replaces the source limb tubes with attached curves and uses the original `.mtl` colors.
"# irie-vibes-mascotte" 
