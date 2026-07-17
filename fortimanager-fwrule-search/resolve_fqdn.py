#!/usr/bin/env python3

import json
import socket



#
# Konfiguráció betöltése
#

with open(
    "config.json",
    "r",
    encoding="utf-8"
) as f:

    config = json.load(f)



LOCAL_DOMAINS = config.get(
    "local_domains",
    []
)



#
# Belső FQDN ellenőrzés
#

def is_internal_fqdn(fqdn):

    fqdn = fqdn.lower()


    for domain in LOCAL_DOMAINS:

        if fqdn.endswith(
            domain.lower()
        ):

            return True


    return False



#
# Address objektumok betöltése
#

with open(
    "firewall_addresses.json",
    "r",
    encoding="utf-8"
) as f:

    addresses = json.load(f)



resolved = []



#
# FQDN objektumok feloldása
#

for addr in addresses:


    #
    # csak FQDN objektum
    #

    if addr.get("type") != 2:

        continue



    fqdn = addr.get("fqdn")


    if not fqdn:

        continue



    #
    # csak belső domainek
    #

    if not is_internal_fqdn(fqdn):

        continue



    try:

        ips = socket.gethostbyname_ex(fqdn)[2]


        resolved.append({

            "name": addr.get("name"),

            "fqdn": fqdn,

            "ip": ips

        })


    except socket.gaierror:

        continue



#
# Mentés
#

with open(

    "fqdn_resolved.json",

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        resolved,

        f,

        indent=2,

        ensure_ascii=False

    )



print(
    "Mentve:",
    len(resolved),
    "FQDN objektum"
)
