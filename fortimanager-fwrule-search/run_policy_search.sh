#!/bin/bash

#
# FortiManager Policy Search teljes futtatás
#

echo "======================================"
echo " FortiManager Policy Search indítása"
echo "======================================"


echo
echo "[1/9] Address objektumok lekérése..."
python3 get_addresses.py

if [ $? -ne 0 ]; then
    echo "HIBA: get_addresses.py sikertelen"
    exit 1
fi



echo
echo "[2/9] Address group-ok lekérése..."
python3 get_addrgrp.py

if [ $? -ne 0 ]; then
    echo "HIBA: get_addrgrp.py sikertelen"
    exit 1
fi



echo
echo "[3/9] Policy package lista lekérése..."
python3 get_policy_packages.py

if [ $? -ne 0 ]; then
    echo "HIBA: get_policy_packages.py sikertelen"
    exit 1
fi



echo
echo "[4/9] Policy-k lekérése..."
python3 get_policies.py

if [ $? -ne 0 ]; then
    echo "HIBA: get_policies.py sikertelen"
    exit 1
fi



echo
echo "[5/9] Firewall service-ek lekérése..."
python3 get_firewall_services.py

if [ $? -ne 0 ]; then
    echo "HIBA: get_firewall_services.py sikertelen"
    exit 1
fi



echo
echo "[6/9] FQDN feloldások frissítése..."
python3 resolve_fqdn.py

if [ $? -ne 0 ]; then
    echo "HIBA: resolve_fqdn.py sikertelen"
    exit 1
fi



echo
echo "[7/9] Host keresés..."
python3 search_hosts.py

if [ $? -ne 0 ]; then
    echo "HIBA: search_hosts.py sikertelen"
    exit 1
fi



echo
echo "[8/9] Policy keresés..."
python3 search_ip_policy.py

if [ $? -ne 0 ]; then
    echo "HIBA: search_ip_policy.py sikertelen"
    exit 1
fi



echo
echo "[9/9] Policy riport készítés..."
python3 show_policy_report.py

if [ $? -ne 0 ]; then
    echo "HIBA: show_policy_report.py sikertelen"
    exit 1
fi



echo
echo "======================================"
echo " Policy Search sikeresen elkészült"
echo " Eredmény: policy_report.csv"
echo "======================================"
