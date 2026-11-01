import * as THREE from "three";
import type { FatigueResult } from "../data-model.ts";

export function createFatigueViewer3D(container: HTMLElement): {
  update: (res: FatigueResult, plateThicknessMm: number) => void;
} {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070a10);

  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
  camera.position.set(160, 110, 180);
  camera.lookAt(0, 20, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  container.appendChild(renderer.domElement);

  const ambient = new THREE.AmbientLight(0xffffff, 0.72);
  const dir = new THREE.DirectionalLight(0xffffff, 0.9);
  dir.position.set(120, 180, 140);
  scene.add(ambient, dir);

  const group = new THREE.Group();
  scene.add(group);

  const resize = () => {
    const w = container.clientWidth || 640;
    const h = container.clientHeight || 480;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener("resize", resize);
  setTimeout(resize, 0);

  const animate = () => {
    requestAnimationFrame(animate);
    group.rotation.y += 0.003;
    renderer.render(scene, camera);
  };
  animate();

  return {
    update(res: FatigueResult, plateThicknessMm: number) {
      while (group.children.length > 0) group.remove(group.children[0]);

      // Placa base
      const baseGeo = new THREE.BoxGeometry(160, plateThicknessMm, 80);
      const baseMat = new THREE.MeshStandardMaterial({
        color: 0x475569,
        roughness: 0.4,
      });
      const basePlate = new THREE.Mesh(baseGeo, baseMat);
      basePlate.position.set(0, -plateThicknessMm / 2, 0);
      group.add(basePlate);

      // Placa vertical (unión en T)
      const vertGeo = new THREE.BoxGeometry(16, 80, 80);
      const vertPlate = new THREE.Mesh(vertGeo, baseMat);
      vertPlate.position.set(0, 40, 0);
      group.add(vertPlate);

      // Cordón de soldadura triangular / prisma
      const weldGeo = new THREE.CylinderGeometry(8, 8, 80, 4);
      const weldMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
      const weld1 = new THREE.Mesh(weldGeo, weldMat);
      weld1.position.set(8, 4, 0);
      weld1.rotation.x = Math.PI / 2;
      group.add(weld1);

      // Puntos / gradiente de tensión hot-spot sobre la superficie
      const sMax = Math.max(res.hotspotStressMpa, 1);
      res.nodes.forEach((n) => {
        const ratio = Math.min(1, n.stressMpa / sMax);
        const color = new THREE.Color().setHSL(0.65 * (1 - ratio), 0.9, 0.5);
        const ptGeo = new THREE.SphereGeometry(1.6, 12, 12);
        const ptMat = new THREE.MeshBasicMaterial({ color });
        const pt = new THREE.Mesh(ptGeo, ptMat);
        pt.position.set(8 + n.distFromToeMm, 0.5, 0);
        group.add(pt);
      });

      // Frente de grieta semi-elíptica en el pie del cordón
      const crackDepth = Math.min(plateThicknessMm * 0.9, res.finalCrackMm);
      const crackGeo = new THREE.CylinderGeometry(crackDepth * 0.5, crackDepth, crackDepth, 16);
      const crackMat = new THREE.MeshStandardMaterial({
        color: 0xf43f5e,
        roughness: 0.2,
      });
      const crack = new THREE.Mesh(crackGeo, crackMat);
      crack.rotation.z = Math.PI / 2;
      crack.position.set(8 + crackDepth / 2, -crackDepth / 2, 0);
      group.add(crack);
    },
  };
}
