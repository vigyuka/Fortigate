#!/bin/bash

INPUT="backup.conf"
OUTPUT="implementation_doc.md"

SECTIONS=(
    "config system global"
    "config system vdom-link"
    "config system interface"
    "config system ha"
    "config system dns"
    "config system snmp sysinfo"
    "config system snmp user"
    "config system central-management"
    "config system vdom-property"
    "config log syslogd setting"
    "config log fortianalyzer setting"
    "config system cluster-sync"
    "config system fortiguard"
    "config system ntp"
    "config system settings"
    "config router route-map"
    "config router ospf"
    "config router bgp"
    "config vpn ipsec phase1-interface"
    "config vpn ipsec phase2-interface"
    "config vdom"
)

# Markdown file ürítése
> "$OUTPUT"

echo "# FortiGate Configuration Documentation" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Generated: $(date)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

for section in "${SECTIONS[@]}"
do
    echo "## $section" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    echo "| Parameter | Value |" >> "$OUTPUT"
    echo "|---|---|" >> "$OUTPUT"

    awk '
    BEGIN {
        in_edit=0
        current_edit=""
    }

    /^    edit / {
        in_edit=1
        current_edit=$0
        gsub(/^[ \t]+edit /,"",current_edit)
        gsub(/"/,"",current_edit)

        printf("| edit | %s |\n", current_edit)
    }

    /^[ \t]+set / {
        line=$0

        gsub(/^[ \t]+set /,"",line)

        split(line,a," ")

        key=a[1]

        value=""

        for(i=2;i<=length(a);i++) {
            value=value a[i] " "
        }

        gsub(/[ \t]+$/,"",value)

        gsub(/\|/,"\\\\|",value)

        printf("| %s | %s |\n", key, value)
    }

    /^[ \t]+next$/ {
        print "|---|---|"
    }
    ' <(
        awk -v section="$section" '
        BEGIN {
            keep=0
        }

        $0 == section {
            keep=1
        }

        keep {
            print
        }

        keep && /^end$/ {
            keep=0
            exit
        }
        ' "$INPUT"
    ) >> "$OUTPUT"

    echo "" >> "$OUTPUT"
done

echo "Kész: $OUTPUT"
