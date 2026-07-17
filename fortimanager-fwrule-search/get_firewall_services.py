#!/usr/bin/env python3

import urllib.request
import json
import ssl


#
# Konfiguráció
#

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


FMG = config["fortimanager"]
TOKEN = config["token"]
ADOM = config["adom"]



#
# FortiManager API hívás
#

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



#
# Service objektumok lekérése
#

url = (
    f"/pm/config/adom/{ADOM}/obj/firewall/service/custom"
)


result = fmg_request(url)



#
# Ellenőrzés
#

if result["result"][0]["status"]["code"] != 0:

    print(result)

    exit(1)



services = result["result"][0]["data"]



#
# Mentés
#

with open(

    "firewall_services.json",

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        services,

        f,

        indent=2,

        ensure_ascii=False

    )



print()

print(
    "Lekért service objektumok:",
    len(services)
)

print(
    "Mentve: firewall_services.json"
)
