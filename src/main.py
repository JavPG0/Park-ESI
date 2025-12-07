from vehicle_identifier import VehicleIdentifier
from vehicle_follower import VehicleFollower

# Rutas a modelos
MODEL_CFG = "models/yolov4-tiny.cfg"
MODEL_WEIGHTS = "models/yolov4-tiny.weights"
CLASS_FILE = "models/coco.names"

# Parámetros
CONF_THRESHOLD = 0.1
NMS_THRESHOLD = 0.4
INPUT_DIMENTSION = 416 # 320, 416*, 512, 640, 1280

def main():
    tipo = input("Seleccione el tipo de cámara (0: Identificación|1: Seguimiento): ")
    while tipo != 0 or tipo != 1:
        match tipo:
            case "0":
                vi = VehicleIdentifier(MODEL_CFG, MODEL_WEIGHTS)
                vi.identify(CLASS_FILE, INPUT_DIMENTSION, CONF_THRESHOLD, NMS_THRESHOLD)
            case "1":
                vf = VehicleFollower(MODEL_CFG, MODEL_WEIGHTS)
                vf.follow(CLASS_FILE, INPUT_DIMENTSION, CONF_THRESHOLD, NMS_THRESHOLD)
            case _:
                tipo = input("Opción inválida.\nSeleccione el tipo de cámara (0: Identificación|1: Seguimiento): ")

if __name__ == "__main__":
    main()
