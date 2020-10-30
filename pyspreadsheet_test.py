'''
This is an example on how to use 'pyspreadsheet'.

Below are doctests. It is worth to study them as they show benefits of this library.
'''

from pathlib import Path
from pyspreadsheet import ExcelReader

# Read a excel sheet
DIRECTORY_OF_THIS_FILE = Path(__file__).parent
excel = ExcelReader(DIRECTORY_OF_THIS_FILE / 'pyspreadsheet_test.xlsx')

from enum import Enum
class EquipmentType(Enum):
    Voltmeter = 1
    Multimeter = 2

print('\nAccess using indices:')
equipment = excel['Equipment']
for row in equipment.rows:
    instrument = row['Instrument']
    model = row['Model'] 
    print(f'  {instrument}: {model}')


print('\nAccess using properties:')
for row in excel.table_Equipment.rows:
    print(f'  {row.col_Instrument}: {row.col_Model}')

# Dump the whole file for source code revision control
FILENAME_DUMP = 'pyspreadsheet_dump.txt'
print(f'\nWrite: {FILENAME_DUMP}')
with (DIRECTORY_OF_THIS_FILE / FILENAME_DUMP).open('w') as f:
    excel.dump(f)

def doctest_reference():
    '''
    >>> excel.reference
    'File "pyspreadsheet_test.xlsx"'

    >>> excel.table_Equipment.reference
    'Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"'

    >>> excel.table_Equipment.rows[0].reference
    'Row 3 in Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"'

    >>> excel.table_Equipment.rows[0].col_ID.reference
    'Cell "C3" in Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"'
    '''

def doctest_excelreader():
    '''
    >>> ExcelReader('invalid_filename.xlsx')
    Traceback (most recent call last):
       ...
    FileNotFoundError: [Errno 2] No such file or directory: 'invalid_filename.xlsx'

    >>> excel.invalid
    Traceback (most recent call last):
       ...
    AttributeError: "ExcelReader" object has no attribute "invalid"

    >>> excel.table_Invalid
    Traceback (most recent call last):
       ...
    AttributeError: No table "table_Invalid". Valid tables are "Equipment|Measurement|TableA|TableC". See: File "pyspreadsheet_test.xlsx"

    >>> excel['Invalid']
    Traceback (most recent call last):
       ...
    KeyError: 'No table "Invalid". Valid tables are "Equipment|Measurement|TableA|TableC". See: File "pyspreadsheet_test.xlsx"'
    '''

def doctest_row():
    '''
    >>> row = excel.table_Equipment.rows[0]

    >>> row.invalid
    Traceback (most recent call last):
       ...
    AttributeError: "Row" object has no attribute "invalid"

    >>> row['Invalid']
    Traceback (most recent call last):
       ...
    KeyError: 'No column "Invalid". Valid columns are ID|Instrument|Model|Serial. See: Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"'

    >>> row.col_Invalid
    Traceback (most recent call last):
       ...
    AttributeError: No column "col_Invalid". Valid columns are ID|Instrument|Model|Serial. See: Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"
    '''

def doctest_cell_int():
    '''
    >>> cell_id = excel.table_Equipment.rows[0].col_ID
    >>> cell_voltmeter = excel.table_Equipment.rows[0].col_Instrument

    >>> cell_id.reference
    'Cell "C3" in Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"'

    >>> cell_id.text
    '1'

    >>> cell_id.int
    1

    >>> cell_id.astype(float)
    1.0

    >>> cell_voltmeter.int
    Traceback (most recent call last):
       ...
    ValueError: "Voltmeter" is not a valid int! See: Cell "D3" in Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"
    '''

def doctest_cell_enumaration():
    '''
    >>> cell_id = excel.table_Equipment.rows[0].col_ID
    >>> cell_voltmeter = excel.table_Equipment.rows[0].col_Instrument

    >>> cell_voltmeter.text
    'Voltmeter'

    >>> cell_voltmeter.asenum(EquipmentType)
    <EquipmentType.Voltmeter: 1>

    >>> cell_id.asenum(EquipmentType)
    Traceback (most recent call last):
       ...
    ValueError: "1" is not a valid EquipmentType! Valid values are Voltmeter|Multimeter. See: Cell "C3" in Table "Equipment" in Worksheet "Inventory" in File "pyspreadsheet_test.xlsx"
    '''

if __name__ == '__main__':
    import doctest
    doctest.testmod()
