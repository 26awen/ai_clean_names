import os
import time

# from glob import glob
from rich import print

# from icecream import ic
from ai_clean_names.libs import gemini_agent, rename, split_path, get_filenames


if __name__ == "__main__":
    root_dir = r"F:\movies_2025\2025"
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"root_dir not exist:{root_dir}.")

    files = get_filenames(root_dir, ["*.mp4", "*.mkv", "*.ts"])
    print(files)
    splited_names = [split_path(f) for f in files]

    results = []
    for item in splited_names:
        try:
            data = gemini_agent(item[1])
            time.sleep(
                5
            )  # gemini model is too easy to be overloaded, so put some sleep here.
            results.append(data)
            print(data)
        except Exception as e:
            print(e)

    for r in results:
        rename(root_dir, r)
