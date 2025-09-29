import os
from PIL import Image, ImageDraw, ImageFont
import io

class MyModel:
    _instance = None

    # ----------------------------------------------------------
    def __init__(self, model_path=None):
        if not hasattr(self, "yolo"):
            from ultralytics import YOLO
            if model_path is None:
                model_path = os.path.join(os.path.dirname(__file__), "..", "model_weights", "Second_head_count_model.pt")
                model_path = os.path.abspath(model_path)
            self.yolo = YOLO(model_path)

    # ----------------------------------------------------------
    @classmethod
    def get_model(cls, model_path=None):
        if cls._instance is None:
            cls._instance = MyModel(model_path)
        return cls._instance

    # ----------------------------------------------------------
    def predict_and_count(self, image):
        if isinstance(image, str):   # path
            image = Image.open(image)
        elif isinstance(image, io.IOBase):  # file-like
            image = Image.open(image)
        elif not isinstance(image, Image.Image):  # not PIL
            raise ValueError("Unsupported image type")

        results = self.yolo(image)[0]
        return self.count_persons(results)
    # ----------------------------------------------------------
    def predict_and_label(self, image, show_image=False):
        if isinstance(image, str):
            image = Image.open(image)

        results = self.yolo(image, conf=0.30)[0]
        labeled_image = self.label_images(image, results, show_image=show_image)
        return labeled_image

    # ----------------------------------------------------------
    def label_images(self, image, results, show_image=False):
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for box in results.boxes:
            cls_index = int(box.cls[0].numpy())
            tag = results.names[cls_index]
            if tag == "1":
                coords = box.xyxy.squeeze().numpy()  # [x1, y1, x2, y2]
                draw.rectangle(coords, outline="green", width=3)
                draw.text((coords[0], coords[1]), tag, fill="red", font=font, stroke_width=1)

        if show_image:
            image.show()
        return image

    # ----------------------------------------------------------
    def count_persons(self, results):
        # Find the class index for "person"
        person_class_index = [k for k, v in results.names.items() if v == "1"][0]
        person_count = (results.boxes.cls == person_class_index).sum().item()
        return person_count


if __name__ == "__main__":
    model = MyModel.get_model()
    for i in range(1):
        img_path = f"C:\\Users\\ISHTIAQ\\OneDrive\\Desktop\\PMIU\\classroom_1.jpg"
        count = model.predict_and_label(img_path, show_image=True)
        print(f"{img_path}: {count} persons detected")
