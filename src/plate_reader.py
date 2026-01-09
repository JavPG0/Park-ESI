import easyocr
import cv2
import re
import threading


class PlateReader:
    # Lock para evitar conflictos entre hilos al usar EasyOCR
    _lock = threading.Lock()  
    
    def __init__(self):
        # Inicializar EasyOCR con español e inglés, sin GPU
        self.reader = easyocr.Reader(['en', 'es'], gpu=False)
    
    def preprocess_plate(self, crop):
        # Convertir a escala de grises
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold para resaltar caracteres
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Reducir ruido para mejorar lectura OCR
        denoised = cv2.fastNlMeansDenoising(thresh)
        return denoised
    
    def clean_plate_text(self, text):
        # Limpiar y normalizar: solo letras mayúsculas y números
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        return cleaned
    
    def read_plate(self, vehicle_crop):
        # Usar lock para evitar conflictos entre hilos
        with self._lock:
            preprocessed = self.preprocess_plate(vehicle_crop)
            results = self.reader.readtext(preprocessed)
        
        # Buscar la mejor candidata a matrícula
        best_plate = None
        best_confidence = 0
        
        for (bbox, text, confidence) in results:
            cleaned = self.clean_plate_text(text)
            
            # Matrículas españolas: 4-10 caracteres alfanuméricos
            if 4 <= len(cleaned) <= 10 and confidence > best_confidence:
                best_plate = cleaned
                best_confidence = confidence
        
        # Devolver solo si la confianza es > 50%
        return best_plate if best_confidence > 0.5 else None
