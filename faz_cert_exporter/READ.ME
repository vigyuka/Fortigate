# FortiAnalyzer Certificate Exporter

A simple Python utility for exporting **local** and **CA certificates** from one or more FortiAnalyzer appliances via the JSON-RPC API.

The script stores certificates as individual PEM files and automatically removes certificates that no longer exist on the FortiAnalyzer.

## Features

- Export local certificates
- Export CA certificates
- Support multiple FortiAnalyzer devices
- Atomic file writes (prevents partially written files)
- Automatic cleanup of obsolete certificate files
- Ignore certificates by name or comment
- No external Python dependencies (Python standard library only)

## Requirements

- Python 3.6+
- API token with permission to read certificates
- Network connectivity to the FortiAnalyzer management interface

## Configuration

The script reads its configuration from an INI file.

Default location:

```
/etc/faz.conf
```

Example configuration:

```ini
[global]
output_dir = /var/lib/monitoring/faz-certs

# Optional
ignore_name = Fortinet_CA_SSL,ExampleCert
ignore_comment = IgnoreMe,Temporary

[FAZ_DC1]
host = faz1.example.com
token = YOUR_API_TOKEN

[FAZ_DC2]
host = faz2.example.com
token = YOUR_API_TOKEN
```

## Usage

Run with the default configuration:

```bash
python3 faz_cert_all.py
```

Use a custom configuration file:

```bash
python3 faz_cert_all.py --config /path/to/faz.conf
```

## Output

Certificates are exported as PEM files.

Example:

```
/var/lib/monitoring/faz-certs/

FAZ_DC1_local_WebServer.pem
FAZ_DC1_local_SSL-VPN.pem
FAZ_DC1_ca_RootCA.pem
FAZ_DC1_ca_InternalCA.pem

FAZ_DC2_local_WebServer.pem
FAZ_DC2_ca_RootCA.pem
```

Filename format:

```
<FAZ_NAME>_<TYPE>_<CERTIFICATE_NAME>.pem
```

Where:

- `TYPE` is either `local` or `ca`
- invalid filename characters are automatically replaced with `_`

## Automatic Cleanup

After every successful export, the script compares the exported certificates with the existing files in the output directory.

Files matching:

```
<FAZ_NAME>_*.pem
```

that were **not exported during the current run** are automatically removed.

This keeps the directory synchronized with the FortiAnalyzer.

## Ignoring Certificates

Certificates can be skipped by:

- certificate name
- certificate comment

Example:

```ini
[global]
ignore_name = Fortinet_CA_SSL,ExampleCert
ignore_comment = Temporary,DoNotExport
```

## Security Notes

- Authentication uses a FortiAnalyzer API token.
- The script currently disables SSL certificate verification:

```python
ssl._create_unverified_context()
```

This simplifies deployment in environments using self-signed certificates, but it is **not recommended for production**. Enabling proper certificate validation is recommended whenever possible.

Exported PEM files are written with file permissions:

```
0600
```

## Exit Codes

| Exit Code | Meaning |
|----------:|---------|
| 0 | Success |
| 1 | One or more FortiAnalyzer instances failed |
| 2 | Configuration file could not be read |

## Example Output

```
[FAZ_DC1] Connecting faz1.example.com
[FAZ_DC1] Exported /var/lib/monitoring/faz-certs/FAZ_DC1_local_WebServer.pem
[FAZ_DC1] Exported /var/lib/monitoring/faz-certs/FAZ_DC1_ca_RootCA.pem
[FAZ_DC1] Completed, exported: 2

[FAZ_DC2] Connecting faz2.example.com
[FAZ_DC2] Exported /var/lib/monitoring/faz-certs/FAZ_DC2_local_SSLVPN.pem
[FAZ_DC2] Removed old /var/lib/monitoring/faz-certs/FAZ_DC2_local_OldCert.pem
[FAZ_DC2] Completed, exported: 3
```

## License

This project is released under the MIT License.
