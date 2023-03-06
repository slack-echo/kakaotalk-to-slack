import json
import os
import re
import sys
import time
from typing import List, Tuple

import pandas as pd

DATE_SEP = r"^-{15}\s[A-Z][a-z]+day,\s([A-Z][a-z]+\s\d{1,2},\s\d{4})\s-{15}"
# if you modify DATE_SEP, you should modify group index in index_by_date function

MESSAGE_TYPE_SEP = r"^\[(.+)\]\s\[(\d{1,2}:\d{2} [AP]M)\]\s|^(.+)님이\s(.+)님을\s초대하였습니다.|^(.+)님이\s나갔습니다."  # noqa: E501
# if you modify MESSAGE_TYPE_SEP, you should modify group index in index_by_message function

DATETIME_FORMAT = "%B %d, %Y %I:%M %p%S"
# if you modify DATETIME_FORMAT, you should check ts format in make_ts function

CHANNEL_NAME_SEP = r"^(.+)\s님과 카카오톡 대화"
# if you modify CHANNEL_NAME_SEP, you should modify group index in get_channel_name function

# channel_name shoud be "[0-9a-z_\-ㄱ-ㅎㅏ-ㅣ가-힣]{1,80}", other characters will be replaced by "_"
CHANNEL_NAME_REPL = r"[^0-9a-z_\-ㄱ-ㅎㅏ-ㅣ가-힣]"

ATTACHMENT_SEP = "^사진$|^사진\s\d{1,2}장$|^파일:\s.+?$|^이모티콘$|^톡게시판\s.+?$"


def index_by_date(data: str) -> List[Tuple[str, int, int]]:
    regex = re.compile(DATE_SEP, re.MULTILINE)
    return [(it.group(1), it.end(), it.start()) for it in regex.finditer(data)]


def index_by_message(data: str) -> List[Tuple[str, str, str, str, int, int]]:
    regex = re.compile(MESSAGE_TYPE_SEP, re.MULTILINE)
    values: List[Tuple[str, str, str, str, int, int]] = []
    for i, it in enumerate(regex.finditer(data)):
        user, ts, inviter, subtype = None, None, None, None
        if it.group(1):
            user, ts = it.group(1), it.group(2)
        elif it.group(4):
            inviter, users = it.group(3), it.group(4)
            subtype = "channel_join"
            for user in users.split("님, "):
                values.append((user, ts, inviter, subtype, it.end(), it.start() if i else -1))  # type: ignore
            continue
        elif it.group(5):
            user, subtype = it.group(5), "channel_leave"
        else:
            continue
        values.append((user, ts, inviter, subtype, it.end(), it.start() if i else -1))
    return values


def split_by_date(row: pd.Series, data: str) -> str:
    return data[row["start"] : row["end"]]


def split_by_message(row: pd.Series) -> str:
    return row["data"][row["start"] : row["end"]].strip()


def fill_text(row: pd.Series) -> None:
    if row["subtype"] == "channel_join":
        row["text"] = f"<@{row['user']}> 님이 채널에 참여함"
    elif row["subtype"] == "channel_leave":
        row["text"] = f"<@{row['user']}> 님이 채널을 떠남"


def make_ts(ts: str) -> float:
    struct_time = time.strptime(ts, DATETIME_FORMAT)
    return time.mktime(struct_time)


def format_date(unix_ts: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(unix_ts))


def get_channel_name(data: str) -> str:
    regex = re.compile(CHANNEL_NAME_SEP)
    return re.sub(CHANNEL_NAME_REPL, "_", regex.search(data).group(1).lower())


def kakaotalk_to_slack(read_file: str, save_dir: str, split: bool = True) -> None:
    # 1. read data
    with open(read_file, "r", encoding="utf-8") as f:
        data = f.read() + "\n\n"

    # 2. group by date
    df = pd.DataFrame(index_by_date(data), columns=["date", "start", "end"])
    df["end"] = df["end"].shift(-1, fill_value=-1)

    # 3. slice data by date
    df["data"] = df.apply(split_by_date, args=(data,), axis=1)

    # 4. group by text
    df["message"] = df["data"].apply(index_by_message)
    df = df.explode("message").reset_index(drop=True).dropna()
    df[["user", "ts", "inviter", "subtype", "start", "end"]] = df["message"].tolist()
    df["end"] = df["end"].shift(-1, fill_value=-1)

    # 5. slice data by text
    df["text"] = df.apply(split_by_message, axis=1)
    df.drop(columns=["data", "message", "start", "end"], inplace=True)
    df.apply(fill_text, axis=1)

    # 6. make timestamp and format date
    df["ts"] = df["ts"].bfill().ffill()
    df["ts"] = df["date"] + " " + df["ts"]
    df["ts"] = df["ts"] + df["ts"].groupby(df["ts"]).cumcount().astype(str)
    df["ts"] = df["ts"].apply(make_ts)
    df["date"] = df["ts"].apply(format_date)

    # 7. save metadata to JSON
    os.makedirs(save_dir, exist_ok=True)
    channel_name = get_channel_name(data)
    members = set(df["user"].unique()) | set(df["inviter"].dropna().unique())
    channel_metadata = {"name": channel_name, "members": list(members)}

    channels_metafile = os.path.join(save_dir, "channels.json")
    if os.path.isfile(channels_metafile):
        with open(channels_metafile, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        json_data.append(channel_metadata)
        with open(channels_metafile, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False)
    else:
        with open(channels_metafile, "w", encoding="utf-8") as f:
            json.dump([channel_metadata], f, ensure_ascii=False)

    users_metafile = os.path.join(save_dir, "users.json")
    if os.path.isfile(users_metafile):
        with open(users_metafile, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        members = set(members) | set(json_data)
    with open(users_metafile, "w", encoding="utf-8") as f:
        json.dump({member: "" for member in members}, f, ensure_ascii=False)

    # 8. split df into text and attachment
    if split:
        has_attachment = df["text"].str.contains(ATTACHMENT_SEP, regex=True)
        df_text, df_attachment = df[~has_attachment], df[has_attachment]
        group_text = df_text.groupby("date")
        group_attachment = df_attachment.groupby("date")
        df_text.drop(columns=["date"], inplace=True)
        df_attachment.drop(columns=["date"], inplace=True)

        dir_text = os.path.join(save_dir, "text", channel_name)
        dir_attachment = os.path.join(save_dir, "attachment", channel_name)
        os.makedirs(dir_text, exist_ok=True)
        os.makedirs(dir_attachment, exist_ok=True)

        for date, group in group_text:
            save_file = os.path.join(dir_text, date + ".json")
            group.to_json(save_file, orient="records", force_ascii=False)

        for date, group in group_attachment:
            save_file = os.path.join(dir_attachment, date + ".json")
            group.to_json(save_file, orient="records", force_ascii=False)
    else:
        group = df.groupby("date")
        df.drop(columns=["date"], inplace=True)

        dir = os.path.join(save_dir, channel_name)
        os.makedirs(dir, exist_ok=True)

        for date, group in group:
            save_file = os.path.join(dir, date + ".json")
            group.to_json(save_file, orient="records", force_ascii=False)


if __name__ == "__main__":
    read_dir = "data/kakaotalk"
    save_dir = "data/slack"
    for file in os.listdir(read_dir):
        if file.endswith(".txt"):
            kakaotalk_to_slack(os.path.join(read_dir, file), save_dir, split=False)
