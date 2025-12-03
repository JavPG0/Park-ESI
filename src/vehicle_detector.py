import json
import os
import time

import cv2
import numpy as np

from itt import ITT
from plate_reader import PlateReader

class VehicleDetector:

    def __init__(self, model_cfg, model_weights):

        # Cargar modelo YOLO
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Obtener capas
        ln = self.net.getLayerNames()
        layer_indices = self.net.getUnconnectedOutLayers()
        if isinstance(layer_indices[0], list) or isinstance(layer_indices[0], np.ndarray):
            layer_indices = [i[0] for i in layer_indices]
        self.output_layers = [ln[i - 1] for i in layer_indices]

        # Cargar plazas de parking
        with open("parking_slots.json", "r", encoding='utf-8') as f:
            self.parking_slots = json.load(f)

        # Cargar LLM
        self.itt = ITT()

        # Base de datos resultados
        self.results = []
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)

        # Para evitar duplicados
        self.processed_centers = []

        #Cagamos el lector de matrículas
        self.plate_reader = PlateReader()

        #Diccionario de matrículas ya leídas
        self.preocessed_plates = {}


    def is_duplicate(self, plate):

        '''
        MÁS ADELANTE HAY QUE CAMBIAR ESTA PARTE PARA QUE
        NO IDENTIFIQUE 2 VECES AL MISMO VEHÍCULO EN BASE
        A LA MATRÍCULA DE ESTE
        '''

        # Evitar analizar dos veces el mismo vehículo
        for (px, py) in self.processed_centers:
            if abs(px - cx) < 60 and abs(py - cy) < 60:
                return True
        return False


    def point_in_polygon(self, x, y, poly):

        inside = False
        n = len(poly)

        # Detecta qué plazas de parking contienen un vehículo
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


    def detect(self, class_file, input_dimension, conf_threshold, nms_threshold):

        # Extraer qué vehículos se deben de identificar
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        target_classes = {'car'}

        # Iniciar captura de video
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la fuente de vídeo")

        # Para medir FPS
        fps_start_time = time.time()
        frame_id = 0
        lock = False
        free_spaces = 0

        # Ciclo de reconocimiento
        while lock is False:
            ret, frame = cap.read()
            if not ret:
                break

            frame_id += 1
            h, w = frame.shape[:2]

            # Crear blob y forward
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (input_dimension, input_dimension), swapRB=True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            boxes = []
            confidences = []
            class_ids = []
            centers = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    conf = float(scores[class_id])

                    if conf > conf_threshold:
                        class_name = classes[class_id]
                        if class_name in target_classes:
                            center_x = int(detection[0] * w)
                            center_y = int(detection[1] * h)
                            bw = int(detection[2] * w)
                            bh = int(detection[3] * h)
                            x = int(center_x - bw / 2)
                            y = int(center_y - bh / 2)

                            boxes.append([x, y, bw, bh])
                            confidences.append(conf)
                            class_ids.append(class_id)
                            centers.append((center_x, center_y))

            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
            detected_count = 0

            if len(indices) > 0:
                for _, i in enumerate(indices.flatten()):
                    x, y, bw, bh = boxes[i]
                    cx, cy = centers[i]

                    label = classes[class_ids[i]]
                    conf = confidences[i]
                    detected_count += 1

                    # Dibujar caja
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                    free_spaces = 0
                    # Identificar plazas de parking
                    for slot in self.parking_slots:
                        if self.point_in_polygon(cx, cy, slot["polygon"]):
                            slot["occupied"] = True
                        else:
                            slot["occupied"] = False
                            free_spaces += 1

                    # Recortar imagen (sin recuadro)
                    crop = frame[max(0, y):max(0, y) + bh,
                                max(0, x):max(0, x) + bw]

                    if crop.size != 0:
                        # Leer matrícula
                        plate = self.plate_reader.read_plate(crop)
                        
                        # Evitar duplicados por matrícula
                        if self.is_duplicate(plate):
                            continue
                        
                        # Obtener características del vehículo con el LLM
                        info = self.itt.describe_vehicle(crop)
                        
                        # Guardar imagen recortada limpia
                        vehicle_id = len(self.results) + 1
                        img_path = f"{self.output_folder}/vehicle_{vehicle_id}.jpg"
                        cv2.imwrite(img_path, crop)
                        
                        # Registrar matrícula procesada
                        if plate:
                            self.processed_plates[plate] = vehicle_id
                        
                        # Guardar resultados en JSON
                        self.results.append({
                            "vehicle_id": vehicle_id,
                            "plate": plate,  # Matrícula leída
                            "color": info["color"],
                            "brand": info["brand"],
                            "image_file": img_path
                        })


            # Dibujar las plazas de parking
            for slot in self.parking_slots:
                pts = np.array(slot["polygon"], dtype=np.int32)

                color = (0, 255, 0) if not slot.get("occupied", False) else (0, 0, 255)

                cv2.polylines(frame, [pts], True, color, 2)

                # Texto de estado
                cx = int(np.mean([p[0] for p in slot["polygon"]]))
                cy = int(np.mean([p[1] for p in slot["polygon"]]))
                status = "Ocupada" if slot.get("occupied", False) else "Libre"
                cv2.putText(frame, f"{slot['id']}: {status}", (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            fps_end_time = time.time()
            time_diff = fps_end_time - fps_start_time
            fps = frame_id / time_diff if time_diff > 0 else 0.0
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            cv2.putText(frame, f"Vehiculos detectados: {detected_count}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            cv2.putText(frame, f"Espacios libres: {free_spaces}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            # Guardar JSON con los resultados
            output_json_path = f"{self.output_folder}/"
            with open(f"{output_json_path}results.json", "w") as f:
                json.dump(self.results, f, indent=4)
            with open("parking_slots.json", "w") as f:
                json.dump(self.parking_slots, f, indent=4)

            # Mostrar detección
            cv2.imshow("Park-ESI", frame)

            # Salir del programa si se presiona la tecla 'o'
            if cv2.waitKey(1) & 0xFF == ord('o'):
                lock = True

        # Finalizar la captura de video
        cap.release()
        cv2.destroyAllWindows()
