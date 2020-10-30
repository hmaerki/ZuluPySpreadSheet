# PySpreadSheet
# https://github.com/hmaerki/PySpreadSheet
# (c) Copyright 2002-2020, Hans Maerki
# Distributed under GNU LESSER GENERAL PUBLIC LICENSE Version 3

# Documentation of openpyxl:
# https://bitbucket.org/openpyxl/openpyxl
# https://openpyxl.readthedocs.io/en/stable/
from pathlib import Path
import openpyxl

TAG_TABLE = 'TABLE'
TAG_HYPHEN = '-'
TAG_EMPTY = ''
COLUMN_TABLE = 0 # TABLE
COLUMN_NAME = 1 # Table name
COLUMN_FIRST_CULUMN = 2

class Cell:
    def __init__(self, row, column, pyxl_cell):
        self._row = row
        self._column = column
        self._pyxl_cell = pyxl_cell

    def __str__(self):
        return self.text

    @property
    def text(self):
        return Cell.get_cell_value(self._pyxl_cell)

    @property
    def int(self):
        return self.astype(int)

    @property
    def float(self):
        return self.astype(float)

    def astype(self, _type):
        t = self.text
        try:
            return _type(t)
        except ValueError:
            raise ValueError(f'"{t}" is not a valid {_type.__name__}! See: {self.reference}')

    def asenum(self, _enum):
        t = self.text
        try:
            return _enum[t]
        except KeyError:
            valid_values = '|'.join([e.name for e in _enum])
            raise ValueError(f'"{t}" is not a valid {_enum.__name__}! Valid values are {valid_values}. See: {self.reference}')

    @property
    def reference(self):
        return f'Cell "{self._pyxl_cell.coordinate}" in {self._row._table.reference}'

    @classmethod
    def get_cell(cls, pyxl_row, columnidx):
        if columnidx >= len(pyxl_row):
            return None
        return pyxl_row[columnidx]

    @classmethod
    def get_cell_value(cls, pyxl_cell):
        if pyxl_cell is None:
            return ''
        value = pyxl_cell.value
        if value is None:
            return ''
        return str(value)

class Row:
    PREFIX = 'col_'

    def __init__(self, table, pyxl_row, rowidx):
        self._table = table
        self._rowidx = rowidx

        self._cells = []
        for column in table.columns:
            cell = Cell.get_cell(pyxl_row, column._columnidx)
            self._cells.append(Cell(self, column, cell))

        for cell in self._cells:
            setattr(self, f'{self.PREFIX}{cell._column.name}', cell)

    @property
    def reference(self):
        return f'Row {self._rowidx+1} in {self._table.reference}'

    def __getitem__(self, column_name):
        assert isinstance(column_name, str)
        column = self._table.get_column(column_name, exceptionclass=KeyError)
        for cell in self._cells:
            if cell._column == column:
                return cell
        assert False, 'Programming error'

    def __getattr__(self, column_name):
        if column_name.startswith(self.PREFIX):
            raise AttributeError(self._table._no_column(column_name))
        raise AttributeError(f'"Row" object has no attribute "{column_name}"')

    def dump(self, file):
        columns = [str(self[c]) for c in self._table.column_names]
        print(f'  {"|".join(columns)}', file=file)

class Column:
    def __init__(self, columnidx, name):
        self._columnidx = columnidx
        self.name = name

class Table:
    def __init__(self, excel, name, worksheet_name, pyxl_row):
        self._excel = excel
        self.name = name
        self.worksheet_name = worksheet_name
        self.rows = []
        self.columns = []

        for columnidx in range(COLUMN_FIRST_CULUMN, len(pyxl_row)):
            pyxl_cell = Cell.get_cell(pyxl_row, columnidx)
            column_name = Cell.get_cell_value(pyxl_cell).strip()
            if column_name == TAG_HYPHEN:
                continue
            if column_name == TAG_EMPTY:
                break
            self.columns.append(Column(columnidx, column_name))

    @property
    def reference(self):
        return f'Table "{self.name}" in Worksheet "{self.worksheet_name}" in {self._excel.reference}'

    @property
    def column_names(self):
        return sorted([c.name for c in self.columns])

    @property
    def column_names_text(self):
        return '|'.join(self.column_names)

    def get_column(self, column_name, exceptionclass=AttributeError):
        for column in self.columns:
            if column.name == column_name:
                return column
        raise exceptionclass(self._no_column(column_name))

    def _no_column(self, column_name):
        return f'No column "{column_name}". Valid columns are {self.column_names_text}. See: {self.reference}'

    def add_row(self, obj_row, rowidx):
        self.rows.append(Row(self, obj_row, rowidx))

    def dump(self, file):
        print(file=file)
        print(f'Table: {self.name}', file=file)
        print(f'  {self.column_names_text}', file=file)
        print(file=file)
        for obj_row in self.rows:
            obj_row.dump(file=file)

class ExcelReader:
    PREFIX = 'table_'

    def __init__(self, str_filename_xlsx):
        self.__filename = str_filename_xlsx
        self.__dict_tables = {}

        pyxl_workbook = openpyxl.load_workbook(filename=str_filename_xlsx, read_only=True, data_only=True)
        for pyxl_worksheet in pyxl_workbook.worksheets:
            self.__read_worksheet(pyxl_worksheet)

    def __read_worksheet(self, pyxl_worksheet):
        def get_value(pyxl_row, idx):
            cell = Cell.get_cell(pyxl_row, idx)
            return Cell.get_cell_value(cell)
        actual_table = None
        for rowidx, pyxl_row in enumerate(pyxl_worksheet.rows):
            if len(pyxl_row) < COLUMN_FIRST_CULUMN:
                actual_table = None
                continue
            cell_table = get_value(pyxl_row, COLUMN_TABLE)

            if actual_table:
                if cell_table == TAG_HYPHEN:
                    continue
                if cell_table == TAG_EMPTY:
                    actual_table = None
                    continue
                actual_table.add_row(pyxl_row, rowidx)
                continue

            if cell_table == TAG_TABLE:
                if len(pyxl_row) <= COLUMN_FIRST_CULUMN:
                    actual_table.raise_exception(f'Need at least {COLUMN_FIRST_CULUMN+1} rows')
                table_name = get_value(pyxl_row, COLUMN_NAME)
                assert table_name is not None
                actual_table = Table(self, table_name, pyxl_worksheet.title, pyxl_row)
                self.__dict_tables[table_name] = actual_table
                setattr(self, f'{self.PREFIX}{table_name}', actual_table)

    @property
    def reference(self):
        return f'File "{self.__filename.name}"'

    @property
    def table_names(self):
        return sorted(self.__dict_tables.keys())

    @property
    def table_names_text(self):
        return '|'.join(self.table_names)

    def __no_table(self, table_name):
        return f'No table "{table_name}". Valid tables are "{self.table_names_text}". See: {self.reference}'

    def __getitem__(self, table_name):
        try:
            return self.__dict_tables[table_name]
        except KeyError as e:
            raise KeyError(self.__no_table(table_name)) from e

    def __getattr__(self, table_name):
        if table_name.startswith(self.PREFIX):
            raise AttributeError(self.__no_table(table_name))
        raise AttributeError(f'"ExcelReader" object has no attribute "{table_name}"')

    def dump(self, file):
        if isinstance(file, Path):
            with file.open('w') as f:
                self.dump(f)
            return

        for table_name in self.table_names:
            self[table_name].dump(file)
