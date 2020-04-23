
misc dev tools

```yaml
- hosts: localhost
  gather_facts: False
  collections:
  - cidrblock.devpak
  tasks:
  - set_fact:
      current:
        config:
          - afi: ipv4
            acls:
              - name: 110
                aces:
                  - grant: permit
                    sequence: 10
                    source:
                      address: 192.0.1.0
                      wildcard_bits: 0.0.0.255
                    destination:
                      address: 192.0.2.0
                      wildcard_bits: 0.0.0.255
                    dscp: ef
                  - grant: deny
                    sequence: 20
                    source:
                      address: 192.0.1.0
                      wildcard_bits: 0.0.0.255
                    destination:
                      address: 192.0.3.0
                      wildcard_bits: 0.0.0.255
                    dscp: cs0
                  
  - debug:
      msg: "{{ current|cidrblock.devpak.to_dotted }}"

  - pause:

  - update_fact:
      "current.config[0].acls[0].aces[1].dscp": cs1
      "current.config[0].acls[0].aces[1].destination.address": "192.0.4.0"
    register: result
  
  - debug:
      msg: "{{ result }}"

  - set_fact:
      revised: "{{ result['current'] }}"

  - fact_diff:
      before: "{{ current|cidrblock.devpak.to_dotted }}"
      after: "{{ revised|cidrblock.devpak.to_dotted }}"
```