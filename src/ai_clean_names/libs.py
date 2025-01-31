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
    # > city='London' country='United Kingdom'
    # print(result.usage())


gemini_agent("2024年国产奇幻片《传说》BD国语中字.mp4")
