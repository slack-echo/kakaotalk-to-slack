## Structure

```
samples
├── README.md
├── kakaotalk
│   ├── KakaoTalk_%Y%m%d_%H%M_%S_{ms}_group.txt
│   ... 
└── slack
    ├──{workspace_name} Slack export %b %d %Y - %b %d %Y.zip
    │   ├── channels.json
    │   ├── integration_logs.json
    │   ├── users.json
    │   ├──{channel_name}
    │   │   ├── %Y-%m-%d.json
    │   │   ...
    │   ├──{channel_name}
    │   │   ├── %Y-%m-%d.json
    │   │   ...
    │   ...
    ...  
```

## Exported Data Samples

### Slack Exported Data Samples

channels.json:
```
{
    "id" (str): "C[0-9A-Z]{8|10}",
    "name" (str): "[0-9a-z_\-ㄱ-ㅎㅏ-ㅣ가-힣]{1,80}",
    "created" (int): time.strftime("%s"),
    "creator" (str): "U[0-9A-Z]{8|10}",
    "is_archived" (bool): true|false,
    "is_general" (bool): true|false,
    "members" (list): ["U[0-9A-Z]{8|10}[,U[0-9A-Z]{8|10} ...]"],
    "pins" (list|optional): [
        {
            "id" (str):  "{time.time():.6f}",
            "type" (str): "C",
            "created" (int): 0,
            "user" (str): "U[0-9A-Z]{8|10}",
            "owner" (str): "U[0-9A-Z]{8|10}",
        }
    ],
    "topic" (dict): {
        "value" (str): "{topic}",
        "creator" (str): ""|"U[0-9A-Z]{8|10}",
        "last_set" (int): 0|time.strftime("%s")
    },
    "purpose" (dict): {
        "value" (str): "{purpose}",
        "creator" (str): ""|"U[0-9A-Z]{8|10}",
        "last_set" (int): 0|time.strftime("%s")
    }
}
```

integration_logs.json:
```
{
    "user_id" (str): "U[0-9A-Z]{8|10}",
    "user_name" (str): "{user_name}",
    "date" (str): "{time.strftime("%s")}",
    "change_type" (str): "added"|"enabled"|"disabled"|"updated"|"expanded"|"removed"|"resource_grant_created"|"wildcard_resource_grant_created",
    "reason" (str|optional): ["user"|"user_deactivated"|"user_uninstalled_app"|"server"|"app_migration"],
    "service_id" (int|*): [0-9]{12},
    "service_type" (str|**): "{service_type}",
    "scope" (str|optional): [null|"{scope}[,{scope} ...]"],
    "channel" (str|optional): ["private"|"C[0-9A-Z]{8|10}"|"G[0-9A-Z]{8|10}"],
    "app_id" (str|*): "A[0-9A-Z]{8|10}",
    "app_type" (str|**): "{app_type}"
}
```

users.json:
```
{
    "id" (str): "U[0-9A-Z]{8|10}",
    "team_id" (str): "T[0-9A-Z]{8|10}",
    "name" (str): "{user_name}",
    "deleted" (bool|#): true|false,
    "color" (str|~#): "{color hex:6}",
    "real_name" (str|~#): "{real_name}",
    "tz" (str|~#): "{Continent/Region}",
    "tz_label" (str|~#): "{timezone label}",
    "tz_offset" (int|~#): {timezone offset:sec},
    "profile" (dict): {
        "title" (str): ""|"{title}",
        "phone" (str): ""|"{phone}",
        "skype" (str): ""|"{skype}",
        "real_name" (str): "{real_name}",
        "real_name_normalized" (str): "{real_name}",
        "display_name" (str): ""|"{display_name}",
        "display_name_normalized" (str): ""|"{display_name}",
        "fields" (dict): {},
        "status_text" (str): "{status_text}",
        "status_emoji" (str): "{status_emoji}",
        "status_emoji_display_info" (list): [],
        "status_expiration" (int): 0|time.strftime("%s"),
        "avatar_hash" (str): "{[0-9a-z]{20}:12}",
        "api_app_id" (str|:robot:): "A[0-9A-Z]{8|10}",
        "always_active" (bool|:robot:): true|false,
        "image_original" (str|!): "{image_original}",
        "is_custom_image" (bool|!): true,
        "bot_id" (str|:robot:): "B[0-9A-Z]{8|10}",
        "email" (str|:man:): "{email}",
        "first_name" (str|@): "{first_name}",
        "last_name" (str|@): "{last_name}",
        "image_24" (str): "{image_24}",
        "image_32" (str): "{image_32}",
        "image_48" (str): "{image_48}",
        "image_72" (str): "{image_72}",
        "image_192" (str): "{image_192}",
        "image_512" (str): "{image_512}",
        "image_1024" (str|!): "{image_1024}",
        "status_text_ canonical" (str): "{status_text_canonical}",
        "team" (str): "T[0-9A-Z]{8|10}"
    },
    "is_admin" (bool|~#): true|false,
    "is_owner" (bool|~#): true|false,
    "is_primary_owner" (bool|~#): true|false,
    "is_restricted" (bool|~#): true|false,
    "is_ultra_restricted" (bool|~#): true|false,
    "is_bot" (bool): true|false,
    "is_app_user" (bool): true|false,
    "updated" (int): time.strftime("%s"),
    "is_email_confirmed" (bool|~#): true|false
    "who_can_share_contact_card" (str|~#): "EVERYONE"|"TEAM_ONLY"|"NO_ONE"
}
```
- `*`, `**` : either or both of these pair of fields are required.

- `#` : these fields(`~#`) are not required only if `delted` is true.

- `!` : only if `is_custom_image` true and the link pattern is `"https:\/\/avatars.slack-edge.com\/%Y-%m-%d\/{}_{avatar_hash:20}_{dp}.png"`. The defult link pattern is `"https:\/\/secure.gravatar.com\/avatar\/{sha32}.jpg?s={dp}&d=_https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_{0000..9999}-{dp}.png"`.

||deleted|*name|is_custom_image|
|:--|:--|:--|:--|
|:robot:|true/false|exist/null|true|
|:man:|true/false|exist/null|true/false|

- `service_id` and `service_type` are legacy fields, and `app_id` and `app_type` are the new fields.

- The length of `user_id`, `channel_id` and `app_id` is 8 for the legacy, and 10 for the new.

- `scope` : `{scope}` can be `{scope}[(.|:){scope}]` recursively. 
The latter scope is a subscope of the former.
For more information, see https://api.slack.com/scopes 

### KakoTalk Exported Data Samples

KakaoTalk_%Y%m%d_%H%M_%S_{ms}_group.txt:
```
{group_name} 님과 카카오톡 대화
저장한 날짜 : %Y-%m-%d %H:%M:%S

--------------- %Y년 %-m월 %-d일 %a요일 ---------------
[{user_name}] [%p %-H:%m] {text}
--------------- %Y년 %-m월 %-d일 %a요일 ---------------
[{user_name}] [%p %-H:%m] {text line1
line2
line3
line4
line5}
--------------- %Y년 %-m월 %-d일 %a요일 ---------------
[{user_name}] [%p %-H:%m] 사진
[{user_name}] [%p %-H:%m] 사진 2장
[{user_name}] [%p %-H:%m] 톡게시판 '투표 종료': {poll_title}
```