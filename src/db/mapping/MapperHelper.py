import imghdr
import hashlib


class MapperHelper:

    @staticmethod
    def get_bytes_length(payload: bytes) -> int:
        return len(payload)

    @staticmethod
    def guess_content_type(image_data: bytes) -> str:
        if image_data:
            detected = imghdr.what(None, h=image_data)
            if detected in {"jpeg", "jpg"}:
                return "image/jpeg"
            elif detected == "png":
                return "image/png"
            elif detected == "bmp":
                return "image/bmp"
            elif detected == "tiff":
                return "image/tiff"
            else:
                return "application/octet-stream"

        return "application/octet-stream"

    @staticmethod
    def guess_file_extension(image_data: bytes) -> str:
        if image_data:
            detected = imghdr.what(None, h=image_data)
            if detected in {"jpeg", "jpg"}:
                return "jpg"
            elif detected == "png":
                return "png"
            elif detected == "bmp":
                return "bmp"
            elif detected == "tiff":
                return "tiff"
            else:
                return "bin"

        return "bin"
