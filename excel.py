import openpyxl

import utility as util


def create_xl_from_data(data: dict, save_to: str) -> None:
    print(f'Creating workbook at: {save_to}')
    wb = openpyxl.Workbook(write_only=True)
    for data_type in data.keys():
        util.vrbs(f'Creating worksheet \'{data_type}\' with columns: {", ".join(data[data_type][0])}')
        ws = wb.create_sheet(title=data_type)

        util.vrbs(f'Appending data to worksheet \'{data_type}\'.')
        for item in data[data_type]:
            ws.append(item)

        util.vrbs(f'Finished worksheet \'{data_type}\'.')
    print(f'Saving workbook at: {save_to}')
    wb.save(save_to)
    print(f'Saved workbook.')
    print('Exiting.')
