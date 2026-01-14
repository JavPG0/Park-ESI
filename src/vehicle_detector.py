# vehicle_detector.py - VERSIÓN CORREGIDA
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
        with open("data/parking_slots.json", "r", encoding='utf-8') as f:
            self.parking_slots = json.load(f)
        
        # Cargar LLM
        self.itt = ITT()
        
        # Base de datos resultados
        self.results = []
        
        # Cargamos el lector de matrículas
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
        # Extraer qué vehículos se deben de identificar
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        
        target_classes = {'car'}
        
        # Iniciar captura de video
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {camera_id}")
        
        # Para medir FPS
        fps_start_time = time.time()
        frame_id = 0
        lock = False
        
        print(f"[VehicleDetector] Cámara {camera_id} iniciada")
        print(f"[VehicleDetector] Presiona 'o' para detener\n")
        
        try:
            # Ciclo de reconocimiento
            while not lock:
                ret, frame = cap.read()
                if not ret:
                    print(f"[VehicleDetector] No se pudo leer frame")
                    break
                
                frame_id += 1
                h, w = frame.shape[:2]
                
                # Crear blob y forward
                blob = cv2.dnn.blobFromImage(frame, 1/255.0, (input_dimension, input_dimension), 
                                            swapRB=True, crop=False)
                self.net.setInput(blob)
                outs = self.net.forward(self.output_layers)
                
                boxes = []
                confidences = []
                class_ids = []
                centers = []
                
                # Procesar detecciones
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

                # Resetear estado de plazas
                for slot in self.parking_slots:
                    slot["occupied"] = False
                
                detected_count = 0
                
                # Procesar vehículos detectados
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
                        cv2.putText(frame, text, (x, y - 5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        
                        # Marcar plaza ocupada
                        for slot in self.parking_slots:
                            if self.point_in_polygon(cx, cy, slot["polygon"]):
                                slot["occupied"] = True
                                break
                        
                        # Recortar imagen
                        crop = frame[max(0, y):max(0, y) + bh,
                                   max(0, x):max(0, x) + bw]
                        
                        if crop.size != 0:
                            # Leer matrícula
                            plate = self.plate_reader.read_plate(crop)
                            
                            # Obtener características del vehículo con el LLM
                            info = self.itt.describe_vehicle(crop)
                            
                            car = {
                                "plate": plate,
                                "color": info["color"],
                                "brand": info["brand"]
                            }

                            # Guardar resultados en JSON
                            if car not in self.results:
                                self.results.append(car)
                
                # Contar espacios libres
                free_spaces = sum(1 for slot in self.parking_slots if not slot.get("occupied", False))
                
                # Dibujar las plazas de parking
                for slot in self.parking_slots:
                    pts = np.array(slot["polygon"], dtype=np.int32)
                    color = (0, 0, 255) if slot.get("occupied", False) else (0, 255, 0)
                    cv2.polylines(frame, [pts], True, color, 2)
                    
                    # Texto de estado
                    cx_slot = int(np.mean([p[0] for p in slot["polygon"]]))
                    cy_slot = int(np.mean([p[1] for p in slot["polygon"]]))
                    status = "Ocupada" if slot.get("occupied", False) else "Libre"
                    cv2.putText(frame, f"{slot['id']}: {status}", (cx_slot-25, cy_slot),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
                # Calcular FPS
                fps_end_time = time.time()
                time_diff = fps_end_time - fps_start_time
                fps = frame_id / time_diff if time_diff > 0 else 0.0
                
                # Información en pantalla
                cv2.putText(frame, f"FPS: {fps:.2f}", (10, 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Vehiculos detectados: {detected_count}", (10, 45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Espacios libres: {free_spaces}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Guardar JSON con los resultados
                output_json_path = f"{self.output_folder}/"
                with open(f"data/results.json", "w") as f:
                    json.dump(self.results, f, indent=4)
                
                with open("data/parking_slots.json", "w") as f:
                    json.dump(self.parking_slots, f, indent=4)
                
                # Mostrar detección
                cv2.imshow("Park-ESI - Detector", frame)
                
                # Salir del programa si se presiona la tecla 'o'
                if cv2.waitKey(1) & 0xFF == ord('o'):
                    lock = True
                    print(f"[VehicleDetector] Cerrando cámara {camera_id}...")
        
        except KeyboardInterrupt:
            print(f"\n[VehicleDetector] Interrupción detectada, cerrando cámara {camera_id}...")
        
        except Exception as e:
            print(f"[VehicleDetector] Error: {e}")
        
        finally:
            # Liberar recursos
            cap.release()
            cv2.destroyAllWindows()
            print(f"[VehicleDetector] ✓ Cámara {camera_id} liberada correctamente")
