import json
import os
import time

import cv2
import numpy as np

from itt import ITT

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

        # Cargar
        self.itt = ITT()

        # Base de datos resultados
        self.results = []
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)

        # Para evitar duplicados
        self.processed_centers = []


    def is_duplicate(self, cx, cy):

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


    def detect(self, class_file, input_dimension, conf_threshold, nms_threshold):

        # Extraer qué vehículos se deben de identificar
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]
        target_classes = {'car', 'truck', 'bus'}

        # Iniciar captura de video
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la fuente de vídeo")

        frame_id = 0
        lock = False

        # Ciclo de reconocimiento
        while lock is False:
            ret, frame = cap.read()
            if not ret:
                break

            frame_id += 1
            h, w = frame.shape[:2]

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

            if len(indices) > 0:
                for idx, i in enumerate(indices.flatten()):
                    x, y, bw, bh = boxes[i]
                    cx, cy = centers[i]

                    # Evitar duplicados
                    if self.is_duplicate(cx, cy):
                        continue

                    # Guardar centro procesado
                    self.processed_centers.append((cx, cy))

                    # Recortar imagen (sin recuadro)
                    crop = frame[max(0, y):max(0, y) + bh,
                                max(0, x):max(0, x) + bw]

                    if crop.size != 0:

                        # Obtener características del vehículo con el LLM
                        info = self.itt.describe_vehicle(crop)

                        # Guardar imagen recortada limpia
                        vehicle_id = len(self.results) + 1
                        img_path = f"{self.output_folder}/vehicle_{vehicle_id}.jpg"
                        cv2.imwrite(img_path, crop)

                        # Guardar resultados en JSON
                        self.results.append({
                            "vehicle_id": vehicle_id,
                            "color": info["color"],
                            "brand": info["brand"],
                            "image_file": img_path
                        })

            # Mostrar detección sin texto adicional
            cv2.imshow("Car Detection - YOLOv4-tiny", frame)

            # Salir del programa si se presiona la tecla 'o'
            if cv2.waitKey(1) & 0xFF == ord('o'):
                lock = True

        # Finalizar la captura de video
        cap.release()
        cv2.destroyAllWindows()

        # Guardar JSON con los resultados
        output_json_path = f"{self.output_folder}/results.json"
        with open(output_json_path, "w") as f:
            json.dump(self.results, f, indent=4)

        print(f"Resultados guardados en {output_json_path}")
