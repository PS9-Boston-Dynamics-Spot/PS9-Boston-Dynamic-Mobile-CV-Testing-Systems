# python snippet — konvertiert pickled learner -> reines state_dict + classes.txt
from pathlib import Path
import torch
from fastai.vision.all import load_learner

pkl = Path("src/common/cvision/notebooks/export_resnet34.pkl")
out_weights = Path("src/common/cvision/notebooks/models/resnet34-state_dict.pth")
out_classes = Path("src/common/cvision/notebooks/models/classes.txt")

learn = load_learner(pkl)               # trusted local file
torch.save(learn.model.state_dict(), out_weights)
out_classes.write_text("\n".join(map(str, learn.dls.vocab)))
print("Saved:", out_weights, "and", out_classes)