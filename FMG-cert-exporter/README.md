# FortiManager / FortiGate Certificate Exporter

`fmg_cert_all.py` is a Python-based certificate exporter for FortiManager and FortiGate managed devices.

The script connects to FortiManager using the JSON-RPC API and exports:

* FortiManager own certificates
* FortiGate managed device certificates
* Global certificates
* VDOM certificates

The exported certificates are stored as PEM files and can be used for:

* certificate monitoring
* expiration checks
* compliance validation
* certificate inventory
* backup purposes

---

## Features

### FortiManager certificates

Exports certificates directly from FortiManager:

* Local certificates
* CA certificates
* Remote CA certificates

Supported API paths:

```
/cli/global/system/certificate/local
/cli/global/system/certificate/ca
/cli/global/system/certificate/remote
```

---

### FortiGate managed devices

Uses FortiManager JSON proxy functionality to query managed FortiGate devices.

Supported certificate types:

* Local certificates
* Remote CA certificates

Supported locations:

* Global scope
* VDOM scope

---

## Supported environment

Tested with:

* FortiManager 7.4.x
* FortiGate 7.4.x
* Python 3.x

---

# Installation

Clone repository:

```bash
git clone https://github.com/example/fmg-cert-exporter.git
cd fmg-cert-exporter
```

Install script:

```bash
install -m 750 fmg_cert_all.py /usr/local/bin/fmg_cert_all.py
```

Create configuration:

```bash
touch /etc/fmg.conf
chmod 600 /etc/fmg.conf
```

---

# Configuration

Example:

```ini
[global]

output_dir=/var/lib/monitoring/fmg-certs

ignore_name=Fortinet_CA_SSL,Fortinet_Factory
ignore_comment=test,ignore


[FMG_PROD]

host=10.10.10.10
token=YOUR_API_TOKEN
adom=Production
```

Multiple FortiManager environments and ADOMs can be configured.

Example:

```ini
[FMG_PROD]

host=10.10.10.10
token=TOKEN1
adom=Production


[FMG_TEST]

host=10.20.20.10
token=TOKEN2
adom=Test
```

---

# Configuration parameters

## Global section

| Parameter      | Description                    |
| -------------- | ------------------------------ |
| output_dir     | Certificate export directory   |
| ignore_name    | Certificate names to ignore    |
| ignore_comment | Certificate comments to ignore |

---

## FortiManager section

| Parameter | Description                 |
| --------- | --------------------------- |
| host      | FortiManager hostname or IP |
| token     | API token                   |
| adom      | ADOM to process             |

---

# Output format

Certificates are stored using:

```
FMG__DEVICE__SCOPE__TYPE__CERTIFICATE.pem
```

The separator is `__` to avoid conflicts with certificate names.

---

## FortiManager certificate examples

```
FMG_PROD__FMG__global__local-cer__fmg_gui.pem

FMG_PROD__FMG__global__ca__Company-Root-CA.pem

FMG_PROD__FMG__global__remote-ca__Remote-CA.pem
```

---

## FortiGate certificate examples

Global certificate:

```
FMG_PROD__FGT-HQ__global__local-cer__vpn-cert.pem
```

VDOM certificate:

```
FMG_PROD__FGT-HQ__SEC__local-cer__vpn-cert.pem
```

---

# Certificate filtering

## FortiManager

FortiManager certificates are filtered by:

* certificate name
* certificate comment

The script does not filter by `source` because FortiManager certificate objects do not always expose the same attributes as FortiGate certificates.

---

## FortiGate

Only user certificates are exported:

```
source=user
```

Factory certificates are ignored.

For VDOM queries the script checks:

Global:

```
range=global
```

VDOM:

```
range=vdom
```

This prevents duplicated export of inherited global certificates.

---

# Execution

Manual run:

```bash
python3 fmg_cert_all.py --config /etc/fmg.conf
```

Example:

```
[FMG_PROD] Processing FortiManager certificates

[FMG_PROD] Exported FMG_PROD__FMG__global__ca__Company-Root.pem

[FGT-HQ] Processing

[FGT-HQ] Exported FMG_PROD__FGT-HQ__SEC__local-cer__vpn.pem


========== SUMMARY ==========

ADOM processed : 1
Devices found  : 5
Devices OK     : 5
Certificates   : 82
Errors         : 0

=============================

Exit code: 0
```

---

# Exit codes

| Code | Description                 |
| ---- | --------------------------- |
| 0    | Successful execution        |
| 1    | One or more errors occurred |
| 2    | Configuration file error    |

---

# Cron example

Run every hour:

```cron
0 * * * * /usr/bin/python3 /usr/local/bin/fmg_cert_all.py --config /etc/fmg.conf >> /var/log/fmg_cert_all.log 2>&1
```

---

# Cleanup behavior

The script removes PEM files that no longer exist in the source system.

Cleanup is separated:

FortiManager:

```
FMG_NAME__FMG__*
```

FortiGate:

```
FMG_NAME__FORTIGATE_NAME__*
```

This prevents accidental deletion between certificate sources.

---

# Security considerations

## Configuration protection

The configuration file contains API tokens.

Recommended permissions:

```bash
chmod 600 /etc/fmg.conf
```

---

## TLS verification

The script disables TLS certificate verification for API communication.

This is intended for internal management networks where FortiManager certificates may be:

* self-signed
* privately issued
* not trusted by the operating system

---

## API token permissions

Create API tokens with the minimum required permissions.

The token must allow:

FortiManager:

```
/cli/global/system/certificate/*
```

FortiManager proxy:

```
/sys/proxy/json
```

FortiGate certificate access:

```
/api/v2/cmdb/vpn.certificate/*
/api/v2/monitor/system/certificate/download
```

---

# API usage

The script uses:

## FortiManager JSON-RPC API

```
/jsonrpc
```

## FortiManager certificate API

```
/cli/global/system/certificate/local
/cli/global/system/certificate/ca
/cli/global/system/certificate/remote
```

## FortiManager proxy API

```
/sys/proxy/json
```

## FortiGate REST API

```
/api/v2/cmdb/system/vdom

/api/v2/cmdb/vpn.certificate/local

/api/v2/cmdb/vpn.certificate/ca

/api/v2/monitor/system/certificate/download
```

---

# License

This project is released under the MIT License.

See the `LICENSE` file for details.

---

# Disclaimer

This project is not an official Fortinet product.

Use it at your own risk.

Always test in a non-production environment before deployment.

---

# Author

Gyorgy Virag
vgyuri75@gmail.com

