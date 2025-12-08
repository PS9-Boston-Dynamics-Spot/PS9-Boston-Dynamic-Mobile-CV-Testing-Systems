from pathlib import Path
from ultralytics import YOLO

project_root = Path(__file__).resolve().parents[3]  # 3 Ebenen hoch
data_path = project_root / 'data' / 'images' / 'data.yaml'
model_root = project_root / 'src' / 'common' / 'cvision' / 'models'


# Modelltraining
model = YOLO('yolov8n.pt')

model.train(data=str(data_path), epochs=4, imgsz=640)
model.save(model_root / 'yolov8n_trained')