import os
import re
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

import anthropic
import glob
from rich import print

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")
ANTHROPIC_MAX_TOKENS = os.getenv("ANTHROPIC_MAX_TOKENS")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")


@dataclass
class FileInfo:
    basename: str
    dirname: str
    filename: str
    extension: str
    full_path: str

    @classmethod
    def from_path(cls, path: str) -> "FileInfo":
        return cls(
            basename=os.path.basename(path),
            dirname=os.path.dirname(path),
            filename=os.path.basename(path),
            extension=os.path.splitext(path)[1],
            full_path=path,
        )

    def __make_new_name(self, new_name: str) -> str:
        return os.path.join(self.dirname, new_name + self.extension)

    def rename(self, new_name: str) -> None:
        new_full_path = self.__make_new_name(new_name)
        os.rename(self.full_path, new_full_path)
        self.full_path = new_full_path


def get_filenames(
    src_root: str, patterns: list[str], recursive: bool = False
) -> list[FileInfo]:
    raw_filenames = []
    for pattern in patterns:
        raw_filenames.extend(
            glob.glob(os.path.join(src_root, pattern), recursive=recursive)
        )
    return [FileInfo.from_path(f) for f in raw_filenames]


def clean_name(src_name: str, name_pattern: str, year_pattern: str) -> str:
    name = re.search(name_pattern, src_name).group()
    year = re.search(year_pattern, src_name).group()
    return f"{name}({year})"


tools_to_use = {"clean_name": clean_name}

tool_clean_name = {
    "name": "clean_name",
    "description": "Clean the name of the file",
    "input_schema": {
        "type": "object",
        "properties": {
            "src_name": {"type": "string"},
            "name_pattern": {
                "type": "string",
                "description": "The pattern help me to find the name use regex",
            },
            "year_pattern": {
                "type": "string",
                "description": "The pattern help me to find the year use regex",
            },
        },
        "required": ["src_name", "name_pattern", "year_pattern"],
    },
}

prompt = """
    You are a helpful assistant that can clean the name of the file.
    You can identify the name and the year of the file from the input string and give me the pattern to find it.
    There is no dot between the name.
    There is no dot around the year.
    Name could be between brackets:(),《》. But your pattern should not include brackets.
    Year could be missing. Then the pattern is "".
"""

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_name_pattern(src_name: str) -> str:
    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        system=prompt,
        max_tokens=int(ANTHROPIC_MAX_TOKENS),
        tools=[tool_clean_name],
        messages=[
            {
                "role": "user",
                "content": f"Clean the name of the file: {src_name}",
            },
        ],
    )

    if response.stop_reason == "tool_use":
        print("tool_use:")
        tool_use = next(
            block for block in response.content if block.type == "tool_use"
        )
        tool_name = tool_use.name
        tool_input = tool_use.input
        print(tool_name)
        print(tool_input)
        if tool_name in tools_to_use:
            return tool_name, tool_input
        else:
            print("tool_name not in tools_to_use:")
            print(tool_name)
    else:
        print("No tool_use:")
        print(response)


if __name__ == "__main__":
    files = get_filenames(
        os.getenv("FILE_ROOT_DIR"), os.getenv("FILE_PATTERNS").split(",")
    )
    for file in files:
        print(file.full_path)
        tool_name, tool_input = get_name_pattern(file.basename)
        new_name = tools_to_use[tool_name](
            tool_input["src_name"],
            tool_input["name_pattern"],
            tool_input["year_pattern"],
        )
        file.rename(new_name)
        print(f"Rename {file.filename} to {new_name}")
        print("-" * 100)
