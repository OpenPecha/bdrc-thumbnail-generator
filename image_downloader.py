import io
import logging
import requests
import rdflib
import shutil
import zipfile
from pathlib import Path
from rdflib import URIRef, Graph
from rdflib.namespace import Namespace, NamespaceManager
from typing import Iterator, Union
from openpecha import github_utils

from openpecha.buda import api as buda_api
from PIL import Image as PillowImage
from wand.image import Image as WandImage

from exceptions import BdcrScanNotFound

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
NSM = NamespaceManager(rdflib.Graph())


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


DATA_DIR = './data'
BASE_PATH = _mkdir(Path.home() / ".openpecha")
zip_file_home = _mkdir(Path.home() / ".openpecha/zip")



class BDRCImageDownloader:
    def __init__(self, bdrc_scan_id: str, output_dir: Path,output_view="zip") -> None:
        self.bdrc_scan_id = bdrc_scan_id
        self.output_dir = output_dir
        self.output_view = output_view

    def get_img_groups(self):
        """
        Get the image groups from the bdrc scan id
        """
        res = buda_api.get_buda_scan_info(self.bdrc_scan_id)
        if not res:
            raise BdcrScanNotFound(f"Scan {self.bdrc_scan_id} not found")
        yield from res["image_groups"]
    
    def get_number_of_intro_images(self, imagegroup):

        ttl_response = requests.get(f"http://purl.bdrc.io/resource/{imagegroup}.ttl")
        ttl_content = ttl_response.text
        g = Graph()
        try:
            g.parse(data=ttl_content, format="ttl")
            number = int((g.value(BDR[imagegroup], BDO["volumePagesTbrcIntro"])).split("/")[-1])
            return number
        except:
            return None

    def get_s3_img_list(self, img_group: str) -> Iterator[str]:
        """Returns image list with filename for the given `image_group`"""
        imgs = buda_api.get_image_list_s3(self.bdrc_scan_id, img_group)
        number_of_intro = self.get_number_of_intro_images(img_group)
        for img in imgs[number_of_intro:]:
            yield img["filename"]

    def save_img_with_wand(self, fp: io.BytesIO, fn: Path) -> bool:
        try:
            with WandImage(blob=fp.getvalue()) as img:
                img.format = "png"
                img.thumbnail(320,320)
                img.save(filename=str(fn))
                return True
        except Exception:
            logging.exception(f"Failed to save {fn} with `Wand`")
            return False

    def save_img_with_pillow(self, fp: io.BytesIO, fn: Path) -> bool:
        """
        uses pillow to interpret the bits as an image and save as a format
        that is appropriate for Google Vision (png instead of tiff for instance).
        """
        try:
            img = PillowImage.open(fp)
            img.thumbnail((320,320))
            img.save(str(fn))
        except Exception:
            logging.exception(f"Failed to save {fn} with `Pillow`")
            return False

        return True

    def save_img(self, fp: io.BytesIO, fn: Union[str, Path], work_dir: Path):
        """Save the image in .png format to `img_groupdir/fn

        Google Vision API does not support bdrc tiff images.

        Args:
            fp (io.BytesIO): image bits
            fn (str): filename
            img_group_dir (Path): directory to save the image
        """
        output_fn = work_dir / fn
        fn = Path(fn)
        if fn.suffix in [".tif", ".tiff", ".TIF"]:
            output_fn = work_dir / f"{fn.stem}.png"

        saved = self.save_img_with_pillow(fp, output_fn)
        if not saved:
            self.save_img_with_wand(fp, output_fn)
        if self.output_view == "zip":
            Path(f"{DATA_DIR}/zip").mkdir(parents=True, exist_ok=True)
            self.zip(output_fn)
    

    def zip(self,file_path):
        home_path = Path(DATA_DIR)
        zip_file = Path(f"{DATA_DIR}/zip/{self.bdrc_scan_id}.zip")
        with zipfile.ZipFile(zip_file, mode='a') as myzip:
            myzip.write(file_path,arcname=file_path.relative_to(home_path))

    def save_img_group(self, img_group, work_dir):
        s3_folder_prefix = buda_api.get_s3_folder_prefix(self.bdrc_scan_id, img_group)
        for img_fn in self.get_s3_img_list(img_group):
            img_path_s3 = Path(s3_folder_prefix) / img_fn
            img_bits = buda_api.gets3blob(str(img_path_s3))
            if img_bits:
                self.save_img(img_bits, img_fn,work_dir)
            break

    def download(self):
        bdrc_scan_dir = self.output_dir / self.bdrc_scan_id
        bdrc_scan_dir.mkdir(exist_ok=True, parents=True)
        for img_group_id in self.get_img_groups():
            self.save_img_group(img_group_id, bdrc_scan_dir)
            break
        return bdrc_scan_dir
    

def zip_img_dir(img_dir):
    work_id = img_dir.stem
    shutil.make_archive(f"{DATA_DIR}/{work_id}", 'zip', img_dir)


if __name__ == "__main__":
    downloader = BDRCImageDownloader(bdrc_scan_id="W26071", output_dir=Path(DATA_DIR),output_view = "zip")
    img_dir = downloader.download()
    # img_dir = Path('./data/W1KG26108')
    zip_img_dir(img_dir)
