from image_downloader import BDRCImageDownloader,zip_work_dir,DATA_DIR
import github_utils
from pathlib import Path
from github import Github 
import os
import csv





def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


BASE_PATH = _mkdir(Path.home() / ".openpecha")
zip_file_home = _mkdir(Path.home() / ".openpecha/zip")

def download_image(work_id):
    downloader = BDRCImageDownloader(bdrc_scan_id=work_id, output_dir=Path(DATA_DIR),output_view = "zip")
    work_dir = downloader.download()
    return work_dir

def get_readme():
    zip_url = "adfdf"
    base_readme = Path("ocr_readme.md").read_text(encoding="utf-8")
    zip_url = f"[zip_url]: {zip_url}"
    readme = base_readme + zip_url
    return base_readme

def publish_repo(repo_name, work_id, asset_paths):
    token = "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"
    read_me = get_readme()
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
    update_read_me(repo_name,release_link,token)


def update_catalog(work_id,repo_name,release_link):
    with open(f"catalog.csv",'a') as f:
        writer = csv.writer(f)
        writer.writerow([work_id,repo_name,release_link])

def update_read_me(repo_name,realease_link,token):
    g = Github(token)
    readme = get_remote_readme(g,repo_name)
    readme+=f"[zip_url]: {realease_link}"
    try:
        commit_msg = "updated readme"
        repo = g.get_repo(f"MonlamAI/{repo_name}")
        contents = repo.get_contents(f"readme.md", ref="master")
        repo.update_file(contents.path, commit_msg, readme, sha=contents.sha, branch="master")
    except Exception as e:
        print(e)

def get_remote_readme(g,repo_name):
    try:
        repo = g.get_repo(f"MonlamAI/{repo_name}")
        contents = repo.get_contents(f"readme.md")
        return contents.decoded_content.decode()
    except:
        print('Repo Not Found')
        return None


def main():
    repo_count = 300
    work_ids = Path("work_ids.txt").read_text().splitlines()
    for work_id in work_ids:
        repo_name = f"OCR_Demo"
        work_dir = download_image(work_id)
        zip_file = zip_work_dir(work_dir)
        release_link = publish_repo(repo_name,work_id,asset_paths=[zip_file])
        update_catalog(work_id,repo_name,release_link)
        repo_count+=1
        break

if __name__ == "__main__":
    main()   