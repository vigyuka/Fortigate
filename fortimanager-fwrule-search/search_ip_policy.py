#!/usr/bin/env python3

import json
import ipaddress


#
# Beállítások
#

POLICY_PACKAGE = "KGIR"

SEARCH_IP_FILE = "search_ips.txt"

OUTPUT_FILE = "policy_search_results.json"


#
# JSON fájlok betöltése
#

with open("firewall_addresses.json", encoding="utf-8") as f:
    addresses = json.load(f)

with open("fqdn_resolved.json", encoding="utf-8") as f:
    fqdn_objects = json.load(f)

with open("firewall_addrgrp.json", encoding="utf-8") as f:
    addrgrps = json.load(f)

with open("all_policies.json", encoding="utf-8") as f:
    policies = json.load(f)

#
# Keresendő IP-k betöltése
#

with open(SEARCH_IP_FILE, encoding="utf-8") as f:

    search_ips = [
        line.strip()
        for line in f
        if line.strip()
    ]


#
# IP -> Address objektum keresés
#

def find_addresses(search_ip):

    ip = ipaddress.ip_address(search_ip)

    matched = set()


    #
    # 1. Először FQDN cache keresés
    #

    for fqdn in fqdn_objects:

        if str(ip) in fqdn.get("ip", []):

            matched.add(
                fqdn.get("name")
            )


    #
    # Ha FQDN találat van,
    # subnet/IP range keresés nincs
    #

    if matched:

        return matched



    #
    # 2. Address objektum keresés
    #

    for addr in addresses:

        obj_type = addr.get("type")

        name = addr.get("name")



        #
        # subnet
        #
        # csak /32 host objektum
        #

        if obj_type == 0:

            subnet = addr.get("subnet")


            if subnet:

                network = ipaddress.ip_network(
                    "{}/{}".format(
                        subnet[0],
                        subnet[1]
                    ),
                    strict=False
                )


                if network.prefixlen == 32:

                    if ip in network:

                        matched.add(name)



        #
        # IP range
        #

        elif obj_type == 1:

            start = addr.get("start-ip")
            end = addr.get("end-ip")


            if start and end:

                if (
                    ip >= ipaddress.ip_address(start)
                    and
                    ip <= ipaddress.ip_address(end)
                ):

                    matched.add(name)



    return matched

#
# Address Group index
#

member_to_group = {}


for group in addrgrps:

    group_name = group.get("name")


    for member in group.get("member", []):

        member_to_group.setdefault(
            member,
            []
        ).append(group_name)



#
# Rekurzív Address Group keresés
#

def find_groups(member):

    groups = set()


    for group in member_to_group.get(member, []):

        if group not in groups:

            groups.add(group)

            groups.update(
                find_groups(group)
            )


    return groups



#
# Action értelmezés
#

action_map = {

    0: "deny",
    1: "accept"

}



#
# Policy név kezelése
#

def get_policy_name(policy):

    return (

        policy.get("name")

        or

        policy.get("policy-name")

        or

        policy.get("comments")

        or

        "-"

    )



#
# Policy keresés
#

results = []



for search_ip in search_ips:


    addresses_found = find_addresses(search_ip)


    groups_found = set()


    for addr in addresses_found:

        groups_found.update(
            find_groups(addr)
        )


    search_objects = (

        addresses_found

        |

        groups_found

    )


    for policy in policies:


        #
        # Csak adott Policy Package
        #

#        if policy.get("_package") != POLICY_PACKAGE:
#
#            continue


        #
        # Disabled policy kihagyása
        #

        if str(policy.get("status", "1")) != "1":

            continue



        src = set(
            policy.get("srcaddr", [])
        )


        dst = set(
            policy.get("dstaddr", [])
        )


        src_hit = search_objects.intersection(src)

        dst_hit = search_objects.intersection(dst)


        if not src_hit and not dst_hit:

            continue



        action = action_map.get(

            policy.get("action"),

            str(policy.get("action", "-"))

        )


        package = policy.get("_package") or "-"

        policy_id = policy.get("policyid")

        policy_name = get_policy_name(policy)



        for obj in sorted(src_hit):

            results.append(

                {

                    "ip": search_ip,

                    "package": package,

                    "policy_id": policy_id,

                    "policy_name": policy_name,

                    "action": action,

                    "direction": "SRC",

                    "object": obj

                }

            )



        for obj in sorted(dst_hit):

            results.append(

                {

                    "ip": search_ip,

                    "package": package,

                    "policy_id": policy_id,

                    "policy_name": policy_name,

                    "action": action,

                    "direction": "DST",

                    "object": obj

                }

            )



#
# JSON eredmény mentése
#

with open(

    OUTPUT_FILE,

    "w",

    encoding="utf-8"

) as f:


    json.dump(

        results,

        f,

        indent=2,

        ensure_ascii=False

    )



#
# Konzol kimenet
#

print()


print("{:<16} {:<15} {:<8} {:<35} {:<8} {:<5} {}".format(

    "IP",

    "Package",

    "Policy",

    "Policy Name",

    "Action",

    "Dir",

    "Object"

))


print("-" * 125)



for r in results:


    print("{:<16} {:<15} {:<8} {:<35} {:<8} {:<5} {}".format(

        r["ip"],

        r["package"],

        str(r["policy_id"]),

        r["policy_name"],

        r["action"],

        r["direction"],

        r["object"]

    ))



print()

print("Keresett IP-k :", len(search_ips))

print("Találatok     :", len(results))

print("Mentve        :", OUTPUT_FILE)
