# RFID Management

The OpenEVSE integration provides complete RFID tag and user management, allowing you to restrict charging access to authorized physical badges, and associate each tag with a Home Assistant `person` entity or friendly name.

---

## Firmware Requirements Matrix

| Feature | Minimum Firmware |
| :--- | :--- |
| Enable/Disable RFID Access Switch | **4.1.4+** |
| Learn (Pair) New RFID Tag | **4.0.0+** |
| Assign Users / Persons to RFID Tags | **5.0.0+** |
| Delete RFID Tag Mappings | **5.0.0+** |
| Retrieve Registered RFID Tag Mappings | **5.0.0+** |

---

## Step 1: Enable RFID Access

Before RFID authorization is enforced by the charger hardware:

1. Locate the **RFID Access** switch under **Settings ➔ Devices & Services ➔ OpenEVSE ➔ (Device)**.
2. Toggle the switch **ON**.

You can also automate this with Home Assistant:

```yaml
action: switch.turn_on
target:
  entity_id: switch.openevse_rfid_access
```

---

## Step 2: Learn (Pair) a New RFID Tag

Put the charger into enrollment mode using the **Learn RFID Tag** button entity or service:

### Via UI Button
Press the **Learn RFID Tag** button entity (`button.openevse_learn_rfid_tag`). The charger enters enrollment mode.

### Via Action / Service Call
```yaml
action: openevse.add_rfid_tag
target:
  entity_id: sensor.openevse_charging_status
```

::: tip Scanning Window
Hold your RFID badge or fob near the charger's reader within the 15-second enrollment window to register it.
:::

---

## Step 3: Associate Tag with a Person or Name *(v5.0.0+)*

Once a tag is enrolled, map the physical tag ID to a Home Assistant `person` or a friendly name string.

### Associate with a Home Assistant Person
```yaml
action: openevse.set_rfid_user
target:
  entity_id: sensor.openevse_charging_status
data:
  rfid: "01020304"
  person: person.jane_doe
```

### Associate with a Friendly Name Only
```yaml
action: openevse.set_rfid_user
target:
  entity_id: sensor.openevse_charging_status
data:
  rfid: "01020304"
  name: "Jane Doe"
```

---

## Listing & Deleting RFID Tags *(v5.0.0+)*

### View All Registered Tags
Query the charger's internal user database:

```yaml
action: openevse.get_rfid_users
target:
  entity_id: sensor.openevse_charging_status
response_variable: rfid_users
```

### Remove an RFID Tag
```yaml
action: openevse.delete_rfid_user
target:
  entity_id: sensor.openevse_charging_status
data:
  rfid: "01020304"
```

---

## Automated Onboarding Script Example

Combine learning and assignment into a single Home Assistant script:

```yaml
script:
  onboard_new_rfid_card:
    alias: "Enroll New RFID Card"
    sequence:
      - action: openevse.add_rfid_tag
        target:
          entity_id: sensor.openevse_charging_status
      - delay: "00:00:15"
      - action: openevse.set_rfid_user
        target:
          entity_id: sensor.openevse_charging_status
        data:
          rfid: "01020304"
          person: person.alex_smith
```
