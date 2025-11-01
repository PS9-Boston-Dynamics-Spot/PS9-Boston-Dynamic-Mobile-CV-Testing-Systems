from pathlib import Path
from db.dal.DataAccessLayer import DataAccessLayer

ArUcoPath = "/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/ArUco"
TrainPath = "/workspaces/PS9-Boston-Dynamic-Mobile-CV-Testing-Systems/data/images/train"


def get_images(path: str) -> list[Path]:
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Pfad '{path}' existiert nicht.")
    if not path_obj.is_dir():
        raise NotADirectoryError(f"'{path}' ist kein Ordner.")

    return [
        file.resolve()
        for file in path_obj.rglob("*")
        if file.suffix.lower() in image_extensions
    ]


def map_image_metadata(
    image_paths: list[Path], bucket_name: str = "raw-images"
) -> list[dict]:
    metadata_list = []

    for i, img_path in enumerate(image_paths, start=1):
        metadata = {
            "file_path": str(img_path),
            "name": img_path.stem,  # Dateiname ohne Endung
            "format": img_path.suffix.lstrip(".").lower(),  # Dateiformat z. B. 'png'
            "bucket": bucket_name,
            "size": img_path.stat().st_size,  # Dateigröße in Bytes
            "compressed": False,
            "compression_method": None,
        }
        metadata_list.append(metadata)

    return metadata_list


if __name__ == "__main__":
    aruco_images = get_images(ArUcoPath)
    train_images = get_images(TrainPath)

    aruco_metadata = map_image_metadata(aruco_images, bucket_name="aruco-images3")
    train_metadata = map_image_metadata(train_images, bucket_name="train-images3")

    print("ArUco-Metadaten:")
    for m in aruco_metadata:
        print(m)

    print("\nTrain-Metadaten:")
    for m in train_metadata:
        print(m)

    # exit()

    with DataAccessLayer() as dal:
        for metadata_raw in aruco_metadata:
            result = dal.insert_raw_image(metadata_raw)
            print("Inserted raw image:", result)

        for metadata_train in train_metadata:
            result = dal.insert_raw_image(metadata_train)
            print("Inserted analyzed image:", result)
