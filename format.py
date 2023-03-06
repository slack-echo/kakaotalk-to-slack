import json
import os
from typing import Any, Dict


def format(dir: str, split:bool=True) -> None:
    with open(os.path.join(dir, "users.json"), "r", encoding="utf-8") as f:
        id: Dict[str, str] = json.load(f)
    assert all(id.values()), "All user IDs must be filled."
    if split:
        dir_text = os.path.join(dir, "text")
        dir_attachment = os.path.join(dir, "attachment")
        format_nested(dir_text, id)
        format_nested(dir_attachment, id)
    else:
        format_nested(dir, id)

    format_channels_json(dir, id)


def format_nested(dir, id):
    channel_dirs = [
        channel_dir
        for item in os.listdir(dir)
        if os.path.isdir(channel_dir := os.path.join(dir, item))
    ]
    for channel_dir in channel_dirs:
        format_date_json(channel_dir, id)


def format_date_json(dir, id):
    for file in os.listdir(dir):
        if file.endswith(".json"):
            with open(os.path.join(dir, file), "r", encoding="utf-8") as f:
                json_data: Dict[str, Any] = json.load(f)
            json_string: str = json.dumps(json_data, ensure_ascii=False)

            for (k, v) in id.items():
                json_string = json_string.replace(f'"{k}"', f'"{v}"')
                json_string = json_string.replace(f"<@{k}>", f"<@{v}>")

            with open(os.path.join(dir, file), "w", encoding="utf-8") as f:
                json.dump(json.loads(json_string), f, ensure_ascii=False)


def format_channels_json(dir, id):
    with open(os.path.join(dir, "channels.json"), "r", encoding="utf-8") as f:
        json_data: Dict[str, str] = json.load(f)
    json_string: str = json.dumps(json_data, ensure_ascii=False)

    for (k, v) in id.items():
        json_string = json_string.replace(f'"{k}"', f'"{v}"')

    with open(os.path.join(dir, "channels.json"), "w", encoding="utf-8") as f:
        json.dump(json.loads(json_string), f, ensure_ascii=False)


if __name__ == "__main__":
    workspace_dir = "data/slack"
    format(workspace_dir, split=False)
