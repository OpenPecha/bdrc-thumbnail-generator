from image_downloader import BDRCImageDownloader
import github_utils
from pathlib import Path

def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


DATA_DIR = './data'
BASE_PATH = _mkdir(Path.home() / ".openpecha")
PECHAS_PATH = _mkdir(BASE_PATH / "pechas")



def download():
    downloader = BDRCImageDownloader(bdrc_scan_id="W26071", output_dir=Path(DATA_DIR),output_view = "zip")
    img_dir = downloader.download()
    # img_dir = Path('./data/W1KG26108')

def get_readme(work_id):
    work_id = f"|Work Id | {work_id}"
    Table = "| --- | --- "
    readme = f"{work_id}\n{Table}"
    return readme

def publish_repo(repo_name, asset_paths=None):
    token = "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"
    read_me = get_readme(repo_name)
    local_repo = _mkdir(BASE_PATH / repo_name)
    Path(local_repo / "readme.md").write_text(read_me)
    github_utils.github_publish(
        local_repo,
        message="initial commit",
        not_includes=[],
        layers=[],
        token=token
       )
    #res = github_utils.create_github_repo(path=repo_name,org_name=org_name,token=token)
    if asset_paths:
        github_utils.create_release(
            repo_name,
            prerelease=False,
            asset_paths=asset_paths, 
            token=token
        )

if __name__ == "__main__":
    assets = [Path("W26071.zip")]
    publish_repo("W26071",asset_paths=assets)
    


    