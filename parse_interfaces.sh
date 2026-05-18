#!/bin/bash

INPUT="backup.conf"
OUTPUT="implementation_doc.md"

> "$OUTPUT"

echo "# FortiGate Implementation Documentation" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "## Interfaces" >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "| edit | vdom | type | ip | allowaccess | vlanid | status |" >> "$OUTPUT"
echo "|---|---|---|---|---|---|---|" >> "$OUTPUT"

awk '
BEGIN {
    inside=0
    name=""
}

/^config system interface$/ {
    inside=1
    next
}

inside && /^end$/ {
    inside=0
}

inside {

    if ($1=="edit") {

        if (name!="") {

            printf("| %s | %s | %s | %s | %s | %s | %s |\n",
                name,
                (vdom != "" ? vdom : "NA"),
                (type != "" ? type : "NA"),
                (ip != "" ? ip : "NA"),
                (allowaccess != "" ? allowaccess : "NA"),
                (vlanid != "" ? vlanid : "NA"),
                (status != "" ? status : "NA"))
        }

        gsub(/"/,"",$2)

        name=$2

        vdom=""
        type=""
        ip=""
        allowaccess=""
        vlanid=""
        status=""
    }

    if ($1=="set") {

        key=$2

        value=""

        for(i=3;i<=NF;i++) {
            value=value $i " "
        }

        sub(/[ \t]+$/,"",value)

        if(key=="vdom") vdom=value
        if(key=="type") type=value
        if(key=="ip") ip=value
        if(key=="allowaccess") allowaccess=value
        if(key=="vlanid") vlanid=value
        if(key=="status") status=value
    }
}

END {

    if (name!="") {

        printf("| %s | %s | %s | %s | %s | %s | %s |\n",
            name,
            (vdom != "" ? vdom : "NA"),
            (type != "" ? type : "NA"),
            (ip != "" ? ip : "NA"),
            (allowaccess != "" ? allowaccess : "NA"),
            (vlanid != "" ? vlanid : "NA"),
            (status != "" ? status : "NA"))
    }
}
' "$INPUT" >> "$OUTPUT"

echo ""
echo "Kész: $OUTPUT"
