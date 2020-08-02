# pss-fleet-data
A module collecting data on the top 100 fleets and their members.
Collects data on top 100 / tournament fleets and their members hourly and stores them on a [public gdrive folder](https://drive.google.com/drive/folders/10wOZgAQk_0St2Y_jC3UW497LVpBNxWmP).

Since October 2019, the fleet data consists of individual json files for each run, representing a dictionary that consists of 4 objects:

- **meta data** (access by key "**meta**")
- **fleets** (access by key "**fleets**")
- **users** (access by key "**users**")
- **data** (access by key "**data**")

## **meta data** object
### Type
dictionary
### Keys
| key | data type | explanation | introduced with |
| --- | --- | --- | --- |
| timestamp | datetime | The point in time, when the run started. | |
| duration | float | Duration of the collection run in seconds. | |
| fleet_count | int | Number of fleets documented in this run. | |
| user_count | int | Number of users documented in this run. | |
| tourney_running | bool | Indicates, whether tournament finals were running, when this run started. | |
| schema_version | int | The schema version used in this file | schema version 4 (October 2020)

## **fleets** object
### Type
list of tuples
### Contents
Tuples with 5 values (all of type string)
| index | fleet property key | explanation | introduced with |
| --- | --- | --- | --- |
| 0 | AllianceId | fleet id |  |
| 1 | AllianceName | fleet name |  |
| 2 | Score | star count |  |
| 3 | DivisionDesignId | division | schema version 3 (November 2019) |
| 4 | Trophy | trophy count | schema version 4 (August 2020) |

## **users** object
### Type
list of tuples
### Contents
Tuples with 2 values (all of type string)
| index | fleet property key | explanation | introduced with |
| --- | --- | --- | --- |
| 0 | Id | user id |  |
| 1 | Name | user name |  |

## **data** object
### Type
list of tuples
### Contents
Tuples with 16 values (all of type string)
| index | fleet property key | explanation | introduced with |
| --- | --- | --- | --- |
| 0 | Id | user id |  |
| 1 | AllianceId | fleet id |  |
| 2 | Trophy | user's trophy count |  |
| 3 | AllianceScore | user's star count |  |
| 4 | AllianceMembership | user's rank in the fleet |  |
| 5 | AllianceJoinDate | timestamp of user joining the fleet |  |
| 6 | LastLoginDate | timestamp of user's last login |  |
| 7 | LastHeartBeatDate | timestamp of the user's last heartbeat sent to Savy servers | schema version 4 (August 2020) |
| 8 | CrewDonated | number of crews donated to the fleet by the user | schema version 4 (August 2020) |
| 9 | CrewReceived | number of crew borrowd from the fleet by the user | schema version 4 (August 2020) |
| 10 | PVPAttackWins | PvP attack wins | schema version 4 (August 2020) |
| 11 | PVPAttackLosses | PvP attack losses | schema version 4 (August 2020) |
| 12 | PVPAttackDraws | PvP attack draws | schema version 4 (August 2020) |
| 13 | PVPDefenceWins | PvP defense wins | schema version 4 (August 2020) |
| 14 | PVPDefenceLosses | PvP defense losses | schema version 4 (August 2020) |
| 15 | PVPDefenceDraws | PvP defense draws | schema version 4 (August 2020) |

# NOTES
All timestamps / datetime strings are in ISO format as used by Savy (`%Y-%m-%dT%H:%M:%S` in python). This also means that they're all in UTC.
All tuples are represented as lists, since json doesn't know tuples.