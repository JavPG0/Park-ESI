import cv2
import time
import numpy as np

from itt import ITT

class VehicleDetector:

    def __init__(self, model_cfg, model_weights):

        # Cargar modelo YOLO
        self.net = cv2.dnn.readNetFromDarknet(model_cfg, model_weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Obtener nombres de las capas
        ln = self.net.getLayerNames()
        layer_indices = self.net.getUnconnectedOutLayers()
        # Compatibilidad con distintas versiones de OpenCV

        if isinstance(layer_indices[0], list) or isinstance(layer_indices[0], np.ndarray):
            layer_indices = [i[0] for i in layer_indices]

        # Guardar las capas de salida
        self.output_layers = [ln[i - 1] for i in layer_indices]

        self.feature_extractor = ITT()

    def detect(self, class_file, input_dimension, conf_threshold, nms_threshold):

        # Cargar nombres de clases
        with open(class_file, 'r', encoding="utf-8") as f:
            classes = [line.strip() for line in f.readlines()]

        # Queremos la clase 'car' (y opcionalmente 'truck', 'bus' si interesa)
        target_classes = {'car', 'truck', 'bus'}


        # Fuente: 0 para webcam o ruta a archivo/stream
        source = 0

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la fuente de vídeo")

        # Para medir FPS
        fps_start_time = time.time()
        frame_id = 0

        lock = False

        while lock == False:
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

            # Non-maxima suppression
            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
            detected_count = 0
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, bw, bh = boxes[i]
                    label = classes[class_ids[i]]
                    conf = confidences[i]
                    detected_count += 1
                    # Dibujar caja
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # FPS
            fps_end_time = time.time()
            time_diff = fps_end_time - fps_start_time
            fps = frame_id / time_diff if time_diff > 0 else 0.0
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            cv2.putText(frame, f"Detected vehicles: {detected_count}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            vehicle_crop = frame[max(y,0):y+bh, max(x,0):x+bw]
            caption = ITT.describe_vehicle(vehicle_crop)
            cv2.putText(frame, caption, (x, y + bh + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 1)


            cv2.imshow("Car Detection - YOLOv4-tiny", frame)
            if cv2.waitKey(1) & 0xFF == ord('o'):
                lock = True

        cap.release()
        cv2.destroyAllWindows()
