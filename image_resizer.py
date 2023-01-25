import io
import logging
import requests
import rdflib
import shutil

from pathlib import Path
from typing import Iterator, Union


from PIL import Image as PillowImage
from wand.image import Image as WandImage

def resize_image(img, img_obj_type):
    if img_obj_type == "wand":
        img.thumbnail(320,320)
    elif img_obj_type == "pillow":
        img.thumbnail((320,320))
    return img


def save_img_with_wand(fp: io.BytesIO, fn: Path) -> bool:
    try:
        with WandImage(blob=fp.getvalue()) as img:
            img.format = "png"
            img = resize_image(img, img_obj_type="wand")
            img.save(filename=str(fn))
            return True
    except Exception:
        logging.exception(f"Failed to save {fn} with `Wand`")
        return False

def save_img_with_pillow(fp: io.BytesIO, fn: Path) -> bool:
    """
    uses pillow to interpret the bits as an image and save as a format
    that is appropriate for Google Vision (png instead of tiff for instance).
    """
    try:
        img = PillowImage.open(fp)
        img = resize_image(img, img_obj_type="pillow")
        img.save(str(fn))
    except Exception:
        logging.exception(f"Failed to save {fn} with `Pillow`")
        return False

    return True

def save_img(fp: io.BytesIO, fn: Union[str, Path], work_dir: Path):
    """Save the image in .png format to `img_groupdir/fn

    Google Vision API does not support bdrc tiff images.

    Args:
        fp (io.BytesIO): image bits
        fn (str): filename
        work_dir (Path): directory to save the image
    """
    output_fn = work_dir / fn
    fn = Path(fn)
    if fn.suffix in [".tif", ".tiff", ".TIF"]:
        output_fn = work_dir / f"{fn.stem}.png"

    saved = save_img_with_pillow(fp, output_fn)
    if not saved:
        save_img_with_wand(fp, output_fn)

def save_img_grp_images(img_grp_dir, target_work_dir):
    img_file_paths = list(img_grp_dir.iterdir())
    for img_file_path in img_file_paths:
        img_file = str(img_file_path)
        save_img(img_file, img_file_path.name, target_work_dir)


def save_images(src_work_dir, output_dir):
    work_id = src_work_dir.stem
    target_work_dir = output_dir / work_id
    target_work_dir.mkdir(exist_ok=True, parents=True)
    img_grp_dirs = list(src_work_dir.iterdir())
    img_grp_dirs.sort()
    for img_grp_dir in img_grp_dirs:
        save_img_grp_images(img_grp_dir, target_work_dir)
    return target_work_dir

def zip_img_dir(img_dir, output_dir):
    work_id = img_dir.stem
    shutil.make_archive(f"{output_dir}/{work_id}", 'zip', img_dir)

if __name__ == "__main__":
    work_id  = "W26071"
    src_work_dir = Path(f'./data/src/{work_id}')
    output_dir = Path(f"./data/target")
    target_work_dir = save_images(src_work_dir, output_dir)
    zip_img_dir(target_work_dir, output_dir)