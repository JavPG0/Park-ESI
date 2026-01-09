# auto_generate_optimal_slots.py

#Define 25 plazas en la camara en horizontal arriba y abajo, no lo vamos a usar.

import json
import cv2
import numpy as np

def generate_optimal_parking_slots(camera_id=1):
    """Genera automáticamente 25 plazas con espaciado óptimo"""
    
    print("=" * 60)
    print("GENERADOR AUTOMÁTICO DE PLAZAS - ÓPTIMO")
    print("=" * 60)
    
    # Capturar frame para obtener dimensiones
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()
    
    if not ret:
        print(" Error al capturar frame de la cámara")
        cap.release()
        return
    
    height, width = frame.shape[:2]
    print(f"📹 Resolución de cámara: {width}x{height}")
    
    # PARÁMETROS OPTIMIZADOS
    MARGIN_TOP = 40          # Margen superior
    MARGIN_BOTTOM = 50       # Margen inferior  
    MARGIN_LEFT = 20         # Margen izquierdo
    MARGIN_RIGHT = 20        # Margen derecho
    GAP_BETWEEN_ROWS = 60    # Espacio entre filas (máximo)
    SLOT_GAP_H = 8           # Espacio horizontal entre plazas (máximo)
    
    slots = []
    
    # === FILA SUPERIOR: 13 PLAZAS ===
    row1_available_width = width - MARGIN_LEFT - MARGIN_RIGHT
    slot_width_row1 = (row1_available_width - (12 * SLOT_GAP_H)) / 13
    slot_height_row1 = 160  # Altura fija para fila superior
    
    print(f"\n📊 Fila Superior (13 plazas):")
    print(f"   Ancho por plaza: {slot_width_row1:.1f}px")
    print(f"   Alto: {slot_height_row1}px")
    print(f"   Separación: {SLOT_GAP_H}px")
    
    for i in range(13):
        x = MARGIN_LEFT + i * (slot_width_row1 + SLOT_GAP_H)
        y = MARGIN_TOP
        
        slots.append({
            "id": i + 1,
            "polygon": [
                [int(x), int(y)],                                    # Top-left
                [int(x + slot_width_row1), int(y)],                 # Top-right
                [int(x + slot_width_row1), int(y + slot_height_row1)],  # Bottom-right
                [int(x), int(y + slot_height_row1)]                 # Bottom-left
            ],
            "occupied": False
        })
    
    # === FILA INFERIOR: 12 PLAZAS ===
    row2_y = MARGIN_TOP + slot_height_row1 + GAP_BETWEEN_ROWS
    row2_available_width = width - MARGIN_LEFT - MARGIN_RIGHT
    slot_width_row2 = (row2_available_width - (11 * SLOT_GAP_H)) / 12
    slot_height_row2 = height - row2_y - MARGIN_BOTTOM
    
    print(f"\n📊 Fila Inferior (12 plazas):")
    print(f"   Ancho por plaza: {slot_width_row2:.1f}px")
    print(f"   Alto: {slot_height_row2:.1f}px")
    print(f"   Separación: {SLOT_GAP_H}px")
    
    for i in range(12):
        x = MARGIN_LEFT + i * (slot_width_row2 + SLOT_GAP_H)
        y = row2_y
        
        slots.append({
            "id": 14 + i,
            "polygon": [
                [int(x), int(y)],
                [int(x + slot_width_row2), int(y)],
                [int(x + slot_width_row2), int(y + slot_height_row2)],
                [int(x), int(y + slot_height_row2)]
            ],
            "occupied": False
        })
    
    # Guardar JSON
    with open("data/parking_slots.json", "w", encoding="utf-8") as f:
        json.dump(slots, f, indent=4)
    
    print(f"\n✓ {len(slots)} plazas generadas y guardadas")
    print(f"✓ Archivo: data/parking_slots.json")
    
    # Mostrar preview
    print("\n📷 Mostrando preview (presiona cualquier tecla para cerrar)...")
    preview = draw_preview(frame, slots)
    cv2.imshow("Preview - Plazas Generadas", preview)
    cv2.waitKey(0)
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✓ Generación completada exitosamente")
    print("=" * 60)

def draw_preview(frame, slots):
    """Dibuja las plazas sobre el frame para preview"""
    display = frame.copy()
    
    for slot in slots:
        pts = np.array(slot["polygon"], dtype=np.int32)
        
        # Color diferente para cada fila
        if slot["id"] <= 13:
            color = (0, 255, 0)  # Verde para fila superior
        else:
            color = (255, 0, 255)  # Magenta para fila inferior
        
        # Dibujar polígono
        cv2.polylines(display, [pts], True, color, 2)
        
        # Dibujar ID
        center_x = int(np.mean([p[0] for p in slot["polygon"]]))
        center_y = int(np.mean([p[1] for p in slot["polygon"]]))
        cv2.putText(display, str(slot["id"]), (center_x-10, center_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Texto informativo
    cv2.putText(display, "Fila Superior: 13 plazas (VERDE)", (10, 25),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(display, "Fila Inferior: 12 plazas (MAGENTA)", (10, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    return display

if __name__ == "__main__":
    # Ejecutar con tu cámara principal
    generate_optimal_parking_slots(camera_id=1)
