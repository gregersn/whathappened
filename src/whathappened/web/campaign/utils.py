import time
import requests

# TODO: Get API_KEY from elsewhere
API_KEY = "9c20c7b332f73ba030742a3efaf1e9240417e5f10006e42c8acfce1ee84c73b9"
PAD_HOST = "http://localhost:9001/"


def get_url(endpoint: str, params: dict[str, str]):
    return f"{PAD_HOST}/api/1.3.0/{endpoint}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"


def check_pad_connection(user_id: str, user_name: str, campaign_id: str):
    print("**** CHECK PAD CONNECTION *****")

    # headers = {"Authorization": f"Bearer {API_KEY}"}
    url = get_url("checkToken", {"apikey": API_KEY})
    r = requests.get(url)
    print(r)
    print(r.json())
    print(r.headers)

    url = get_url(
        "createAuthorIfNotExistsFor",
        {"apikey": API_KEY, "name": user_name, "authorMapper": user_id},
    )
    r = requests.get(url)
    print(r)
    author_id = r.json()["data"]["authorID"]

    url = get_url(
        "createGroupIfNotExistsFor", {"apikey": API_KEY, "groupMapper": campaign_id}
    )

    r = requests.get(url)
    print(r)
    group_id = r.json()["data"]["groupID"]

    url = get_url(
        "createGroupPad",
        {
            "apikey": API_KEY,
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
            "apikey": API_KEY,
            "groupID": group_id,
            "authorID": author_id,
            "validUntil": str(int(time.time() + 60 * 60)),
        },
    )

    r = requests.get(url)
    print(r)
    session_id = r.json()["data"]["sessionID"]

    print("*******************************")

    return {"author_id": author_id, "group_id": group_id, "session_id": session_id}
