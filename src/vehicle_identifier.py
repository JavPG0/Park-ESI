
# vehicle_identifier.py - VERSIÓN COMPLETA CORREGIDA
import json
import os
import cv2
import numpy as np
from itt import ITT
from plate_reader import PlateReader

class VehicleIdentifier:
    def __init__(self, model_cfg, model_weights):
        # Cargar modelo YOLO
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        
        # Obtener capas de salida
        ln = self.net.getLayerNames()
        layer_indices = self.net.getUnconnectedOutLayers()
        if isinstance(layer_indices[0], (list, np.ndarray)):
            layer_indices = [i[0] for i in layer_indices]
        self.output_layers = [ln[i - 1] for i in layer_indices]
        
        # Cargar modelos auxiliares
        self.itt = ITT()
        self.plate_reader = PlateReader()
        
        # Resultado acumulado
        self.results = []
        os.makedirs("output", exist_ok=True)
        self.json_path = "output/vehicles.json"
    
    def identify(self, class_file, input_dimension, conf_threshold, nms_threshold, camera_id=3):
        # Leer clases de YOLO
        with open(class_file, "r", encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        
        target_classes = {"car"}
        
        # Captura de vídeo
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {camera_id}")
        
        print(f"[VehicleIdentifier] Cámara {camera_id} iniciada")
        print(f"[VehicleIdentifier] Presiona 'o' para detener\n")
        
        running = True
        frame_count = 0
        
        try:
            while running:
                ret, frame = cap.read()
                if not ret:
                    print(f"[VehicleIdentifier] No se pudo leer frame")
                    break
                
                frame_count += 1
                h, w = frame.shape[:2]
                
                # Forward del YOLO
                blob = cv2.dnn.blobFromImage(frame, 1/255.0, (input_dimension, input_dimension), 
                                            swapRB=True, crop=False)
                self.net.setInput(blob)
                outs = self.net.forward(self.output_layers)
                
                boxes = []
                confidences = []
                class_ids = []
                
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
                
                # NMS
                indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
                
                detected_count = 0
                
                # Analizar vehículos detectados
                if len(indices) > 0:
                    for _, i in enumerate(indices.flatten()):
                        x, y, bw, bh = boxes[i]
                        label = classes[class_ids[i]]
                        conf = confidences[i]
                        
                        detected_count += 1
                        
                        # Dibujar detección en el frame
                        color = (255, 0, 0)
                        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
                        text = f"{label}: {conf:.2f}"
                        cv2.putText(frame, text, (x, y - 5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        
                        # Recortar imagen del vehículo
                        crop = frame[max(0, y):max(0, y + bh),
                                   max(0, x):max(0, x + bw)]
                        
                        if crop.size == 0:
                            continue
                        
                        # Leer matrícula
                        plate = self.plate_reader.read_plate(crop)
                        
                        # Descripción del coche (color y marca)
                        info = self.itt.describe_vehicle(crop)
                        
                        # Guardar resultado
                        vehicle_data = {
                            "plate": plate,
                            "color": info["color"],
                            "brand": info["brand"]
                        }
                        
                        # Evitar duplicados por matrícula
                        if plate:
                            already_exists = any(v.get("plate") == plate for v in self.results)
                            if not already_exists:
                                self.results.append(vehicle_data)
                                print(f"[VehicleIdentifier] Nuevo vehículo: {plate} - {info['color']} {info['brand']}")
                        else:
                            self.results.append(vehicle_data)
                
                # Guardar en JSON
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=4)
                
                # Información en pantalla
                cv2.putText(frame, f"Vehiculos detectados: {detected_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Vehiculos registrados: {len(self.results)}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Frames: {frame_count}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Mostrar detección
                cv2.imshow("Park-ESI - Identifier", frame)
                
                # Salir al pulsar "o"
                if cv2.waitKey(1) & 0xFF == ord('o'):
                    running = False
                    print(f"[VehicleIdentifier] Cerrando cámara {camera_id}...")
        
        except KeyboardInterrupt:
            print(f"\n[VehicleIdentifier] Interrupción detectada (Ctrl+C), cerrando cámara {camera_id}...")
        
        except Exception as e:
            print(f"[VehicleIdentifier] Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Liberar recursos correctamente
            cap.release()
            cv2.destroyAllWindows()
            print(f"[VehicleIdentifier]  Cámara {camera_id} liberada correctamente")
            print(f"[VehicleIdentifier]  Total vehículos identificados: {len(self.results)}")