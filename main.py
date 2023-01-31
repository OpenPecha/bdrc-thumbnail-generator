from image_downloader import BDRCImageDownloader,_mkdir,DATA_DIR,BASE_PATH
import github_utils
from pathlib import Path
import os



def download_image(work_id):
    downloader = BDRCImageDownloader(bdrc_scan_id=work_id, output_dir=Path(DATA_DIR),output_view = "zip")
    downloader.download()

def get_readme(work_id):
    work_id = f"|Work Id | {work_id}"
    Table = "| --- | --- "
    readme = f"{work_id}\n{Table}"
    return readme

def publish_repo(repo_name, asset_paths=None):
    token = ""
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
    if asset_paths:
        github_utils.create_release(
            repo_name,
            prerelease=False,
            asset_paths=asset_paths, 
            token=token
        )

def main():
    work_ids = Path("work_ids.txt").read_text().splitlines()
    for work_id in work_ids:
        download_image(work_id)
        zip_file = Path(f"{DATA_DIR}/zip/{work_id}.zip")
        publish_repo(work_id,asset_paths=[zip_file])
        break


if __name__ == "__main__":
    main()   


    