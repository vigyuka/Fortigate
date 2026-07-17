#!/usr/bin/env python3

import urllib.request
import json
import ssl


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


FMG = config["fortimanager"]
TOKEN = config["token"]
ADOM = config["adom"]


def fmg_request(url):

    payload = {
        "id": 1,
        "method": "get",
        "params": [
            {
                "url": url
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        FMG,
        data=data,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Content-Type": "application/json"
        }
    )

    ctx = ssl._create_unverified_context()

    response = urllib.request.urlopen(
        request,
        context=ctx,
        timeout=60
    )

    return json.loads(
        response.read().decode("utf-8")
    )


# Policy package lista betöltése

with open("policy_packages.json", "r", encoding="utf-8") as f:
    packages = json.load(f)


all_policies = []


for pkg in packages:

    pkg_name = pkg.get("name")

    print("Lekérés:", pkg_name)


    url = (
        "/pm/config/adom/{}/pkg/{}/firewall/policy"
        .format(
            ADOM,
            pkg_name
        )
    )


    result = fmg_request(url)


    status = result["result"][0]["status"]

    if status["code"] != 0:
        print(
            "HIBA:",
            pkg_name,
            status
        )
        continue


    policies = result["result"][0]["data"]


    for policy in policies:

        policy["_package"] = pkg_name
        all_policies.append(policy)


print()
print("Összes policy:", len(all_policies))


with open(
    "all_policies.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_policies,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Mentve: all_policies.json")
