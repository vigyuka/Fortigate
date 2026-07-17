#!/usr/bin/env python3

import urllib.request
import json
import ssl



#
# Konfiguráció betöltése
#

with open("config.json", "r", encoding="utf-8") as f:

    config = json.load(f)


FMG = config["fortimanager"]
TOKEN = config["token"]
ADOM = config["adom"]



#
# FortiManager API kérés
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

            "Authorization":
                "Bearer " + TOKEN,

            "Content-Type":
                "application/json"

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
# Address objektum lekérés
#

url = "/pm/config/adom/{}/obj/firewall/address".format(

    ADOM

)


result = fmg_request(url)



#
# API hibakezelés
#

status = result["result"][0]["status"]


if status["code"] != 0:

    print("API hiba:")

    print(status)

    exit(1)



addresses = result["result"][0]["data"]



#
# Mentés JSON-be
#

with open(

    "firewall_addresses.json",

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        addresses,

        f,

        indent=2,

        ensure_ascii=False

    )



print()

print("Mentve: firewall_addresses.json")

print("Összes address objektum:", len(addresses))

print("-" * 80)

