#!/usr/bin/env python3

import urllib.request
import json
import ssl


FMG = "https://10.121.132.192/jsonrpc"
TOKEN = "wfezy5mft4j8xon4tbxyj8bskhhainzp"
ADOM = "KGIR-7-2"


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

    context = ssl._create_unverified_context()

    response = urllib.request.urlopen(
        request,
        context=context,
        timeout=30
    )

    return json.loads(
        response.read().decode("utf-8")
    )


url = "/pm/config/adom/{}/obj/firewall/addrgrp".format(ADOM)

result = fmg_request(url)


status = result["result"][0]["status"]

if status["code"] != 0:
    print(status)
    exit(1)


groups = result["result"][0]["data"]

print("Address Group objektumok:", len(groups))


with open("firewall_addrgrp.json", "w", encoding="utf-8") as f:
    json.dump(
        groups,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Mentve: firewall_addrgrp.json")
