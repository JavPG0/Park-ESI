import json
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
        with open("data/parking_slots.json", "r", encoding='utf-8') as f:
            self.parking_slots = json.load(f)
        
        # Cargar LLM
        self.itt = ITT()
        
        # Base de datos resultados
        self.results = []
        
        # Lector de matrículas
        self.plate_reader = PlateReader()
    
    def point_in_polygon(self, x, y, poly):
        """Detecta si un punto está dentro de un polígono"""
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
    
    def detect(self, class_file, input_dimension, conf_threshold, nms_threshold, camera_id=1):
        # Clases
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        
        target_classes = {'car'}
        
        # Captura de video
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {camera_id}")
        
        fps_start_time = time.time()
        frame_id = 0
        lock = False
        
        print(f"[VehicleDetector] Cámara {camera_id} iniciada")
        print(f"[VehicleDetector] Presiona 'o' para detener\n")
        
        try:
            while not lock:
                ret, frame = cap.read()
                if not ret:
                    break

                with open("data/results.json", "r", encoding="utf-8") as f:
                    registered_vehicles = json.load(f)
                
                frame_id += 1
                h, w = frame.shape[:2]
                
                blob = cv2.dnn.blobFromImage(
                    frame, 1/255.0,
                    (input_dimension, input_dimension),
                    swapRB=True, crop=False
                )
                self.net.setInput(blob)
                outs = self.net.forward(self.output_layers)
                
                boxes, confidences, class_ids, centers = [], [], [], []
                
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        conf = float(scores[class_id])
                        
                        if conf > conf_threshold and classes[class_id] in target_classes:
                            cx = int(detection[0] * w)
                            cy = int(detection[1] * h)
                            bw = int(detection[2] * w)
                            bh = int(detection[3] * h)
                            x = int(cx - bw / 2)
                            y = int(cy - bh / 2)
                            
                            boxes.append([x, y, bw, bh])
                            confidences.append(conf)
                            class_ids.append(class_id)
                            centers.append((cx, cy))
                
                indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
                
                # Resetear plazas
                for slot in self.parking_slots:
                    slot["occupied"] = False
                
                detected_count = 0
                
                if len(indices) > 0:
                    for i in indices.flatten():
                        x, y, bw, bh = boxes[i]
                        cx, cy = centers[i]
                        conf = confidences[i]
                        label = classes[class_ids[i]]
                        detected_count += 1
                        
                        # Dibujar bounding box
                        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                        cv2.putText(
                            frame, f"{label}: {conf:.2f}",
                            (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1
                        )
                        
                        # Detectar plaza
                        slot_id = None
                        for slot in self.parking_slots:
                            if self.point_in_polygon(cx, cy, slot["polygon"]):
                                slot["occupied"] = True
                                slot_id = slot["id"]
                                break
                        
                        crop = frame[max(0, y):y + bh, max(0, x):x + bw]
                        if crop.size == 0:
                            continue
                        
                        plate = self.plate_reader.read_plate(crop)
                        info = self.itt.describe_vehicle(crop)
                        
                        car = {
                            "plate": plate,
                            "color": info.get("color"),
                            "brand": info.get("brand"),
                            "slot_id": slot_id
                        }
                        
                        # Insertar
                        existing = any(
                            c for c in registered_vehicles if (
                                c["plate"] == car["plate"] and
                                c["color"] == car["color"] and
                                c["brand"] == car["brand"]
                                )
                        )
                        if not existing:
                            self.results.append(car)
                
                free_spaces = sum(1 for s in self.parking_slots if not s["occupied"])
                
                # Dibujar plazas
                for slot in self.parking_slots:
                    pts = np.array(slot["polygon"], dtype=np.int32)
                    color = (0, 0, 255) if slot["occupied"] else (0, 255, 0)
                    cv2.polylines(frame, [pts], True, color, 2)
                    
                    cx_slot = int(np.mean([p[0] for p in slot["polygon"]]))
                    cy_slot = int(np.mean([p[1] for p in slot["polygon"]]))
                    status = "Ocupada" if slot["occupied"] else "Libre"
                    cv2.putText(
                        frame, f"{slot['id']}: {status}",
                        (cx_slot - 25, cy_slot),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        color, 1
                    )
                
                fps = frame_id / (time.time() - fps_start_time)
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Vehiculos detectados: {detected_count}", (10, 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Espacios libres: {free_spaces}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                with open("data/results.json", "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=4, ensure_ascii=False)
                
                with open("data/parking_slots.json", "w", encoding="utf-8") as f:
                    json.dump(self.parking_slots, f, indent=4, ensure_ascii=False)
                
                cv2.imshow("Park-ESI - Detector", frame)
                if cv2.waitKey(1) & 0xFF == ord('o'):
                    lock = True
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"[VehicleDetector] ✓ Cámara {camera_id} liberada correctamente")
