import openpyxl

import settings
import utility


def create_xl_from_data(data: dict, save_to: str) -> None:
    print(f'Creating workbook at: {save_to}')
    wb = openpyxl.Workbook(write_only=True)
    for data_type in data.keys():
        print(f'Creating worksheet \'{data_type}\' with columns: {", ".join(data[0])}')
        ws = wb.create_sheet(title=data_type)
        ws = wb.active

        print(f'Appending data to worksheet \'{data_type}\'.')
        for item in data:
            ws.append(item)

        for column_number, info in enumerate(settings.DATA_OUTPUT_SCHEMA[data_type].values()):
            data_format = info[0]
            if data_format:
                column_letter = openpyxl.utils.get_column_letter(column_number)
                column_range = ws[column_letter]
                column_range.number_format = data_format

        print(f'Finished worksheet \'{data_type}\'. Saving workbook at: {save_to}')
        wb.save(save_to)
        print(f'Saved workbook.')
    print('Exiting.')
