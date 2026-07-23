#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import glob
import json
import os
import ssl
import sys
import tempfile

from urllib.parse import quote
import urllib.request



class FortiManagerAPI(object):

    def __init__(self, host, token):

        self.url = "https://{}/jsonrpc".format(host)
        self.token = token
        self.context = ssl._create_unverified_context()



    def call(self, url):

        payload = {
            "id": 1,
            "method": "get",
            "params": [
                {
                    "url": url
                }
            ]
        }


        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json"
            }
        )


        response = urllib.request.urlopen(
            request,
            context=self.context,
            timeout=20
        )


        result = json.loads(
            response.read().decode("utf-8")
        )


        api_result = result["result"][0]


        status = api_result.get(
            "status",
            {}
        )


        if status.get("code", 0) != 0:

            raise Exception(
                status.get(
                    "message",
                    "API error"
                )
            )


        return api_result.get(
            "data",
            []
        )



    def proxy_get(
            self,
            target,
            resource):


        payload = {
            "id": 1,
            "method": "exec",
            "params": [
                {
                    "url": "/sys/proxy/json",
                    "data": {
                        "target": [
                            target
                        ],
                        "action": "get",
                        "resource": resource
                    }
                }
            ]
        }


        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer {}".format(self.token),
                "Content-Type": "application/json"
            }
        )


        response = urllib.request.urlopen(
            request,
            context=self.context,
            timeout=30
        )


        result = json.loads(
            response.read().decode("utf-8")
        )


        api_result = result["result"][0]


        status = api_result.get(
            "status",
            {}
        )


        if status.get("code", 0) != 0:

            raise Exception(
                status.get(
                    "message",
                    "Proxy API error"
                )
            )


        return api_result["data"][0]["response"]




def save_pem_atomic(
        filename,
        pem):


    directory = os.path.dirname(
        filename
    )


    if not os.path.exists(directory):

        os.makedirs(directory)


    fd, tmpfile = tempfile.mkstemp(
        dir=directory
    )


    try:

        with os.fdopen(
            fd,
            "w"
        ) as f:

            f.write(
                pem
            )


        os.chmod(
            tmpfile,
            0o600
        )


        os.rename(
            tmpfile,
            filename
        )


    except Exception:

        try:

            os.unlink(
                tmpfile
            )

        except Exception:

            pass


        raise




def clean_filename(value):

    for char in [
        "/",
        "\\",
        " ",
        ":"
    ]:

        value = value.replace(
            char,
            "_"
        )

    return value




def is_ignored(
        cert,
        ignore_names,
        ignore_comments):


    name = cert.get(
        "name",
        ""
    )


    comment = cert.get(
        "comment",
        ""
    )


    if name in ignore_names:

        return True


    if comment in ignore_comments:

        return True


    return False




def export_fmg_certificates(
        fmg,
        fmg_name,
        output_dir,
        ignore_names,
        ignore_comments,
        stats):


    cert_types = [

        (
            "local",
            "local-cer",
            "certificate"
        ),

        (
            "ca",
            "ca",
            "ca"
        ),

        (
            "remote",
            "remote-ca",
            "certificate"
        )

    ]


    exported = []


    for api_name, file_type, pem_key in cert_types:


        try:

            cert_list = fmg.call(
                "/cli/global/system/certificate/{}".format(
                    api_name
                )
            )


        except Exception as e:


            stats["errors"] += 1


            print(
                "[{}] FMG {} list error: {}".format(
                    fmg_name,
                    api_name,
                    e
                )
            )


            continue



        for cert in cert_list:


            if is_ignored(
                cert,
                ignore_names,
                ignore_comments
            ):

                continue


            name = cert.get(
                "name"
            )


            if not name:

                continue



            try:


                detail = fmg.call(
                    "/cli/global/system/certificate/{}/{}".format(
                        api_name,
                        quote(name)
                    )
                )


                if not detail:

                    continue


                pem = detail.get(
                    pem_key
                )


                if not pem:

                    continue


                if isinstance(
                    pem,
                    list
                ):

                    pem = pem[0]


                pem = pem.replace(
                    "\\n",
                    "\n"
                )


                filename = os.path.join(

                    output_dir,

                    "{}__FMG__global__{}__{}.pem".format(

                        fmg_name,

                        file_type,

                        clean_filename(name)

                    )

                )


                save_pem_atomic(
                    filename,
                    pem
                )


                exported.append(
                    filename
                )


                stats["certificates"] += 1


                print(
                    "[{}] Exported {}".format(
                        fmg_name,
                        filename
                    )
                )


            except Exception as e:


                stats["errors"] += 1


                print(
                    "[{}] {} export error: {}".format(
                        fmg_name,
                        name,
                        e
                    )
                )


    return exported

def download_certificate(
        fmg,
        target,
        cert_name,
        scope,
        cert_type,
        vdom=None):


    url = (
        "/api/v2/monitor/system/certificate/download/"
        + quote(cert_name)
        + "?scope="
        + scope
        + "&type="
        + cert_type
    )


    if vdom:

        url += (
            "&vdom="
            + quote(vdom)
        )


    return fmg.proxy_get(
        target,
        url
    )




def export_fortigate_certificates(
        fmg,
        target,
        fmg_name,
        device_name,
        certs,
        output_dir,
        scope,
        expected_range,
        cert_type,
        api_type,
        ignore_names,
        ignore_comments,
        stats,
        vdom=None):


    exported = []


    for cert in certs:


        if is_ignored(
            cert,
            ignore_names,
            ignore_comments
        ):

            continue


        if cert.get(
            "source"
        ) != "user":

            continue


        if cert.get(
            "range"
        ) != expected_range:

            continue


        name = cert.get(
            "name"
        )


        if not name:

            continue


        try:


            pem = download_certificate(
                fmg,
                target,
                name,
                scope,
                cert_type,
                vdom
            )


            parts = [

                fmg_name,

                device_name

            ]


            if vdom:

                parts.append(
                    vdom
                )

            else:

                parts.append(
                    "global"
                )


            parts.extend(
                [

                    api_type,

                    clean_filename(name)

                ]
            )


            filename = os.path.join(

                output_dir,

                "__".join(parts) + ".pem"

            )


            save_pem_atomic(
                filename,
                pem
            )


            exported.append(
                filename
            )


            stats["certificates"] += 1


            print(
                "[{}] Exported {}".format(
                    device_name,
                    filename
                )
            )


        except Exception as e:


            stats["errors"] += 1


            print(
                "[{}] {} export error: {}".format(
                    device_name,
                    name,
                    e
                )
            )


    return exported




def get_vdoms(
        fmg,
        target):


    result = fmg.proxy_get(

        target,

        "/api/v2/cmdb/system/vdom"

    )


    return [

        x["name"]

        for x in result.get(
            "results",
            []
        )

    ]




def cleanup_old(
        prefix,
        output_dir,
        exported):


    files = glob.glob(

        os.path.join(

            output_dir,

            prefix + "*.pem"

        )

    )


    for filename in files:


        if filename not in exported:


            os.remove(
                filename
            )


            print(
                "Removed old {}".format(
                    filename
                )
            )




def process_device(
        fmg,
        fmg_name,
        device,
        output_dir,
        ignore_names,
        ignore_comments,
        stats):


    device_name = device["name"]


    stats["devices"] += 1


    target = (

        "adom/{}/device/{}"

        .format(

            fmg.adom,

            device_name

        )

    )


    exported = []


    print(
        "[{}] Processing".format(
            device_name
        )
    )


    try:


        # GLOBAL LOCAL CERT

        local = fmg.proxy_get(

            target,

            "/api/v2/cmdb/vpn.certificate/local"

        )


        exported.extend(

            export_fortigate_certificates(

                fmg,

                target,

                fmg_name,

                device_name,

                local.get(
                    "results",
                    []
                ),

                output_dir,

                "global",

                "global",

                "local-cer",

                "local-cer",

                ignore_names,

                ignore_comments,

                stats

            )

        )



        # GLOBAL REMOTE CA

        ca = fmg.proxy_get(

            target,

            "/api/v2/cmdb/vpn.certificate/ca"

        )


        exported.extend(

            export_fortigate_certificates(

                fmg,

                target,

                fmg_name,

                device_name,

                ca.get(
                    "results",
                    []
                ),

                output_dir,

                "global",

                "global",

                "remote-ca",

                "remote-ca",

                ignore_names,

                ignore_comments,

                stats

            )

        )



        # VDOM

        for vdom in get_vdoms(

            fmg,

            target

        ):


            local = fmg.proxy_get(

                target,

                "/api/v2/cmdb/vpn.certificate/local?vdom={}".format(

                    quote(vdom)

                )

            )


            exported.extend(

                export_fortigate_certificates(

                    fmg,

                    target,

                    fmg_name,

                    device_name,

                    local.get(
                        "results",
                        []
                    ),

                    output_dir,

                    "vdom",

                    "vdom",

                    "local-cer",

                    "local-cer",

                    ignore_names,

                    ignore_comments,

                    stats,

                    vdom

                )

            )


            ca = fmg.proxy_get(

                target,

                "/api/v2/cmdb/vpn.certificate/ca?vdom={}".format(

                    quote(vdom)

                )

            )


            exported.extend(

                export_fortigate_certificates(

                    fmg,

                    target,

                    fmg_name,

                    device_name,

                    ca.get(
                        "results",
                        []
                    ),

                    output_dir,

                    "vdom",

                    "vdom",

                    "remote-ca",

                    "remote-ca",

                    ignore_names,

                    ignore_comments,

                    stats,

                    vdom

                )

            )



        cleanup_old(

            "{}__{}__".format(

                fmg_name,

                device_name

            ),

            output_dir,

            exported

        )


        stats["devices_ok"] += 1



        print(

            "[{}] Completed {}".format(

                device_name,

                len(exported)

            )

        )


    except Exception as e:


        stats["errors"] += 1


        print(

            "[{}] ERROR: {}".format(

                device_name,

                e

            )

        )


def process_adom(
        name,
        cfg,
        output_dir,
        ignore_names,
        ignore_comments,
        stats):


    stats["adom"] += 1


    fmg = FortiManagerAPI(

        cfg["host"],

        cfg["token"]

    )


    fmg.adom = cfg["adom"]



    print(

        "[{}] Processing FortiManager certificates".format(

            name

        )

    )


    export_fmg_certificates(

        fmg,

        name,

        output_dir,

        ignore_names,

        ignore_comments,

        stats

    )



    print(

        "[{}] Processing ADOM {}".format(

            name,

            fmg.adom

        )

    )



    devices = fmg.call(

        "/dvmdb/adom/{}/device".format(

            fmg.adom

        )

    )


    if not devices:


        print(

            "[{}] No managed devices".format(

                name

            )

        )


        return



    for device in devices:


        process_device(

            fmg,

            name,

            device,

            output_dir,

            ignore_names,

            ignore_comments,

            stats

        )




def print_summary(stats):


    print("")

    print(
        "========== SUMMARY =========="
    )


    print(
        "ADOM processed : {}".format(
            stats["adom"]
        )
    )


    print(
        "Devices found  : {}".format(
            stats["devices"]
        )
    )


    print(
        "Devices OK     : {}".format(
            stats["devices_ok"]
        )
    )


    print(
        "Certificates   : {}".format(
            stats["certificates"]
        )
    )


    print(
        "Errors         : {}".format(
            stats["errors"]
        )
    )


    print(
        "============================="
    )




def main():


    parser = argparse.ArgumentParser(

        description="FortiManager and FortiGate certificate exporter"

    )


    parser.add_argument(

        "--config",

        default="/etc/fmg.conf",

        help="Config file"

    )


    args = parser.parse_args()



    config = configparser.ConfigParser()



    if not config.read(

        args.config

    ):


        print(

            "Cannot read config"

        )


        return 2




    output_dir = "/var/lib/monitoring/fmg-certs"


    ignore_names = []

    ignore_comments = []



    if "global" in config:


        output_dir = config["global"].get(

            "output_dir",

            output_dir

        )


        ignore_names = [

            x.strip()

            for x in config["global"].get(

                "ignore_name",

                ""

            ).split(",")

            if x.strip()

        ]


        ignore_comments = [

            x.strip()

            for x in config["global"].get(

                "ignore_comment",

                ""

            ).split(",")

            if x.strip()

        ]




    stats = {

        "adom": 0,

        "devices": 0,

        "devices_ok": 0,

        "certificates": 0,

        "errors": 0

    }



    exit_code = 0



    for section in config.sections():


        if section.lower() == "global":

            continue



        try:


            process_adom(

                section,

                config[section],

                output_dir,

                ignore_names,

                ignore_comments,

                stats

            )


        except Exception as e:


            stats["errors"] += 1


            exit_code = 1


            print(

                "[{}] ERROR: {}".format(

                    section,

                    e

                )

            )




    if stats["errors"] > 0:

        exit_code = 1



    print_summary(

        stats

    )



    print(

        "Exit code: {}".format(

            exit_code

        )

    )



    return exit_code





if __name__ == "__main__":


    sys.exit(

        main()

    )
