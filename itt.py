from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch
import cv2

class ITT:
    """
    Clase para generar descripciones de características visibles
    de vehículos a partir de recortes de imágenes.
    """
    def __init__(self, model_name="nlpconnect/vit-gpt2-image-captioning"):
        self.device = "cpu"

        # Cargar modelo y tokenizer de Hugging Face
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name).to(self.device)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Parámetros de generación
        self.gen_kwargs = {"max_length": 50, "num_beams": 4}

    def describe_vehicle(self, vehicle_crop):
        """
        Recibe un recorte de vehículo (numpy array BGR de OpenCV)
        y devuelve una descripción de sus características visibles.
        """
        if vehicle_crop.size == 0:
            return ""

        # Convertir BGR a RGB y luego a PIL
        pil_image = Image.fromarray(cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2RGB))

        # Preprocesar imagen
        pixel_values = self.feature_extractor(images=pil_image, return_tensors="pt").pixel_values.to(self.device)

        # Generar caption
        output_ids = self.model.generate(pixel_values, **self.gen_kwargs)
        caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return caption
