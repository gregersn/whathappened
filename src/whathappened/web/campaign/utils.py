import time
import requests
from pathlib import Path

from flask import current_app


def get_api_key():
    api_key = current_app.config.get("ETHERPAD_API_KEY")
    if isinstance(api_key, Path) and api_key.is_file():
        return open(api_key, "r", encoding="utf8").read()

    if isinstance(api_key, str):
        return api_key


def get_pad_host():
    return current_app.config.get(
        "ETHERPAD_INSTANCE", None
    )  #  "http://localhost:9001/"


def get_url(endpoint: str, params: dict[str, str]):
    return f"{get_pad_host()}/api/1.3.0/{endpoint}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"


def check_pad_connection(
    user_id: str, user_name: str, campaign_id: str
) -> dict[str, str]:
    print("**** CHECK PAD CONNECTION *****")

    # headers = {"Authorization": f"Bearer {API_KEY}"}
    url = get_url("checkToken", {"apikey": get_api_key()})
    r = requests.get(url)
    print(r)
    print(r.json())
    print(r.headers)

    url = get_url(
        "createAuthorIfNotExistsFor",
        {"apikey": get_api_key(), "name": user_name, "authorMapper": user_id},
    )
    r = requests.get(url)
    print(r)
    author_id = r.json()["data"]["authorID"]

    url = get_url(
        "createGroupIfNotExistsFor",
        {"apikey": get_api_key(), "groupMapper": campaign_id},
    )

    r = requests.get(url)
    print(r)
    group_id = r.json()["data"]["groupID"]

    url = get_url(
        "createGroupPad",
        {
            "apikey": get_api_key(),
            "groupID": group_id,
            "padName": f"campaign_document_{campaign_id}",
        },
    )

    r = requests.get(url)
    print(r)
    print(r.json())

    url = get_url(
        "createSession",
        {
            "apikey": get_api_key(),
            "groupID": group_id,
            "authorID": author_id,
            "validUntil": str(int(time.time() + 60 * 60)),
        },
    )

    r = requests.get(url)
    print(r)
    session_id = r.json()["data"]["sessionID"]

    print("*******************************")

    return {
        "author_id": author_id,
        "group_id": group_id,
        "session_id": session_id,
        "endpoint": current_app.config.get("ETHERPAD_ENDPOINT"),
    }
