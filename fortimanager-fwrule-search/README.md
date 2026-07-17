# FortiManager Policy Search rendszer – működési összefoglaló

## Cél

A rendszer célja, hogy egy vagy több IP/host alapján megkeresse:

* mely FortiManager address objektum érintett,
* mely address group-ok tartalmazzák,
* mely policy package-ekben,
* mely policy-k használják,
* a policy teljes tartalmát riport formában előállítsa.

A működés hasonló a FortiManager GUI **Where Used** funkciójához, de automatizálható és Excelben tovább feldolgozható formában.

---

Tesztelve Fortimanager 7.4.x verzióval.
Python scriptkek szándékosan nem használnak külső telepítendő modulokat.

---

# 1. Konfiguráció

Minden FortiManager kapcsolat adata egy közös fájlban van:

## config.json

Példa:

```json
{
    "fortimanager": "https://FORTIMANAGER/jsonrpc",
    "token": "API_TOKEN",
    "adom": "ADOM_NEV",
    "local_domains": [
        ".valami.hu",
        ".intranet.local"
    ]

}
```

A scriptek innen olvassák:

* FortiManager URL
* API token
* ADOM név

Nincs többé beégetett jelszó/token a Python fájlokban.

---

# 2. Adatgyűjtés FortiManagerből

## Address objektumok lekérése

Script:

```
get_addresses.py
```

API:

```
/pm/config/adom/{ADOM}/obj/firewall/address
```

Kimenet:

```
firewall_addresses.json
```

Tartalmazza:

* IP objektumok
* subnet objektumok
* IP range objektumok
* FQDN objektumok

Példa:

```json
{
  "name": "WEB01",
  "type": "fqdn",
  "fqdn": "web01.example.com"
}
```

---

## Address group lekérés

Script:

```
get_addrgrp.py
```

Kimenet:

```
firewall_addrgrp.json
```

Tartalmazza:

* csoportokat
* csoport tagokat
* beágyazott groupokat

Példa:

```
WEB_SERVERS
 |
 +-- WEB01
 +-- WEB02
```

---

## Policy package lista

Script:

```
get_policy_packages.py
```

Kimenet:

```
policy_packages.json
```

Megmutatja az összes policy package-et.

Példa:

```
ALMA
KORTE
DMZ
```

---

## Policy lekérés

Script:

```
get_policies.py
```

Kimenet:

```
all_policies.json
```

Tartalmazza:

* package neve
* policy ID
* policy név
* source
* destination
* service
* action
* status

Fontos:

A policy azonosító nem globális.

A helyes kulcs:

```
(package, policy_id)
```

Példa:

```
ALMA 1590
KORTE  1590
```

két külön policy.

---

## Service objektumok lekérése

Script:

```
get_firewall_services.py
```

Kimenet:

```
firewall_services.json
```

Tartalmazza:

* service neve
* TCP portok
* UDP portok

Példa:

```
HTTPS

TCP/443
```

---

# 3. FQDN kezelés

A rendszer elvégezi a DNS lekérést.

A FortiManager FQDN objektumokat használjuk erre.

A folyamat:

```
firewall_addresses.json
        |
        |
        v
resolve_fqdn.py
        |
        |
        v
fqdn_resolved.json
```

A keresés ebből dolgozik.

Előnye:

* nincs dupla DNS lekérés
* ugyanazt az állapotot látjuk, mint FortiManagerben

---

# 4. Host keresés

A bementi fileba kell beírni a keresendő objektumokat.

Bemeneti fájl:

```
search_hosts.txt
```

Tartalmazhat:

* host nevet
* részleges objektum nevet
* IP címet

Példa:

```
web01
database
app
192.168.1.1
```

kimeneti file:
```
search_ips.txt
```

A keresés:

1. Megnézi a FortiManager address objektum neveket
2. Megnézi az FQDN cache-t
3. Meghatározza az IP címeket
4. Ezek alapján indul a policy keresés

---

# 5. IP alapú keresés

A keresési logika szándékosan nem keres subnet tartományban.

Nincs:

```
10.121.0.0/16
```

találat csak azért, mert az IP beleesik.

Ez azért történt, mert a FortiManager GUI Where Used sem mindig listázza ezeket.

A keresés:

* host objektum
* /32
* FQDN feloldott IP
* pontos objektum

alapján működik.

---

# 6. Policy keresés

Script:

```
search_ip_policy.py
```

Feladata:

* megkeresi az IP-hez tartozó objektumokat
* feloldja az address groupokat
* megkeresi a policy-ket

Figyel:

* disabled policy kizárás
* package kezelés
* policy ID duplikáció

Kimenet:

```
policy_search_results.json
```

---

# 7. Riport készítés

Script:

```
show_policy_report.py
```

Bemenetek:

```
policy_search_results.json
all_policies.json
firewall_addresses.json
firewall_addrgrp.json
firewall_services.json
fqdn_resolved.json
```

Kimenet:

```
policy_report.csv
```

Excelben megnyitható.

---

# Riport tartalma

Oszlopok:

| Mező        | Tartalom                       |
| ----------- | ------------------------------ |
| IP          | keresett IP                    |
| Package     | policy package                 |
| Policy ID   | policy azonosító               |
| Policy Name | szabály neve                   |
| Source      | feloldott source objektum      |
| Destination | feloldott destination objektum |
| Service     | porttal együtt                 |
| Action      | allowed / deny                 |
| Status      | enabled / disabled             |

---

# Példa riport

```
IP:
192.168.111.134


Package:
ALMA


Policy ID:
777


Policy Name:
BGP


Source:
BGP_NET (192.168.111.0/24)


Destination:
BGP_REMOTE (192.168.222.10)


Service:
BGP (TCP/179)


Action:
allowed


Status:
enabled
```

---

# Futási sorrend

Teljes adatfrissítés:

```bash
python3 get_addresses.py

python3 get_addrgrp.py

python3 get_policy_packages.py

python3 get_policies.py

python3 get_firewall_services.py
```

FQDN frissítés:

```bash
python3 search_fqdn_cache.py
```

Keresés:

```bash
python3 search_hosts.py
```

Policy keresés:

```bash
python3 search_ip_policy.py
```

Riport:

```bash
python3 show_policy_report.py
```

---

# Fontos működési elvek

## Policy azonosítás

Mindig:

```
Package + Policy ID
```

Nem csak:

```
Policy ID
```

---

## FQDN kezelés

Nem DNS lekérésből dolgozik.

Forrás:

```
fqdn_resolved.json
```

---

## Address group

Támogatott:

* group
* nested group
* FQDN tag
* IP tag

---

## Export

A végső CSV:

```
policy_report.csv
```

Excelben:

* szűrhető
* rendezhető
* tovább feldolgozható

---

# Könyvtár struktúra ajánlott

```
fortimanager-search/

├── config.json

├── get_addresses.py
├── get_addrgrp.py
├── get_policies.py
├── get_policy_packages.py
├── get_firewall_services.py

├── search_hosts.py
├── search_ip_policy.py
├── show_policy_report.py

├── firewall_addresses.json
├── firewall_addrgrp.json
├── firewall_services.json
├── all_policies.json
├── policy_packages.json
├── fqdn_resolved.json

├── search_hosts.txt

└── policy_report.csv
```

```
```

Ezzel a dokumentációval később újra felépíthető a teljes folyamat anélkül, hogy a Python fájlok részleteit végig kellene nézni.


Scriptek futtatási sorrendje:

python3 get_addresses.py
python3 get_addrgrp.py
python3 get_policy_packages.py
python3 get_policies.py
python3 get_firewall_services.py
python3 resolve_fqdn.py
python3 search_hosts.py
python3 search_ip_policy.py
python3 show_policy_report.py

run_policy_search.sh file tartalmazza ezt az indítási sorrendet.

indítása:
./run_policy_search.sh
