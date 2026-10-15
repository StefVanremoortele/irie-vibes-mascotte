import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const stage = document.querySelector('#stage');
const status = document.querySelector('#status');
const music = document.querySelector('#music');
const beatOffsetSeconds = 30 / 31; // The Blender sound strip begins 30 frames before animation frame 0.
const danceClipName = 'hip_shake_openmind_77_5bpm';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.append(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xfff4d7, 0x345249, 2.3));
const key = new THREE.DirectionalLight(0xffffff, 3);
key.position.set(2, 4, 4);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
scene.add(key);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(200, 200),
  new THREE.ShadowMaterial({ color: 0x06100c, opacity: 0.28 }),
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.015;
floor.receiveShadow = true;
scene.add(floor);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI * 0.9;

let mixer;
function resize() {
  const width = stage.clientWidth;
  const height = stage.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
window.addEventListener('resize', resize);
resize();

try {
  const gltf = await new GLTFLoader().loadAsync('./assets/models/irie-vibes-openmind.glb');
  const clip = gltf.animations.find((item) => item.name === danceClipName);
  if (!clip) throw new Error(`Dance clip “${danceClipName}” is missing from the GLB.`);

  scene.add(gltf.scene);
  gltf.scene.traverse((object) => {
    if (object.isMesh) object.castShadow = true;
  });

  const bounds = new THREE.Box3().setFromObject(gltf.scene);
  const center = bounds.getCenter(new THREE.Vector3());
  const height = bounds.getSize(new THREE.Vector3()).y;
  controls.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(height * 1.4, height * 0.75, height * 2.8));
  camera.lookAt(center);
  controls.update();

  mixer = new THREE.AnimationMixer(gltf.scene);
  mixer.clipAction(clip).play();
  status.textContent = 'Ready — press play';
} catch (error) {
  console.error(error);
  status.textContent = `Could not load the mascot: ${error.message}`;
}

function render() {
  requestAnimationFrame(render);
  if (mixer) mixer.setTime(Math.max(0, music.currentTime - beatOffsetSeconds));
  controls.update();
  renderer.render(scene, camera);
}
render();

music.addEventListener('play', () => { status.textContent = 'Dancing to Open Mind'; });
music.addEventListener('pause', () => { status.textContent = 'Paused'; });
music.addEventListener('error', () => { status.textContent = 'Could not load openmindaudio.mp3'; });
