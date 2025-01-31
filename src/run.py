import os

# from glob import glob
from rich import print

# from icecream import ic
from ai_clean_names.libs import gemini_agent, rename, split_path, get_filenames


if __name__ == "__main__":
    root_dir = "/Users/cdy/Desktop/test_files/"
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"root_dir not exist:{root_dir}.")

    files = get_filenames(root_dir, ["*.mp4", "*.mkv", "*.ts"])
    print(files)
    print([split_path(f) for f in files])
