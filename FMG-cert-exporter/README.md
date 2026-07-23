# FortiManager Certificate Exporter

`fmg_cert_all.py` is a Python-based certificate exporter for FortiManager managed FortiGate devices.

The script connects to FortiManager using the JSON-RPC API and uses the FortiManager JSON proxy functionality to retrieve and export certificates from managed FortiGate devices.

The main purpose is to create a local PEM certificate repository that can be used for monitoring, certificate expiration checks, compliance checks, or backup purposes.

## Features

* Supports multiple FortiManager ADOMs
* Supports ADOMs without managed devices
* Exports certificates from managed FortiGate devices
* Supports:

  * Global certificates
  * VDOM certificates
  * Local certificates
  * Remote CA certificates
* Uses FortiManager `/sys/proxy/json` API functionality
* Filters certificates:

  * Only user imported certificates (`source=user`)
  * Avoids duplicated certificates by checking certificate scope (`range`)
* Supports certificate ignore lists
* Atomic PEM file writing
* Removes obsolete exported certificates
* Returns proper exit codes for automation and monitoring systems

## Requirements

* Python 3.x
* FortiManager API access
* FortiGate devices managed by FortiManager
* API token with sufficient permissions

Tested environment:

* FortiManager 7.4.x
* FortiGate 7.4.x

## Installation

Clone the repository:

```bash
git clone https://github.com/vigyuka/Fortigate/FMG-cert-exporter/fmg-cert-exporter.git
cd fmg-cert-exporter
```

Copy the script:

```bash
install -m 750 fmg_cert_all.py /usr/local/bin/fmg_cert_all.py
```

Create the configuration file:

```bash
touch /etc/fmg.conf
chmod 600 /etc/fmg.conf
```

## Configuration

Example `/etc/fmg.conf`:

```ini
[global]
output_dir=/var/lib/monitoring/fmg-certs

ignore_name=Fortinet_CA_SSL,Fortinet_Factory
ignore_comment=test,ignore


[FMG_PROD]
host=10.10.10.10
token=YOUR_API_TOKEN
adom=Production


[FMG_TEST]
host=fmg.example.local
token=YOUR_API_TOKEN
adom=Test
```

## Configuration parameters

### Global section

| Parameter        | Description                                     |
| ---------------- | ----------------------------------------------- |
| `output_dir`     | Directory where PEM files are stored            |
| `ignore_name`    | Comma separated certificate names to exclude    |
| `ignore_comment` | Comma separated certificate comments to exclude |

### FortiManager section

| Parameter | Description                         |
| --------- | ----------------------------------- |
| `host`    | FortiManager hostname or IP address |
| `token`   | FortiManager API token              |
| `adom`    | ADOM name to process                |

Multiple ADOMs can be configured.

ADOMs without managed devices are skipped automatically.

## Output files

Certificates are stored using the following naming format:

```
FMG_NAME__FORTIGATE_NAME__SCOPE__TYPE__CERTIFICATE_NAME.pem
```

Examples:

```
FMG_PROD__FGT-HQ__global__local-cer__GUI-Fortigate.pem

FMG_PROD__FGT-HQ__SEC__local-cer__vpn-cert.pem

FMG_PROD__FGT-HQ__SEC__remote-ca__Company-Root-CA.pem
```

The file separator is `__` to avoid conflicts with certificate names.

## Certificate filtering

The script exports only certificates matching:

### Global certificates

```
source=user
range=global
```

### VDOM certificates

```
source=user
range=vdom
```

This prevents exporting inherited global certificates multiple times when querying VDOM certificate lists.

## Running manually

Test run:

```bash
python3 fmg_cert_all.py --config /etc/fmg.conf
```

Example output:

```
[FMG_PROD] Processing ADOM Production
[FGT-HQ] Processing
[FGT-HQ] Exported FMG_PROD__FGT-HQ__global__local-cer__certificate.pem

========== SUMMARY ==========
ADOM processed : 1
Devices found  : 2
Devices OK     : 2
Certificates   : 18
Errors         : 0
=============================

Exit code: 0
```

## Exit codes

| Code | Meaning                                |
| ---- | -------------------------------------- |
| `0`  | Successful execution                   |
| `1`  | One or more errors occurred            |
| `2`  | Configuration file could not be loaded |

## Cron example

Run the exporter every hour:

```cron
0 * * * * /usr/bin/python3 /usr/local/bin/fmg_cert_all.py --config /etc/fmg.conf >> /var/log/fmg_cert_all.log 2>&1
```

## Security considerations

* Protect the configuration file:

```bash
chmod 600 /etc/fmg.conf
```

* The script disables TLS certificate validation for API communication.
  This is intended for internal management networks where FortiManager certificates may be self-signed.

* API tokens should be created with the minimum required permissions.

## API usage

The script uses:

FortiManager JSON-RPC API:

```
/jsonrpc
```

FortiManager proxy API:

```
/sys/proxy/json
```

FortiGate REST API endpoints:

```
/api/v2/cmdb/system/vdom

/api/v2/cmdb/vpn.certificate/local

/api/v2/cmdb/vpn.certificate/ca

/api/v2/monitor/system/certificate/download
```

## License

This project is released under the MIT License.

See the `LICENSE` file for details.

## Author

Gyorgy Virag
vgyuri75@gmail.com

## Disclaimer

This script is not an official Fortinet product.

Use it at your own risk and test in a non-production environment before deployment.
