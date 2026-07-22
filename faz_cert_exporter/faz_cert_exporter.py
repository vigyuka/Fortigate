faz_cert_all.py
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
import urllib.request


class FortiAnalyzerAPI(object):

    def __init__(self, host, token):

        self.url = "https://{}/jsonrpc".format(host)
        self.token = token
        self.context = ssl._create_unverified_context()


    def call(self, cli_url):

        payload = {
            "id": 1,
            "method": "get",
            "params": [
                {
                    "url": cli_url
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
            timeout=15
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

        return api_result["data"]



def save_pem_atomic(filename, pem):

    directory = os.path.dirname(filename)

    if not os.path.exists(directory):
        os.makedirs(directory)


    fd, tmpfile = tempfile.mkstemp(
        dir=directory
    )

    try:

        with os.fdopen(fd, "w") as f:
            f.write(pem)


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
            os.unlink(tmpfile)
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



def export_local_certificates(
        faz_name,
        certs,
        output_dir,
        ignore_names,
        ignore_comments):

    exported = []


    for cert in certs:


        if is_ignored(
            cert,
            ignore_names,
            ignore_comments
        ):
            continue


        name = cert.get(
            "name"
        )


        if "certificate" not in cert:
            continue


        pem = cert["certificate"][0]


        pem = pem.replace(
            "\\n",
            "\n"
        )


        filename = os.path.join(
            output_dir,
            "{}_local_{}.pem".format(
                faz_name,
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


        print(
            "[{}] Exported {}".format(
                faz_name,
                filename
            )
        )


    return exported



def export_ca_certificates(
        faz_name,
        certs,
        output_dir,
        ignore_names,
        ignore_comments):

    exported = []


    for cert in certs:


        if is_ignored(
            cert,
            ignore_names,
            ignore_comments
        ):
            continue


        name = cert.get(
            "name"
        )


        if "ca" not in cert:
            continue


        pem = cert["ca"][0]


        pem = pem.replace(
            "\\n",
            "\n"
        )


        filename = os.path.join(
            output_dir,
            "{}_ca_{}.pem".format(
                faz_name,
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


        print(
            "[{}] Exported {}".format(
                faz_name,
                filename
            )
        )


    return exported



def cleanup_old_certificates(
        faz_name,
        output_dir,
        exported_files):

    pattern = os.path.join(
        output_dir,
        "{}_*.pem".format(faz_name)
    )


    existing_files = glob.glob(
        pattern
    )


    for filename in existing_files:


        if filename not in exported_files:

            os.remove(
                filename
            )


            print(
                "[{}] Removed old {}".format(
                    faz_name,
                    filename
                )
            )



def process_faz(
        name,
        cfg,
        output_dir,
        ignore_names,
        ignore_comments):


    host = cfg.get(
        "host"
    )

    token = cfg.get(
        "token"
    )


    if not host:
        raise Exception(
            "Missing host"
        )


    if not token:
        raise Exception(
            "Missing token"
        )


    print(
        "[{}] Connecting {}".format(
            name,
            host
        )
    )


    faz = FortiAnalyzerAPI(
        host,
        token
    )


    local = faz.call(
        "/cli/global/system/certificate/local"
    )


    ca = faz.call(
        "/cli/global/system/certificate/ca"
    )


    exported_files = []


    exported_files.extend(
        export_local_certificates(
            name,
            local,
            output_dir,
            ignore_names,
            ignore_comments
        )
    )


    exported_files.extend(
        export_ca_certificates(
            name,
            ca,
            output_dir,
            ignore_names,
            ignore_comments
        )
    )


    cleanup_old_certificates(
        name,
        output_dir,
        exported_files
    )


    print(
        "[{}] Completed, exported: {}".format(
            name,
            len(exported_files)
        )
    )



def main():

    parser = argparse.ArgumentParser(
        description="FortiAnalyzer certificate exporter"
    )


    parser.add_argument(
        "--config",
        default="/etc/faz.conf",
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



    output_dir = "/var/lib/monitoring/faz-certs"

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



    exit_code = 0


    for section in config.sections():


        if section.lower() == "global":
            continue


        try:

            process_faz(
                section,
                config[section],
                output_dir,
                ignore_names,
                ignore_comments
            )


        except Exception as e:

            print(
                "[{}] ERROR: {}".format(
                    section,
                    e
                )
            )

            exit_code = 1



    return exit_code



if __name__ == "__main__":

    sys.exit(
        main()
    )
