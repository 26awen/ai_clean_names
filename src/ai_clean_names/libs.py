import os
import time
from collections.abc import Sequence
import shutil

# from glob import glob
from rich import print
from glob import glob
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from dotenv import load_dotenv

_ = load_dotenv()

default_model = OpenAIChatModel(
    "google/gemini-2.5-flash",
    provider=OpenRouterProvider(api_key=os.environ.get("OPENROUTER_API_KEY")),
)


prompt = """
    You are a helpful assistant that can clean the name of the file.
    You can identify the "movie name", the "movie year" and ext of the file from the inputed origin movie name.
    The "movie name" could be between brackets,:(),《》. But your result should not include brackets.
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


def get_name_info(origin_name: str, model: OpenAIChatModel | str | None = None):
    if model is None:
        # model = "google-gla:gemini-2.5-flash"
        model = default_model
    agent = Agent(model=model, system_prompt=prompt, output_type=NameInfo)
    result = agent.run_sync(f"The origin movie name is: {origin_name}")
    # printresult.data)
    # return result.output
    # > city='London' country='United Kingdom'
    # print(result.usage())
    return result.output


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


def rename(root_dir: str, name_info: NameInfo, sub_dir: str | None = None):
    # 源文件在原始目录中
    origin_name_full = os.path.join(root_dir, name_info.origin_name)

    # 处理年份为空的情况
    if name_info.movie_year:
        new_movie_name = (
            f"{name_info.movie_name}({name_info.movie_year}).{name_info.movie_file_ext}"
        )
    else:
        new_movie_name = f"{name_info.movie_name}.{name_info.movie_file_ext}"

    # 目标文件在输出目录中，如果没有指定output_root则使用原目录
    target_root = os.path.join(root_dir, sub_dir) if sub_dir is not None else root_dir
    movie_name_full = os.path.join(target_root, new_movie_name)

    if not os.path.exists(origin_name_full):
        raise FileNotFoundError(f"源文件不存在: {origin_name_full}")

    # 确保目标目录存在
    # os.makedirs(target_dir, exist_ok=True)

    if os.path.exists(movie_name_full):
        print(f"警告: 目标文件已存在，跳过重命名: {new_movie_name}")
        return

    try:
        print(f"重命名: {name_info.origin_name} -> {new_movie_name}")
        shutil.move(
            origin_name_full, movie_name_full
        )  # 使用 shutil.move 代替 os.rename
        print(f"成功重命名!")
    except Exception as e:
        raise ValueError(f"重命名失败: {e}")


# def rename(root_dir: str, name_info: NameInfo):
#     origin_name_full = os.path.join(root_dir, name_info.origin_name)
#     new_movie_name = (
#         f"{name_info.movie_name}({name_info.movie_year}).{name_info.movie_file_ext}"
#     )
#     movie_name_full = os.path.join(root_dir, new_movie_name)
#
#     if not os.path.exists(origin_name_full):
#         raise FileNotFoundError
#
#     try:
#         print(f"Renaming {name_info.origin_name} to {new_movie_name}")
#         os.rename(origin_name_full, movie_name_full)
#     except Exception as e:
#         raise ValueError(e)

def filter_downloading_files(file_list: list[tuple[str, str]], root_dir: str):
    """
    过滤正在下载的文件
    直接检查文件系统中是否存在对应的.aria2文件
    """
    print(f"过滤前文件列表: {[item[1] for item in file_list]}")  # 调试信息
    
    filtered_list = []
    downloading_files = []
    
    for item in file_list:
        dir_path, filename = item
        # 构造对应的.aria2文件路径
        aria2_file_path = os.path.join(root_dir, filename + ".aria2")
        
        if os.path.exists(aria2_file_path):
            # 如果存在.aria2文件，说明正在下载，跳过这个文件
            downloading_files.append(filename)
            print(f"跳过正在下载的文件: {filename}")
        else:
            # 如果不存在.aria2文件，保留这个文件
            filtered_list.append(item)
    
    print(f"正在下载的文件: {downloading_files}")
    print(f"过滤后文件列表: {[item[1] for item in filtered_list]}")
    return filtered_list

# def filter_downloading_files(file_list: list[tuple[str, str]]):
#     """
#     过滤正在下载的文件
#     如果存在带 .aria2 扩展名的文件，则过滤掉对应的原始文件
#     """
#     # 找出所有正在下载的文件的原始文件名
#     downloading_files = set()
#     for item in file_list:
#         filename = item[1]  # 获取文件名
#         if filename.endswith(".aria2"):
#             # 去掉 .aria2 后缀得到原始文件名
#             original_filename = filename[:-6]  # 移除 '.aria2'
#             downloading_files.add(original_filename)
#
#     # 过滤掉正在下载的文件对应的所有项
#     filtered_list = [item for item in file_list if item[1] not in downloading_files]
#     return filtered_list


def batch_rename(
    root_dir: str,
    wildcards: Sequence[str] | None = None,
    model: str = None,
    ignore_unfinshed: bool = True,
    sub_dir: str | None = "renamed",
):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"root_dir not exist:{root_dir}.")

    files = get_filenames(root_dir, wildcards)
    print(files)
    splited_names = [split_path(f) for f in files]

    # 过滤掉还没下载好的文件——存在"aria2"后缀的同名视频文件。
    if ignore_unfinshed:
        splited_names = filter_downloading_files(splited_names, root_dir=root_dir)

    results = []
    for item in splited_names:
        try:
            data = get_name_info(item[1], model=model)
            time.sleep(
                5
            )  # gemini model is too easy to be overloaded, so put some sleep here.
            results.append(data)
            rename(root_dir, data, sub_dir=sub_dir)
            # print(data)
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e or 'No message'}")

    # for r in results:
    #     rename(root_dir, r)
