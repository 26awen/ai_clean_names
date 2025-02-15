import os
import time
from collections.abc import Sequence

# from glob import glob
from rich import print
from glob import glob
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv

_ = load_dotenv()


prompt = """
    You are a helpful assistant that can clean the name of the file.
    You can identify the "movie name", the "movie year" and ext of the file from the inputed origin movie name.
    The "movie name" could be between brackets:(),《》. But your result should not include brackets.
    Except that if some part of the name is in brackets:(), you should keep it as the pattern. For example: 守望者(上).
    **NOTE**:
        - There is no dot between the name.
        - There is no dot around the year. Year could be missing. Then the result of "movie year" is "".
        - Do not include a '.' at the beginning of the "ext name".
"""


class NameInfo(BaseModel):
    origin_name: str
    movie_name: str
    movie_year: str
    movie_file_ext: str


def get_name_info(origin_name: str, model: str | None = None):
    if model is None:
        model = "google-gla:gemini-1.5-pro"
    agent = Agent(model=model, system_prompt=prompt, result_type=NameInfo)
    result = agent.run_sync(f"The origin movie name is: {origin_name}")
    # printresult.data)
    return result.data
    # > city='London' country='United Kingdom'
    # print(result.usage())


def split_path(p: str):
    return os.path.dirname(p), os.path.basename(p)


def get_filenames(
    src_root: str, wildcards: list[str] | None = None, recursive: bool = False
):
    if wildcards is None:
        wildcards = ["*.mp4", "*.mkv", "*.ts"]
    raw_filenames = []
    for wc in wildcards:
        raw_filenames.extend(glob(os.path.join(src_root, wc), recursive=recursive))
    return raw_filenames


def rename(root_dir: str, name_info: NameInfo):
    origin_name_full = os.path.join(root_dir, name_info.origin_name)
    new_movie_name = (
        f"{name_info.movie_name}({name_info.movie_year}).{name_info.movie_file_ext}"
    )
    movie_name_full = os.path.join(root_dir, new_movie_name)

    if not os.path.exists(origin_name_full):
        raise FileNotFoundError

    try:
        print(f"Renaming {name_info.origin_name} to {new_movie_name}")
        os.rename(origin_name_full, movie_name_full)
    except Exception as e:
        raise ValueError(e)


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
