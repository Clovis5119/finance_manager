"""
TO DO:

Create temporary file to act as buffer so we can undo actions.

Flow:
- Read original file (perm file), set initial data state
- Create temporary file
- Copy perm file to temp file, which becomes working file
- Changes should modify data state whenever possible
    - If not possible, changes should modify temp file
- Provide save button to commit changes to perm file

"""


import csv
from file_handler import FileCSV


class MonthlyFinances:
    def __init__(self, year, month):

        self.path = f'test_dir/{year}-{month}'

        # Open permanent file and get its contents
        self.perm_file = FileCSV(f'{self.path}.csv')
        self.data = self.perm_file.get_content()

        # Create temp working file and copy contents to it
        self.temp_file = FileCSV(f'{self.path}-temp.csv')
        self.temp_file.write_content(self.data)
        print(f"Created temp file ::  {f'{self.path}-temp.csv'}")

        # Used by App class to determine read range
        self.length = self.get_length()

    def get_length(self):
        try:
            return len(self.data)
        except TypeError:
            print("ERR: TypeError when attempting to measure length.")
            pass

    def get_header_index(self, n):
        """
        Returns a string's index in the CSV data's header row.

        TODO: Handle exceptions when no matching string is found.

        :param n: string to be found in CSV's header row
        :return: string's index in the header row
        """
        return self.data[0].index(n.strip())

    def get_row(self, i, listed=True):
        """Return a row, formatted as requested."""
        if listed:
            return self.data[i]
        else:
            return ','.join(self.data[i])

    def get_value(self, r, c):
        """

        :param r: row
        :param c: column
        :return: value at the intersection of r and c
        """
        return self.data[r][c]

    def add_row(self, row):
        """Add a row to the data."""

        new_day = int(row[0])       # Day of data entry (as an integer)
        index = self.length         # Default insertion index (end of list)

        # Loop through the data, except header row
        for i, r in enumerate(self.data[1:], start=1):

            # Set insertion index to 1 before next found date in the data
            if int(r[0]) > new_day:
                index = i
                break

        # Insert the data and update the working file
        self.data.insert(index, row)
        self.temp_file.write_content(self.data)
        print(f"Added entry ::  {row}  :: to {self.path}-temp")

    def replace_row(self, old, new):
        """Replace a row with a new one."""
        index = self.data.index(old)
        self.data[index] = new
        print(f"Replaced entry ::  {old}  :: New entry ::  {new}")

    def del_row(self, i):
        """Remove a line from the data and then rewrite the file."""
        removed = self.data.pop(i)
        self.temp_file.write_content(self.data)
        print(f'Removed entry ::  {removed}  :: from {self.path}')

    def close_month(self):

        self.commit_changes()
        self.temp_file.delete_file()

    def commit_changes(self):
        self.perm_file.write_content(self.data)
        print(f"Changes saved to permanent file ::  {self.path}.csv")


# main = MonthlyFinances('2022', '04')
