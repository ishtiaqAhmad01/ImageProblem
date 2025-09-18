import hashlib
from PIL import Image


def get_sha256_from_pil(file_obj):
    sha256 = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256.update(chunk)
        
    return sha256.hexdigest()


if __name__ == "__main__":
    img1 = Image.open("classroom_2.jpg")
    img2 = Image.open("classroom_2.jpg")

    img1_hash = get_sha256_from_pil(img1)
    img2_hash = get_sha256_from_pil(img2)

    print(img1_hash)
    print(img2_hash)

    if img1_hash == img2_hash:
        print("Same Image")
    else:
        print("Differ Image")























