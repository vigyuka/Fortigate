#!/usr/bin/env python3

import json
import csv


RESULT_FILE = "policy_search_results.json"
POLICY_FILE = "all_policies.json"
ADDRESS_FILE = "firewall_addresses.json"
ADDRGRP_FILE = "firewall_addrgrp.json"
SERVICE_FILE = "firewall_services.json"
FQDN_FILE = "fqdn_resolved.json"

OUTPUT_FILE = "policy_report.csv"



#
# JSON betöltések
#

with open(RESULT_FILE, encoding="utf-8") as f:
    search_results = json.load(f)


with open(POLICY_FILE, encoding="utf-8") as f:
    policies = json.load(f)


with open(ADDRESS_FILE, encoding="utf-8") as f:
    addresses = json.load(f)


with open(ADDRGRP_FILE, encoding="utf-8") as f:
    addrgrps = json.load(f)


with open(SERVICE_FILE, encoding="utf-8") as f:
    services = json.load(f)


with open(FQDN_FILE, encoding="utf-8") as f:
    fqdn_objects = json.load(f)



#
# Address index
#

address_index = {}

for addr in addresses:

    name = addr.get("name")

    if name:

        address_index[name] = addr



#
# FQDN index
#

fqdn_index = {}

for fqdn in fqdn_objects:

    name = fqdn.get("name")

    if name:

        fqdn_index[name] = fqdn



#
# Address group index
#

group_index = {}

for group in addrgrps:

    name = group.get("name")

    if name:

        group_index[name] = group



#
# Service index
#

service_index = {}

for svc in services:

    name = svc.get("name")

    if name:

        service_index[name] = svc



#
# Action fordítás
#

def action_text(value):

    if value == 1 or value == "1":

        return "allowed"

    if value == 0 or value == "0":

        return "deny"

    return str(value)



#
# Status fordítás
#

def status_text(value):

    if value == 1 or value == "1":

        return "enabled"

    if value == 0 or value == "0":

        return "disabled"

    return str(value)



#
# Address objektum feloldás
#

def resolve_address(name):

    addr = address_index.get(name)


    if not addr:

        return name



    obj_type = addr.get("type")



    #
    # subnet
    #

    if obj_type == 0:

        subnet = addr.get("subnet")

        if subnet:

            return "{} ({}/{})".format(

                name,

                subnet[0],

                subnet[1]

            )



    #
    # IP range
    #

    elif obj_type == 1:

        return "{} ({}-{})".format(

            name,

            addr.get("start-ip"),

            addr.get("end-ip")

        )



    #
    # FQDN
    #

    elif obj_type == 2:

        fqdn = fqdn_index.get(name)


        if fqdn:

            ips = fqdn.get("ip", [])


            if ips:

                return "{} ({})".format(

                    name,

                    ",".join(ips)

                )


    return name



#
# Address group rekurzív feloldás
#

def resolve_group(name, visited=None):

    if visited is None:

        visited = set()



    if name in visited:

        return [

            name + " (circular reference)"

        ]



    visited.add(name)



    group = group_index.get(name)



    if not group:

        return [

            resolve_address(name)

        ]



    result = []



    for member in group.get("member", []):


        if member in group_index:


            result.extend(

                resolve_group(

                    member,

                    visited.copy()

                )

            )


        else:

            result.append(

                resolve_address(member)

            )



    return result



#
# Policy address feloldás
#

def resolve_policy_address(name):

    if name in group_index:

        members = resolve_group(name)


        return "{} => {}".format(

            name,

            " | ".join(members)

        )


    return resolve_address(name)



#
# Service feloldás
#

def resolve_service(name):

    svc = service_index.get(name)


    if not svc:

        return name



    result = []


    tcp = svc.get("tcp-portrange")

    udp = svc.get("udp-portrange")



    if tcp:

        if isinstance(tcp, list):

            for port in tcp:

                result.append(

                    "TCP/" + str(port)

                )

        else:

            result.append(

                "TCP/" + str(tcp)

            )



    if udp:

        if isinstance(udp, list):

            for port in udp:

                result.append(

                    "UDP/" + str(port)

                )

        else:

            result.append(

                "UDP/" + str(udp)

            )



    if result:

        return "{} ({})".format(

            name,

            ",".join(result)

        )


    return name



#
# Policy index
# kulcs: (package, policy_id)
#

policy_index = {}


for policy in policies:

    pid = policy.get("policyid")

    package = policy.get("_package")


    if pid is not None and package:

        policy_index[

            (

                package,

                pid

            )

        ] = policy



#
# Policy találatok összegyűjtése
#

policy_ip_map = {}


for result in search_results:

    pid = result.get("policy_id")

    package = result.get("package")


    if not package:

        package = result.get("_package")


    ip = result.get("ip")



    key = (

        package,

        pid

    )


    if key not in policy_ip_map:

        policy_ip_map[key] = set()



    if ip:

        policy_ip_map[key].add(ip)



#
# CSV export
#

with open(

    OUTPUT_FILE,

    "w",

    newline="",

    encoding="utf-8-sig"

) as f:


    writer = csv.writer(

        f,

        delimiter=";"

    )


    writer.writerow([

        "IP",

        "Package",

        "Policy ID",

        "Policy Name",

        "Source",

        "Destination",

        "Service",

        "Action",

        "Status"

    ])



    for key in sorted(policy_ip_map):


        package, pid = key


        policy = policy_index.get(key)



        if not policy:

            continue



        src = []


        for item in policy.get("srcaddr", []):

            src.append(

                resolve_policy_address(item)

            )



        dst = []


        for item in policy.get("dstaddr", []):

            dst.append(

                resolve_policy_address(item)

            )



        svc = []


        for item in policy.get("service", []):

            svc.append(

                resolve_service(item)

            )



        writer.writerow([

            ", ".join(

                sorted(

                    policy_ip_map[key]

                )

            ),


            package,


            pid,


            policy.get("name") or "-",


            ", ".join(src),


            ", ".join(dst),


            ", ".join(svc),


            action_text(

                policy.get("action")

            ),


            status_text(

                policy.get("status")

            )

        ])



print()

print("Riport elkészült:")

print(OUTPUT_FILE)
