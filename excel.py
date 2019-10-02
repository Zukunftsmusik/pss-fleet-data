import openpyxl

import settings
import utility





def create_ordered_data(raw_data: dict) -> list:
    """ This function will output 1 list:
         - Tournament data, with the following column format:
           - output timestamp
           - user id
           - user name
           - fleet id
           - fleet name
           - trophy count
           - star count"""
    tournament_data = [(
        settings.COLUMN_NAME_TIMESTAMP,
        settings.COLUMN_NAME_USER_ID,
        settings.COLUMN_NAME_USER_NAME,
        settings.COLUMN_NAME_FLEET_ID,
        settings.COLUMN_NAME_FLEET_NAME,
        settings.COLUMN_NAME_TROPHIES,
        settings.COLUMN_NAME_STARS
    )]
    for timestamp, data in raw_data.items():
        for user_id, tourney_data in data.items():
            user_name = tourney_data['UserName']
            fleet_id = tourney_data['AllianceId']
            fleet_name = tourney_data['AllianceName']
            trophies = tourney_data['Trophies']
            stars = tourney_data['Stars']

            tournament_data.append((timestamp, user_id, user_name, fleet_id, fleet_name, trophies, stars))
    return tournament_data


def create_xl_from_data(data: list, save_to: str, column_formats: list = []) -> None:
    print(f'Creating workbook at: {save_to}')
    wb = openpyxl.Workbook(write_only=True)
    print(f'Creating worksheet \'data\' with columns: {", ".join(data[0])}')
    ws_data = wb.create_sheet(title='data')
    ws_data = wb.active

    print(f'Appending data to worksheet \'data\'.')
    for item in data:
        ws_data.append(item)

    #tab_raw_data = openpyxl.worksheet.table.Table(displayName='tblRawData', tableStyleInfo=TABLE_STYLE)

    print(f'Finished worksheet \'data\'. Saving workbook at: {save_to}')
    wb.save(save_to)
    print(f'Saved workbook. Exiting.')
