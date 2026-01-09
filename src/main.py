# main.py - Punto de entrada del sistema Park-ESI con múltiples cámaras
from vehicle_detector import VehicleDetector
from vehicle_identifier import VehicleIdentifier
import multiprocessing
import time

# Configuración de modelos YOLO
MODEL_CFG = "models/yolov4-tiny.cfg"
MODEL_WEIGHTS = "models/yolov4-tiny.weights"
CLASS_FILE = "models/coco.names"

# Parámetros de detección
CONF_THRESHOLD = 0.1    # Umbral de confianza mínimo
NMS_THRESHOLD = 0.4     # Supresión de No-Máximos
INPUT_DIMENSION = 416   # Dimensión de entrada para YOLO

def run_detector(camera_id):
    # Proceso 1: Detecta vehículos y monitoriza plazas de parking
    try:
        print(f"[PROCESO 1] Iniciando VehicleDetector en cámara {camera_id}")
        vd = VehicleDetector(MODEL_CFG, MODEL_WEIGHTS)
        vd.detect(CLASS_FILE, INPUT_DIMENSION, CONF_THRESHOLD, NMS_THRESHOLD, camera_id)
    except Exception as e:
        print(f"[ERROR PROCESO 1] {e}")

def run_identifier(camera_id):
    # Proceso 2: Identifica y registra nuevos vehículos
    try:
        print(f"[PROCESO 2] Iniciando VehicleIdentifier en cámara {camera_id}")
        vi = VehicleIdentifier(MODEL_CFG, MODEL_WEIGHTS)
        vi.identify(CLASS_FILE, INPUT_DIMENSION, CONF_THRESHOLD, NMS_THRESHOLD, camera_id)
    except Exception as e:
        print(f"[ERROR PROCESO 2] {e}")

def main():
    # Configuración de cámaras (ajustar según disponibilidad)
    CAMERA_DETECTOR = 2     # Cámara para monitorización del parking
    CAMERA_IDENTIFIER = 0   # Cámara para identificación de vehículos
    
    print("Park-ESI - Sistema Multi-Cámara")
    
    # Crear procesos independientes para cada cámara
    process_detector = multiprocessing.Process(
        target=run_detector,
        args=(CAMERA_DETECTOR,),
        name="DetectorProcess"
    )
    
    process_identifier = multiprocessing.Process(
        target=run_identifier,
        args=(CAMERA_IDENTIFIER,),
        name="IdentifierProcess"
    )
    
    # Iniciar detector primero
    process_detector.start()
    time.sleep(3)  # Delay para evitar conflictos al cargar modelos
    process_identifier.start()
    
    print("[INFO] Ambos procesos iniciados")
    print("[INFO] Presiona 'o' en cualquier ventana o Ctrl+C para detener\n")
    
    try:
        # Esperar a que terminen ambos procesos
        process_detector.join()
        process_identifier.join()
    except KeyboardInterrupt:
        # Manejo de interrupción del Ctrl+C
        print("\n[INFO] Deteniendo procesos...")
        process_detector.terminate()
        process_identifier.terminate()
        process_detector.join()
        process_identifier.join()
    
    print("\n[INFO] Programa finalizado correctamente")

if __name__ == "__main__":
    # Usar 'spawn' para evitar conflictos con CUDA/PyTorch en multiprocessing
    multiprocessing.set_start_method('spawn', force=True)
    main()
