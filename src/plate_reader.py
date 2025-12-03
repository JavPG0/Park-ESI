import easyocr
import cv2
import re

class PlateReader:
    def __init__(self):
        # Inicializar EasyOCR con español e inglés, sin GPU
        self.reader = easyocr.Reader(['en', 'es'], gpu=False)
    
    def preprocess_plate(self, crop):
        """Preprocesar imagen para mejorar lectura OCR"""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold para resaltar caracteres
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def clean_plate_text(self, text):
        """Limpiar y normalizar texto de matrícula"""
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        return cleaned
    
    def read_plate(self, vehicle_crop):
        """Extraer matrícula de imagen de vehículo"""
        preprocessed = self.preprocess_plate(vehicle_crop)
        
        # Leer texto con EasyOCR
        results = self.reader.readtext(preprocessed)
        
        # Buscar la mejor candidata
        best_plate = None
        best_confidence = 0
        
        for (bbox, text, confidence) in results:
            cleaned = self.clean_plate_text(text)
            # Matrículas españolas: 4 números + 3 letras (ej: 1234ABC)
            if 4 <= len(cleaned) <= 10 and confidence > best_confidence:
                best_plate = cleaned
                best_confidence = confidence
        
        return best_plate if best_confidence > 0.5 else None
