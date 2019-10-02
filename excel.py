import openpyxl

import settings
import utility





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
