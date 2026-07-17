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
        timeout=30
    )

    return json.loads(
        response.read().decode("utf-8")
    )


url = "/pm/pkg/adom/{}".format(ADOM)

result = fmg_request(url)

packages = result["result"][0]["data"]

print("Policy package darabszám:", len(packages))
print("-" * 60)

for pkg in packages:
    print(
        pkg.get("name"),
        " | oid:",
        pkg.get("oid")
    )


with open("policy_packages.json", "w", encoding="utf-8") as f:
    json.dump(
        packages,
        f,
        indent=2,
        ensure_ascii=False
    )


print()
print("Mentve: policy_packages.json")
