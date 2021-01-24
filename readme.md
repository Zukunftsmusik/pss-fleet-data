# pss-fleet-data
A module collecting data on the top 100 fleets and their members.
Collects data on top 100 / tournament fleets and their members hourly and stores them on a [public gdrive folder](https://drive.google.com/drive/folders/10wOZgAQk_0St2Y_jC3UW497LVpBNxWmP).

# Schema descriptions

Since October 2019, the fleet data consists of individual json files for each run, representing a dictionary containing multiple objects.

## Schema version 6

This schema is in use since January 2021. It adds the `ChampionshipScore` to the fleets and users data.

### **meta data** object
_Unchanged_

### **fleets** object
#### Type
list of tuples
#### Contents
Tuples with 5 values (all of type string)
| index | fleet property key | data type | explanation |
| --- | --- | --- | --- |
| 0 | AllianceId | int | Fleet ID |
| 1 | AllianceName | str | Fleet name |
| 2 | Score | int | Fleet's star count |
| 3 | DivisionDesignId | int | Division design ID |
| 4 | Trophy | int | Fleet's trophy count |
| 5 | ChampionshipScore | int | Tournament score determining the yearly rankings |

### **users** object
#### Type
list of tuples
#### Contents
Tuples with 16 values (all of type string)
| index | fleet property key | explanation | introduced with |
| --- | --- | --- | --- |
| 0 | Id | int | User ID |  |
| 1 | Name | str | User name |
| 2 | AllianceId | int | User's fleet ID |  |
| 3 | Trophy | int | User's trophy count |  |
| 4 | AllianceScore | int | User's star count |  |
| 5 | AllianceMembership | int | User's rank in the fleet\* |  |
| 6 | AllianceJoinDate | timestamp | Timestamp of user joining the fleet |  |
| 7 | LastLoginDate | timestamp | Timestamp of user's last login |  |
| 8 | LastHeartBeatDate | timestamp | Timestamp of the user's last heartbeat sent to Savy servers |
| 9 | CrewDonated | int | Number of crews donated to the fleet by the user |
| 10 | CrewReceived | int | Number of crew borrowd from the fleet by the user |
| 11 | PVPAttackWins | int | PvP attack wins |
| 12 | PVPAttackLosses | int | PvP attack losses |
| 13 | PVPAttackDraws | int | PvP attack draws |
| 14 | PVPDefenceWins | int | PvP defense wins |
| 15 | PVPDefenceLosses | int | PvP defense losses |
| 16 | PVPDefenceDraws | int | PvP defense draws |
| 17 | ChampionsipScore | int | Tournament score determining the yearly rankings |

## Schema version 5

This schema version is in use since September 2020. It's been introduced to fix the timestamp bug in schema version 4.

## Schema version 4

This schema version is in use since August 2020. It's been introduced to store more data, while keeping the file size or increasing it only slightly. The json file contains a dictionary containing 3 different objects:

- **meta data** (access by key "**meta**")
- **fleets** (access by key "**fleets**")
- **users** (access by key "**users**")

### NOTES
All timestamps represent the number of full seconds since PSS officially started (2016-01-06 00:00:00 UTC).

All tuples are represented as lists, since json doesn't know tuples.

### **meta data** object
#### Type
dictionary
#### Keys
| key | data type | explanation |
| --- | --- | --- |
| timestamp | timestamp | The point in time, when the run started |
| duration | float | Duration of the collection run in seconds |
| fleet_count | int | Number of fleets documented in this run |
| user_count | int | Number of users documented in this run |
| tourney_running | bool | Indicates, whether tournament finals were running, when this run started |
| schema_version | int | The schema version used in this file |

### **fleets** object
#### Type
list of tuples
#### Contents
Tuples with 5 values (all of type string)
| index | fleet property key | data type | explanation |
| --- | --- | --- | --- |
| 0 | AllianceId | int | Fleet ID |
| 1 | AllianceName | str | Fleet name |
| 2 | Score | int | Fleet's star count |
| 3 | DivisionDesignId | int | Division design ID |
| 4 | Trophy | int | Fleet's trophy count |

### **users** object
#### Type
list of tuples
#### Contents
Tuples with 16 values (all of type string)
| index | fleet property key | explanation | introduced with |
| --- | --- | --- | --- |
| 0 | Id | int | User ID |  |
| 1 | Name | str | User name |
| 2 | AllianceId | int | User's fleet ID |  |
| 3 | Trophy | int | User's trophy count |  |
| 4 | AllianceScore | int | User's star count |  |
| 5 | AllianceMembership | int | User's rank in the fleet\* |  |
| 6 | AllianceJoinDate | timestamp | Timestamp of user joining the fleet |  |
| 7 | LastLoginDate | timestamp | Timestamp of user's last login |  |
| 8 | LastHeartBeatDate | timestamp | Timestamp of the user's last heartbeat sent to Savy servers |
| 9 | CrewDonated | int | Number of crews donated to the fleet by the user |
| 10 | CrewReceived | int | Number of crew borrowd from the fleet by the user |
| 11 | PVPAttackWins | int | PvP attack wins |
| 12 | PVPAttackLosses | int | PvP attack losses |
| 13 | PVPAttackDraws | int | PvP attack draws |
| 14 | PVPDefenceWins | int | PvP defense wins |
| 15 | PVPDefenceLosses | int | PvP defense losses |
| 16 | PVPDefenceDraws | int | PvP defense draws |

**NOTE**

The timestamps `AllianceJoinDate`, `LastLoginDate` & `LastHeartBeatDate` are bugged with this schema. They don't contain the correct values.

\* = The ranks are encoded:
| rank | code |
| --- | --- |
| FleetAdmiral | 0 |
| ViceAdmiral | 1 |
| Commander | 2 |
| Major | 3 |
| Lieutenant | 4 |
| Ensign | 5 |
| Candidate | 6 |

## Schema version 3

This schema version is in use since October 2019.

- **meta data** (access by key "**meta**")
- **fleets** (access by key "**fleets**")
- **users** (access by key "**users**")
- **data** (access by key "**data**")

### NOTES
All timestamps / datetime strings are in ISO format as used by Savy (`%Y-%m-%dT%H:%M:%S` in python). This also means that they're all in UTC.
All tuples are represented as lists, since json doesn't know tuples.

### **meta data** object
#### Type
dictionary
#### Keys
| key | data type | explanation |
| --- | --- | --- |
| timestamp | datetime | The point in time, when the run started. |
| duration | float | Duration of the collection run in seconds. |
| fleet_count | int | Number of fleets documented in this run. |
| user_count | int | Number of users documented in this run. |
| tourney_running | bool | Indicates, whether tournament finals were running, when this run started. |

### **fleets** object
#### Type
list of tuples
#### Contents
Tuples with 5 values (all of type string)
| index | fleet property key | explanation | introduced in |
| --- | --- | --- | --- |
| 0 | AllianceId | Fleet ID |  |
| 1 | AllianceName | Fleet name |  |
| 2 | Score | Fleet's star count |  |
| 3 | DivisionDesignId | Division design ID | November 2019 |

### **users** object
#### Type
list of tuples
#### Contents
Tuples with 2 values (all of type string)
| index | fleet property key | explanation |
| --- | --- | --- |
| 0 | Id | User ID |
| 1 | Name | User name |

### **data** object
#### Type
list of tuples
#### Contents
Tuples with 16 values (all of type string)
| index | fleet property key | explanation |
| --- | --- | --- |
| 0 | Id | User ID |
| 1 | AllianceId | User's fleet ID |
| 2 | Trophy | User's trophy count |
| 3 | AllianceScore | User's star count |
| 4 | AllianceMembership | User's rank in the fleet |
| 5 | AllianceJoinDate | Timestamp of user joining the fleet |
| 6 | LastLoginDate | Timestamp of user's last login |