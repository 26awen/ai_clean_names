import os
import time
from collections.abc import Sequence

# from glob import glob
from rich import print

# from icecream import ic
from ai_clean_names.libs import get_name_info, rename, split_path, get_filenames


if __name__ == "__main__":
    root_dir = r"F:\movies_2025\2025"

    def batch_rename(
        root_dir: str,
        wildcards: Sequence[str] | None = None,
        model: str = None,
    ):
        if not os.path.exists(root_dir):
            raise FileNotFoundError(f"root_dir not exist:{root_dir}.")

        files = get_filenames(root_dir, wildcards)
        print(files)
        splited_names = [split_path(f) for f in files]

        results = []
        for item in splited_names:
            try:
                data = get_name_info(item[1], model=model)
                time.sleep(
                    5
                )  # gemini model is too easy to be overloaded, so put some sleep here.
                results.append(data)
                print(data)
            except Exception as e:
                print(e)

        for r in results:
            rename(root_dir, r)
