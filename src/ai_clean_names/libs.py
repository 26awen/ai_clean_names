import os

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


def gemini_agent(origin_name: str):
    agent = Agent(
        "google-gla:gemini-1.5-flash", system_prompt=prompt, result_type=NameInfo
    )
    result = agent.run_sync(f"The origin movie name is: {origin_name}")
    print(result.data)
    return result.data
    # > city='London' country='United Kingdom'
    # print(result.usage())


def rename(root_dir: str, name_info: NameInfo):
    origin_name_full = os.path.join(root_dir, name_info.origin_name)
    new_movie_name = (
        f"{name_info.movie_name}(name_info.movie_year).{name_info.movie_file_ext}"
    )
    movie_name_full = os.path.join(root_dir, new_movie_name)

    if not os.path.exists(origin_name_full):
        raise FileNotFoundError

    try:
        os.rename(origin_name_full, movie_name_full)
    except Exception as e:
        raise ValueError(e)
