import json
import os

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


class VehicleFollower:

    def __init__(self, model_cfg, model_weights):

        # --- Cargar YOLO ---
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        ln = self.net.getLayerNames()
        layer_indices = self.net.getUnconnectedOutLayers()
        if isinstance(layer_indices[0], (list, np.ndarray)):
            layer_indices = [i[0] for i in layer_indices]
        self.output_layers = [ln[i - 1] for i in layer_indices]

        # --- Cargar plazas de parking ---
        with open("data/parking_slots.json", "r", encoding='utf-8') as f:
            self.parking_slots = json.load(f)

        # --- Cargar coches registrados ---
        self.registered_cars = self.load_registered_cars()

        # Estado interno: qué coche está en qué plaza
        self.car_locations = {}     # {plate: slot_id o None}


    def load_registered_cars(self):
        """Carga la lista de vehículos detectados por vehicle_identifier"""
        path = "output/vehicles.json"

        if not os.path.exists(path):
            print("[WARNING] No existe vehicles.json todavía.")
            return []

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


    def point_in_polygon(self, x, y, poly):
        """Comprueba si un punto está dentro de un polígono"""
        inside = False
        n = len(poly)

        px1, py1 = poly[0]
        for i in range(n + 1):
            px2, py2 = poly[i % n]
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2

        return inside


    def compare_crops(self, crop1, crop2):
        """Devuelve similitud estructural entre dos imágenes"""
        crop1 = cv2.resize(crop1, (200, 200))
        crop2 = cv2.resize(crop2, (200, 200))

        gray1 = cv2.cvtColor(crop1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(crop2, cv2.COLOR_BGR2GRAY)

        score, _ = ssim(gray1, gray2, full=True)
        return score


    def match_registered_car(self, crop):
        """Encuentra cuál de los coches registrados coincide mejor con el crop detectado."""

        best_score = 0
        best_car = None

        for car in self.registered_cars:
            img_path = car.get("image_file")
            if not img_path or not os.path.exists(img_path):
                continue

            known_crop = cv2.imread(img_path)
            if known_crop is None:
                continue

            score = self.compare_crops(crop, known_crop)

            if score > best_score:
                best_score = score
                best_car = car

        if best_score > 0.55:  # Umbral razonable para SSIM
            return best_car
        else:
            return None


    def follow(self, class_file, input_dimension, conf_threshold, nms_threshold, camera_id=0):
        # Leer clases YOLO
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        target_classes = {'car'}

        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")

        running = True

        while running:

            ret, frame = cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]

            # Detección
            blob = cv2.dnn.blobFromImage(frame, 1/255, (input_dimension, input_dimension), swapRB=True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            boxes = []
            confidences = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    conf = float(scores[class_id])

                    if conf > conf_threshold:
                        class_name = classes[class_id]
                        if class_name in target_classes:
                            cx = int(detection[0] * w)
                            cy = int(detection[1] * h)
                            bw = int(detection[2] * w)
                            bh = int(detection[3] * h)
                            x = int(cx - bw / 2)
                            y = int(cy - bh / 2)

                            boxes.append([x, y, bw, bh])
                            confidences.append(conf)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

            # Para cada coche detectado, determinar cuál es
            if len(indices) > 0:
                for i in indices.flatten():

                    x, y, bw, bh = boxes[i]
                    cx = x + bw // 2
                    cy = y + bh // 2

                    crop = frame[max(0, y):y + bh, max(0, x):x + bw]
                    if crop.size == 0:
                        continue

                    # Identificar qué coche registrado es
                    car = self.match_registered_car(crop)

                    if car is None:
                        continue  # coche desconocido → no seguir

                    plate = car["plate"]

                    # Comprobar si está en alguna plaza
                    in_slot = None
                    for slot in self.parking_slots:
                        if self.point_in_polygon(cx, cy, slot["polygon"]):
                            in_slot = slot["id"]
                            break

                    self.car_locations[plate] = in_slot

            # Guardar estado actualizado
            with open("data/following_status.json", "w", encoding="utf-8") as f:
                json.dump(self.car_locations, f, indent=4)

            # Salir con "o"
            if cv2.waitKey(1) & 0xFF == ord('o'):
                running = False

        cap.release()
        cv2.destroyAllWindows()
