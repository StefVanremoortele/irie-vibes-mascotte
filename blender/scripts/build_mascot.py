"""Build an animated Blender scene and GLB from irie-vibes-peeking.obj.

Run from repository root: blender --background --python blender/scripts/build_mascot.py
"""

from pathlib import Path
import math

import bpy
from mathutils import Matrix, Vector


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "assets/models/source/irie-vibes-peeking.obj"
BLEND = REPO_ROOT / "blender/projects/irie-vibes-animated.blend"
GLB = REPO_ROOT / "assets/models/exports/irie-vibes-animated.glb"
FRAME_SCALE = 2  # Double the authored frame spacing; 28 fps makes each beat 70 BPM.
FPS = 28


def dance_frame(frame):
    return (frame - 1) * FRAME_SCALE

def imported_axes(point):
    """Map original OBJ X/Y/Z to the importer's Blender X/Y/Z."""
    x, y, z = point
    return (-x, z, y)


def control(name, location, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "CIRCLE"
    obj.empty_display_size = 0.12
    obj.location = imported_axes(location)
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj


def attach(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()


def animate(obj, path, values):
    for frame, value in values:
        if path == "location":
            value = imported_axes(value)
        setattr(obj, path, value)
        obj.keyframe_insert(data_path=path, frame=dance_frame(frame))


def radians(values):
    return tuple(math.radians(v) for v in values)


def aim(obj, point):
    direction = Vector(point) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def tube(name, points, radius, mat):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 48
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, position in zip(spline.bezier_points, points):
        point.co = imported_axes(position)
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.data.materials.append(mat)
    return obj


if not SOURCE.exists():
    raise FileNotFoundError(SOURCE)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.obj_import(filepath=str(SOURCE), forward_axis="Z", up_axis="Y")
parts = {obj.name: obj for obj in bpy.context.selected_objects if obj.type == "MESH"}
if len(parts) < 50:
    raise RuntimeError(f"Expected separate mascot parts; found {len(parts)} meshes")

# Use the source MTL directly, including its color and surface settings.
palette = {}
for obj in parts.values():
    for slot in obj.material_slots:
        if slot.material:
            palette[slot.material.name.split(".")[0]] = slot.material
    if not obj.material_slots:
        raise RuntimeError(f"Missing material assignment on {obj.name}")
if "dark_brown" not in palette:
    raise RuntimeError("Source MTL must define dark_brown for the replacement limbs")

# The source limb tubes run across the face and one leg crosses to the opposite
# boot. Replace those four rigid tubes with clean, attached curves. Keep the
# source gloves and boots, moved as complete groups below.
for name in ("arm_left", "arm_right", "leg_left", "leg_right"):
    bpy.data.objects.remove(parts.pop(name), do_unlink=True)
parts["arm_left"] = tube("arm_left", [
    (-0.51, 0.76, 0.12), (-0.62, 0.77, 0.02), (-0.67, 0.86, -0.07),
    (-0.62, 0.89, -0.08),
], 0.034, palette["dark_brown"])
parts["arm_right"] = tube("arm_right", [
    (0.30, 0.73, -0.12), (0.38, 0.70, 0.07), (0.51, 0.70, 0.17),
    (0.58, 0.83, 0.22),
], 0.034, palette["dark_brown"])
parts["leg_left"] = tube("leg_left", [
    (-0.28, 0.31, -0.02), (-0.31, 0.22, -0.06), (-0.32, 0.13, -0.08),
], 0.034, palette["dark_brown"])
parts["leg_right"] = tube("leg_right", [
    (0.06, 0.32, -0.07), (0.09, 0.23, 0.00), (0.07, 0.15, 0.04),
], 0.034, palette["dark_brown"])

root = control("CTRL | Body bob / lean", (0, 0, 0))
# The OBJ importer converts its Y-up coordinates into Blender's Z-up space.
hip = control("CTRL | Hip shake", (-0.10, 0.30, -0.02), root)
bpy.context.view_layer.update()
speaker = control("CTRL | Speaker pulse", (-0.105, 0.728, -0.01), hip)
left_arm = control("CTRL | Left arm wave", (-0.51, 0.76, 0.12), hip)
right_arm = control("CTRL | Right arm wave", (0.30, 0.73, -0.12), hip)
left_eye = control("CTRL | Left eye look", (0.045, 0.83, -0.057), hip)
right_eye = control("CTRL | Right eye look", (-0.149, 0.913, 0.007), hip)
left_lid = control("CTRL | Left blink", (0.073, 0.884, -0.083), hip)
right_lid = control("CTRL | Right blink", (-0.125, 0.974, -0.017), hip)
left_foot = control("CTRL | Left foot tap", (-0.32, 0.13, -0.08), hip)
right_foot = control("CTRL | Right foot tap", (0.07, 0.15, 0.04), hip)

bpy.context.view_layer.update()
for name, obj in parts.items():
    if name.startswith("glove_left"):
        obj.location = imported_axes((-0.631, 0.294, -0.455))
    elif name.startswith("glove_right"):
        obj.location = imported_axes((0.586, -0.285, -0.157))
    parent = hip
    if name in {"cone", "cone_ripple_0", "cone_ripple_1", "dust_cap"}:
        parent = speaker
    elif name.startswith("arm_left") or name.startswith("glove_left"):
        parent = left_arm
    elif name.startswith("arm_right") or name.startswith("glove_right"):
        parent = right_arm
    elif name in {"eye_left_pupil", "eye_left_shine"}:
        parent = left_eye
    elif name in {"eye_right_pupil", "eye_right_shine"}:
        parent = right_eye
    elif name == "eye_left_lid":
        parent = left_lid
    elif name == "eye_right_lid":
        parent = right_lid
    elif name.startswith("boot_left"):
        parent = left_foot
    elif name.startswith("boot_right"):
        parent = right_foot
    attach(obj, parent)

# Eight-beat loop at 70 BPM: alternating hip accents every 24 frames.
animate(root, "location", [(1, (0, 0, 0)), (25, (0, 0.025, 0)),
                           (49, (0, 0, 0)), (73, (0, -0.014, 0)), (97, (0, 0, 0))])
animate(root, "rotation_euler", [
    (1, radians((0, 0, 0))), (25, radians((0, 0, 2))),
    (49, radians((0, 0, 0))), (73, radians((0, 0, -2))),
    (97, radians((0, 0, 0))),
])
hip_home = (-0.10, 0.30, -0.02)
hip_steps = [(frame, math.cos(2 * math.pi * (frame - 1) / 24))
             for frame in range(1, 98, 6)]
animate(hip, "location", [
    (frame, (hip_home[0] + 0.11 * swing, hip_home[1], hip_home[2]))
    for frame, swing in hip_steps
])
animate(hip, "rotation_euler", [
    (frame, radians((0, 8 * swing, 15 * swing)))
    for frame, swing in hip_steps
])
speaker_rest = (-0.105, 0.728, -0.01)
speaker_hit = (-0.105, 0.728, 0.045)
speaker_positions = []
speaker_scales = []
for start in range(1, 97, 12):
    speaker_positions.extend([(start, speaker_hit), (start + 5, speaker_rest)])
    speaker_scales.extend([(start, (1.05, 1.05, 1.05)),
                           (start + 5, (1, 1, 1))])
speaker_positions.append((97, speaker_hit))
speaker_scales.append((97, (1.05, 1.05, 1.05)))
animate(speaker, "location", speaker_positions)
animate(speaker, "scale", speaker_scales)
animate(left_arm, "rotation_euler", [
    (1, radians((0, 0, 0))), (25, radians((0, 9, -4))),
    (49, radians((0, 0, 0))), (73, radians((0, -5, 2))),
    (97, radians((0, 0, 0))),
])
# Repeat the arm's high pose at both ends so it flows through the loop seam.
animate(right_arm, "rotation_euler", [
    (1, radians((0, 9, -4))), (17, radians((0, -12, 5))),
    (33, radians((0, 9, -4))), (49, radians((0, -12, 5))),
    (65, radians((0, 9, -4))), (81, radians((0, -12, 5))),
    (97, radians((0, 9, -4))),
])
for eye, home in [(left_eye, (0.045, 0.83, -0.057)),
                  (right_eye, (-0.149, 0.913, 0.007))]:
    animate(eye, "location", [(1, home), (28, home),
                              (38, (home[0] + 0.014, home[1], home[2])),
                              (59, (home[0] + 0.014, home[1], home[2])),
                              (69, home), (97, home)])
for lid, home in ((left_lid, (0.073, 0.884, -0.083)),
                  (right_lid, (-0.125, 0.974, -0.017))):
    animate(lid, "location", [(1, home), (44, home),
                              (47, (home[0], home[1] - 0.045, home[2])),
                              (50, home), (97, home)])
animate(left_foot, "rotation_euler", [(1, (0, 0, 0)),
    (25, radians((7, 0, 0))), (49, (0, 0, 0)), (97, (0, 0, 0))])
animate(right_foot, "rotation_euler", [(1, (0, 0, 0)),
    (49, (0, 0, 0)), (73, radians((7, 0, 0))), (97, (0, 0, 0))])

scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = dance_frame(97) - 1
scene.render.fps = FPS
scene.frame_set(0)
bpy.context.view_layer.update()

# Bake the editable control hierarchy into a real armature. Each glove, boot,
# facial detail, and speaker part is skinned to its corresponding bone. The
# curved arms and legs blend across two bones so elbows and knees can be posed.
bone_specs = [
    # name, parent, head, tail, source control
    ("root", None, (0, 0, 0), (0, 0.12, 0), root),
    ("hips", "root", (-0.10, 0.30, -0.02), (-0.10, 0.43, -0.02), hip),
    ("body", "hips", (-0.10, 0.43, -0.02), (-0.10, 1.12, -0.02), hip),
    ("upper_arm.L", "body", (-0.51, 0.76, 0.12), (-0.62, 0.77, 0.02), left_arm),
    ("forearm.L", "upper_arm.L", (-0.62, 0.77, 0.02), (-0.62, 0.89, -0.08), left_arm),
    ("hand.L", "forearm.L", (-0.62, 0.89, -0.08), (-0.62, 0.95, -0.08), left_arm),
    ("upper_arm.R", "body", (0.30, 0.73, -0.12), (0.38, 0.70, 0.07), right_arm),
    ("forearm.R", "upper_arm.R", (0.38, 0.70, 0.07), (0.58, 0.83, 0.22), right_arm),
    ("hand.R", "forearm.R", (0.58, 0.83, 0.22), (0.58, 0.89, 0.22), right_arm),
    ("thigh.L", "hips", (-0.28, 0.31, -0.02), (-0.31, 0.22, -0.06), hip),
    ("shin.L", "thigh.L", (-0.31, 0.22, -0.06), (-0.32, 0.13, -0.08), hip),
    ("foot.L", "shin.L", (-0.32, 0.13, -0.08), (-0.327, 0.06, 0.015), left_foot),
    ("thigh.R", "hips", (0.06, 0.32, -0.07), (0.09, 0.23, 0.00), hip),
    ("shin.R", "thigh.R", (0.09, 0.23, 0.00), (0.07, 0.15, 0.04), hip),
    ("foot.R", "shin.R", (0.07, 0.15, 0.04), (0.109, 0.071, 0.118), right_foot),
    ("speaker", "body", (-0.105, 0.728, -0.01), (-0.105, 0.728, 0.12), speaker),
    ("eye.L", "speaker", (0.045, 0.83, -0.057), (0.045, 0.83, 0.015), left_eye),
    ("eye.R", "speaker", (-0.149, 0.913, 0.007), (-0.149, 0.913, 0.08), right_eye),
    ("lid.L", "speaker", (0.073, 0.884, -0.083), (0.073, 0.94, -0.083), left_lid),
    ("lid.R", "speaker", (-0.125, 0.974, -0.017), (-0.125, 1.03, -0.017), right_lid),
]
rig_data = bpy.data.armatures.new("Irie Vibes skeleton")
rig = bpy.data.objects.new("Irie Vibes | Armature", rig_data)
bpy.context.collection.objects.link(rig)
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
for name, parent_name, head, tail, _ in bone_specs:
    bone = rig_data.edit_bones.new(name)
    bone.head = imported_axes(head)
    bone.tail = imported_axes(tail)
    if parent_name:
        bone.parent = rig_data.edit_bones[parent_name]
        bone.use_connect = name.startswith(("forearm.", "shin.", "hand."))
bpy.ops.object.mode_set(mode="OBJECT")


def skin_piece(obj, weights):
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = world
    for bone_name in ((weights["first"], weights["second"])
                      if isinstance(weights, dict) else (weights,)):
        obj.vertex_groups.new(name=bone_name)
    if isinstance(weights, dict):
        for index, vertex in enumerate(obj.data.vertices):
            point = obj.matrix_world @ vertex.co
            start, joint, end = weights["segment"]
            direction = end - start
            # Keep the shafts solid; blend weights only around the joint.
            along = (point - joint).dot(direction) / direction.length_squared
            blend = min(1.0, max(0.0, 0.5 + along / 0.22))
            second = blend * blend * (3 - 2 * blend)
            first = 1.0 - second
            if first:
                obj.vertex_groups[weights["first"]].add([index], first, "REPLACE")
            if second:
                obj.vertex_groups[weights["second"]].add([index], second, "REPLACE")
    else:
        obj.vertex_groups[weights].add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    modifier = obj.modifiers.new("Skeleton skin", "ARMATURE")
    modifier.object = rig
    modifier.use_deform_preserve_volume = True
    obj.parent = rig
    obj.matrix_parent_inverse = rig.matrix_world.inverted()


segments = {
    "arm_left": ("upper_arm.L", "forearm.L", (-0.51, 0.76, 0.12), (-0.62, 0.77, 0.02), (-0.62, 0.89, -0.08)),
    "arm_right": ("upper_arm.R", "forearm.R", (0.30, 0.73, -0.12), (0.38, 0.70, 0.07), (0.58, 0.83, 0.22)),
    "leg_left": ("thigh.L", "shin.L", (-0.28, 0.31, -0.02), (-0.31, 0.22, -0.06), (-0.32, 0.13, -0.08)),
    "leg_right": ("thigh.R", "shin.R", (0.06, 0.32, -0.07), (0.09, 0.23, 0.00), (0.07, 0.15, 0.04)),
}
for name, obj in parts.items():
    if name in segments:
        first, second, start, joint, end = segments[name]
        groups = {"first": first, "second": second,
                  "segment": tuple(Vector(imported_axes(p)) for p in (start, joint, end))}
    elif name.startswith("glove_left"):
        groups = "hand.L"
    elif name.startswith("glove_right"):
        groups = "hand.R"
    elif name.startswith("boot_left"):
        groups = "foot.L"
    elif name.startswith("boot_right"):
        groups = "foot.R"
    elif name in {"cone", "cone_ripple_0", "cone_ripple_1", "dust_cap",
                  "eye_left_white", "eye_right_white", "smirk",
                  "smile_dimple", "cheek_r", "cheek_l"}:
        groups = "speaker"
    elif name in {"eye_left_pupil", "eye_left_shine"}:
        groups = "eye.L"
    elif name in {"eye_right_pupil", "eye_right_shine"}:
        groups = "eye.R"
    elif name == "eye_left_lid":
        groups = "lid.L"
    elif name == "eye_right_lid":
        groups = "lid.R"
    else:
        groups = "body"
    skin_piece(obj, groups)

# Preserve the precise curve of the existing loop while making the bones the
# sole animation source. Rest matrices preserve the opening pose during baking.
rest_controls = {name: control_obj.matrix_world.copy()
                 for name, _, _, _, control_obj in bone_specs}
upper_body = {"body", "upper_arm.L", "forearm.L", "hand.L",
              "upper_arm.R", "forearm.R", "hand.R", "speaker",
              "eye.L", "eye.R", "lid.L", "lid.R"}
for pose_bone in rig.pose.bones:
    pose_bone.rotation_mode = "QUATERNION"
editable_joints = {"thigh.L", "shin.L", "thigh.R", "shin.R",
                   "forearm.L", "forearm.R", "hand.L", "hand.R"}
for frame in range(scene.frame_start, scene.frame_end + 2):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    beat = math.cos(2 * math.pi * frame / (24 * FRAME_SCALE))
    hip_delta = hip.matrix_world @ rest_controls["hips"].inverted()
    speaker_delta = speaker.matrix_world @ rest_controls["speaker"].inverted()
    speaker_pulse = speaker_delta @ hip_delta.inverted()
    hip_pivot = hip.matrix_world.translation
    body_counter = (Matrix.Translation(hip_pivot)
                    @ Matrix.Rotation(math.radians(-7 * beat), 4, "Z")
                    @ Matrix.Rotation(math.radians(-4 * beat), 4, "Y")
                    @ Matrix.Translation(-hip_pivot))
    for name, _, _, _, control_obj in bone_specs:
        bone = rig.pose.bones[name]
        desired = (control_obj.matrix_world @ rest_controls[name].inverted()
                   @ rig_data.bones[name].matrix_local)
        if name in {"eye.L", "eye.R", "lid.L", "lid.R"}:
            desired = speaker_pulse @ desired
        if name in upper_body:
            desired = body_counter @ desired
        bone.matrix = desired
        bpy.context.view_layer.update()
        if name not in editable_joints:
            bone.keyframe_insert(data_path="location", frame=frame)
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            bone.keyframe_insert(data_path="scale", frame=frame)
scene.frame_set(0)
if rig.animation_data and rig.animation_data.action:
    rig.animation_data.action.name = "Irie Vibes | Hip shake and idle"
for control_obj in (speaker, left_arm, right_arm, left_eye, right_eye,
                    left_lid, right_lid, left_foot, right_foot, hip, root):
    bpy.data.objects.remove(control_obj, do_unlink=True)
rig.show_in_front = True
rig_data.display_type = "OCTAHEDRAL"
rig_data.show_names = True

# Useful opening view and simple studio lights, excluded from GLB export.
bpy.ops.object.camera_add(location=(2.0, 3.4, 1.55))
camera = bpy.context.object
camera.name = "Preview camera"
aim(camera, (-0.1, 0, 0.65))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 2.15
scene.camera = camera
for name, position, energy, size in [
    ("Key", (1.5, 2.5, 3.0), 350, 3),
    ("Fill", (-2.0, 1.2, 1.5), 200, 2),
    ("Rim", (0.0, -1.5, 2.6), 420, 2),
]:
    bpy.ops.object.light_add(type="AREA", location=position)
    light = bpy.context.object
    light.name = f"Preview light | {name}"
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    aim(light, (-0.1, 0, 0.65))

scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.world.color = (0.10, 0.10, 0.10)

# Open the project in a clear model view instead of the default world grid.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_perspective = "CAMERA"
            space.overlay.show_extras = False
            space.overlay.show_floor = False
            space.shading.type = "SOLID"
            space.shading.color_type = "MATERIAL"

bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

# Export only the animated hierarchy, omitting preview camera and lights.
for obj in parts.values():
    obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(GLB), export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIVE_ACTIONS",
)
print(f"Created {BLEND} and {GLB} from {len(parts)} mesh parts")
