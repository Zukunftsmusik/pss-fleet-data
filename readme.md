**pss-fleet-data** - A module collecting data on the top 100 fleets and their members by _me_: https://github.com/Zukunftsmusik/pss-fleet-data (the repository is currently private, so I'd have to invite you for you to see it)
Collects data on top 100 / tournament fleets and their members hourly and stores them on gdrive (<https://drive.google.com/drive/folders/10wOZgAQk_0St2Y_jC3UW497LVpBNxWmP>).

Since October 2019, the fleet data consists of individual json files for each run, representing a dictionary that consists of 4 objects:

- **meta data** (access by key "**meta**")
- **fleet names** (access by key "**fleets**")
- **user names** (access by key "**users**")
- **data** (access by key "**data**")

**meta data** object
Type: dictionary
Keys:
```AutoHotKey
timestamp: datetime (The point in time, when the run started.)
duration: float (Duration of the collection run in seconds.)
fleet_count: int (Number of fleets documented in this run.)
user_count: int (Number of users documented in this run.)
tourney_running: bool (Indicates, whether tournament finals were running, when this run started.)
schema_version: int (The schema version used in this file)
```
**fleets** object
Type: list of tuples
Contents: Tuples with 5 values (all of type string)
```json
[0] AllianceId
[1] AllianceName
[2] Score (stars as displayed in game)

New with schema version 3 (from November 2019):
[3] DivisionDesignId

New with schema version 4 (from August 2020):
[4] Trophy
```
**users** object
Type: list of tuples
Contents: Tuples with 2 values (all of type string)
```json
[0] Id (user id)
[1] Name (user name)
```
**data** object
Type: list of tuples
Contents: Tuples with 16 values (all of type string)
```json
[0] Id (user id)
[1] AllianceId
[2] Trophy (user's trophy count)
[3] AllianceScore (user's star count)
[4] AllianceMembership (user's rank in the fleet)
[5] AllianceJoinDate (user's join date)
[6] LastLoginDate (user's last login date)

New with schema version 4 (from August 2020):
[7] LastHeartBeatDate
[8] CrewDonated
[9] CrewReceived
[10] PVPAttackWins
[11] PVPAttackLosses
[12] PVPAttackDraws
[13] PVPDefenceWins
[14] PVPDefenceLosses
[15] PVPDefenceDraws
```
**NOTES**
All datetime strings are in ISO format as used by Savy (`%Y-%m-%dT%H:%M:%S` in python). This also means that they're all in UTC.
All tuples are represented as lists, since json doesn't know tuples.