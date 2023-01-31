from image_downloader import BDRCImageDownloader,_mkdir,DATA_DIR,BASE_PATH
import github_utils
from pathlib import Path
import os
import csv



def download_image(work_id):
    downloader = BDRCImageDownloader(bdrc_scan_id=work_id, output_dir=Path(DATA_DIR),output_view = "zip")
    downloader.download()

def get_readme(work_id):
    work_id = f"|Work Id | {work_id}"
    Table = "| --- | --- "
    readme = f"{work_id}\n{Table}"
    return readme

def publish_repo(repo_name, work_id, asset_paths):
    return 
    token = "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"
    read_me = get_readme(work_id)
    local_repo = _mkdir(BASE_PATH / repo_name)
    Path(local_repo / "readme.md").write_text(read_me)
    github_utils.github_publish(
        local_repo,
        message="initial commit",
        not_includes=[],
        layers=[],
        token=token,
        description=work_id
       )
    release_link = github_utils.create_release(
        repo_name,
        prerelease=False,
        asset_paths=asset_paths, 
        token=token

    )
    return release_link

def update_catalog(work_id,repo_name,release_link):
    with open(f"catalog.csv",'a') as f:
        writer = csv.writer(f)
        writer.writerow([work_id,repo_name,release_link])
            

def main():
    repo_count = 300
    work_ids = Path("work_ids.txt").read_text().splitlines()
    for work_id in work_ids:
        repo_name = f"OCR{repo_count}"
        download_image(work_id)
        zip_file = Path(f"{DATA_DIR}/zip/{work_id}.zip")
        release_link = publish_repo(repo_name,work_id,asset_paths=[zip_file])
        update_catalog(work_id,repo_name,release_link)
        repo_count+=1
        break


if __name__ == "__main__":
    main()   


    