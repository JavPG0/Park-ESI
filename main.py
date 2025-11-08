from vehicle_detector import VehicleDetector

# Ruta a modelos
MODEL_CFG = "models/yolov4-tiny.cfg"
MODEL_WEIGHTS = "models/yolov4-tiny.weights"
CLASS_FILE = "models/coco.names"

# Parámetros
CONF_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
# 320, 416, 512, 640, 1280
INPUT_DIMENTSION = 416

def main():
    vd = VehicleDetector(MODEL_CFG, MODEL_WEIGHTS)
    vd.detect(CLASS_FILE, INPUT_DIMENTSION, CONF_THRESHOLD, NMS_THRESHOLD)

if __name__ == "__main__":
    main()
