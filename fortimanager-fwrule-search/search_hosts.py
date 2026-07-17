#!/usr/bin/env python3

import json
import ipaddress


HOST_FILE = "search_hosts.txt"
ADDRESS_FILE = "firewall_addresses.json"
FQDN_FILE = "fqdn_resolved.json"
OUTPUT_FILE = "search_ips.txt"


def is_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


#
# Fájlok betöltése
#

with open(
    HOST_FILE,
    encoding="utf-8"
) as f:

    search_hosts = [

        line.strip()

        for line in f

        if line.strip()

    ]


with open(
    ADDRESS_FILE,
    encoding="utf-8"
) as f:

    addresses = json.load(f)


try:

    with open(
        FQDN_FILE,
        encoding="utf-8"
    ) as f:

        fqdn_objects = json.load(f)

except FileNotFoundError:

    fqdn_objects = []


#
# FQDN index
#

fqdn_index = {}


for fqdn in fqdn_objects:

    name = fqdn.get(
        "name",
        ""
    ).lower()

    if name:

        fqdn_index[name] = fqdn


#
# Host/IP keresés
#

found_ips = set()


for item in search_hosts:

    #
    # Ha a keresett elem IP cím,
    # akkor azt automatikusan felvesszük.
    #

    if is_ip(item):

        found_ips.add(item)

        continue


    matched = None


    #
    # részleges név keresés
    #

    for addr in addresses:

        name = addr.get(
            "name",
            ""
        )

        if item.lower() in name.lower():

            matched = addr

            break


    if not matched:

        continue


    object_name = matched.get(
        "name"
    )


    obj_type = matched.get(
        "type"
    )


    #
    # FQDN objektum
    #

    if obj_type == 2:


        fqdn = fqdn_index.get(

            object_name.lower()

        )


        if fqdn:

            for ip in fqdn.get(
                "ip",
                []
            ):

                found_ips.add(ip)


    #
    # subnet objektum
    #

    elif obj_type == 0:


        subnet = matched.get(
            "subnet"
        )


        if subnet:


            network = ipaddress.ip_network(

                "{}/{}".format(

                    subnet[0],

                    subnet[1]

                ),

                strict=False

            )


            #
            # csak /32 host objektum
            #

            if network.prefixlen == 32:


                found_ips.add(

                    str(

                        network.network_address

                    )

                )


    #
    # IP range szándékosan nincs kezelve
    #

    elif obj_type == 1:

        continue


#
# search_ips.txt mentés
#

with open(

    OUTPUT_FILE,

    "w",

    encoding="utf-8"

) as f:


    for ip in sorted(found_ips):

        f.write(

            ip + "\n"

        )


print(

    "Talált IP-k:",

    len(found_ips)

)


print(

    "Mentve:",

    OUTPUT_FILE

)
