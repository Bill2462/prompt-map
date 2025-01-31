import lmdb
from PIL import Image
from io import BytesIO

def _get_img(filename, txn, img_size):
    if not isinstance(filename, str):
        filename = str(filename)

    image_data = txn.get(filename.encode())
    img = Image.open(BytesIO(image_data))
    img = img.resize((img_size, img_size))
    return img

class ImageDatabase:
    def __init__(self, db_path: str, img_size=256):
        self.img_size = img_size
        self.db_path = db_path
        self.env = lmdb.open(db_path)
    
    def get_img(self, filename: str):
        with self.env.begin() as txn:
            return _get_img(filename, txn, self.img_size)
    
    def get_imgs(self, filenames: list[str]):
        with self.env.begin() as txn:
            return [_get_img(filename, txn, self.img_size) for filename in filenames]

