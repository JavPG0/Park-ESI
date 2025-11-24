import cv2
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

class ITT:
    
    def __init__(self):

        # Cargar modelo BLIP
        self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        # Diccionarios simples para la extracción de características
        self.colors = [
            "white", "black", "red", "blue", "green", "yellow",
            "grey", "gray", "silver", "gold", "brown"
        ]
        self.brands = [
            "toyota", "ford", "chevrolet", "honda", "mercedes",
            "bmw", "audi", "volkswagen", "nissan", "hyundai",
            "renault", "fiat", "kia", "tesla"
        ]

    def describe_vehicle(self, crop_bgr):

        # Extraer la imagen limpia del vehículo
        crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(crop_rgb)

        # Obtener descripción general
        inputs = self.caption_processor(image, return_tensors="pt")
        out = self.caption_model.generate(**inputs, max_length=50)
        caption = self.caption_processor.decode(out[0], skip_special_tokens=True).lower()

        # Detectar características señaladas
        color = next((c for c in self.colors if c in caption), None)
        brand = next((b for b in self.brands if b in caption), None)

        return {
            "color": color,
            "brand": brand
        }
