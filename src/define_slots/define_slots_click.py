import cv2
import json
import numpy as np

class ParkingSlotDefiner:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.slots = []
        self.current_polygon = []
        self.frame = None
        self.slot_id = 1
        
    def mouse_callback(self, event, x, y, flags, param):
        """Callback para clicks del ratón"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Añadir punto al polígono actual
            self.current_polygon.append([x, y])
            print(f"  Punto {len(self.current_polygon)}: ({x}, {y})")
            
            # Si tenemos 4 puntos, completar la plaza
            if len(self.current_polygon) == 4:
                self.slots.append({
                    "id": self.slot_id,
                    "polygon": self.current_polygon.copy(),
                    "occupied": False
                })
                print(f"✓ Plaza {self.slot_id} definida correctamente\n")
                self.slot_id += 1
                self.current_polygon = []
    
    def draw_slots(self, frame):
        """Dibujar todas las plazas definidas"""
        display = frame.copy()
        
        # Dibujar plazas completadas
        for slot in self.slots:
            pts = np.array(slot["polygon"], dtype=np.int32)
            cv2.polylines(display, [pts], True, (0, 255, 0), 2)
            
            # Dibujar ID en el centro
            center_x = int(np.mean([p[0] for p in slot["polygon"]]))
            center_y = int(np.mean([p[1] for p in slot["polygon"]]))
            cv2.putText(display, str(slot["id"]), (center_x-10, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Dibujar polígono en progreso
        if len(self.current_polygon) > 0:
            for point in self.current_polygon:
                cv2.circle(display, tuple(point), 5, (0, 0, 255), -1)
            
            if len(self.current_polygon) > 1:
                pts = np.array(self.current_polygon, dtype=np.int32)
                cv2.polylines(display, [pts], False, (0, 255, 255), 2)
        
        # Instrucciones
        cv2.putText(display, f"Plaza {self.slot_id}/50", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(display, "Click 4 esquinas por plaza", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display, "Orden: arriba-izq, arriba-der, abajo-der, abajo-izq", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display, "'s' = guardar | 'r' = reset | 'q' = salir", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        return display
    
    def run(self):
        """Ejecutar el definidor de plazas"""
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"No se pudo abrir la cámara {self.camera_id}")
            return
        
        cv2.namedWindow("Definir Plazas de Parking")
        cv2.setMouseCallback("Definir Plazas de Parking", self.mouse_callback)
        
        print("=" * 60)
        print("DEFINIDOR DE PLAZAS DE PARKING")
        print("=" * 60)
        print("Instrucciones:")
        print("1. Haz click en las 4 esquinas de cada plaza")
        print("2. Orden: arriba-izq → arriba-der → abajo-der → abajo-izq")
        print("3. Define primero las 13 plazas superiores (1-13)")
        print("4. Luego las 12 plazas inferiores (14-25)")
        print("\nControles:")
        print("  's' = Guardar y salir")
        print("  'r' = Reiniciar (borrar todas las plazas)")
        print("  'q' = Salir sin guardar")
        print("=" * 60)
        print()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            self.frame = frame
            display = self.draw_slots(frame)
            cv2.imshow("Definir Plazas de Parking", display)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Guardar
            if key == ord('s'):
                self.save_slots()
                print("✓ Plazas guardadas correctamente")
                break
            
            
            # Reiniciar
            elif key == ord('r'):
                self.slots = []
                self.current_polygon = []
                self.slot_id = 1
                print("\nPlazas reseteadas. Empieza de nuevo.\n")
            
            # Salir
            elif key == ord('q'):
                print(" Saliendo sin guardar")
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def save_slots(self):
        """Guardar plazas en JSON"""
        with open("data/parking_slots.json", "w", encoding="utf-8") as f:
            json.dump(self.slots, f, indent=4)
        
        print(f"\n✓ {len(self.slots)} plazas guardadas en data/parking_slots.json")

if __name__ == "__main__":
    definer = ParkingSlotDefiner(camera_id=0) # Usa tu cámara principal
    definer.run()
