"""
Program flow:
- Create or read original file (perm file), set initial data state
- Copy data from perm file to a temporary working file
- Changes should modify temp file only
- Save button or exiting program commits changes to perm file

TODO: It's questionable that a temp file is needed at all. Could just work
 from within self.data.
"""

from file_handler import FileCSV
import json
from categories import categories
from categories import keys


class MonthlyFinances:
    def __init__(self, year, month):

        # Create file path based on provided date
        self.path = f'test_dir/{year}-{month}'

        # Open permanent file object
        self.perm_file = FileCSV(f'{self.path}.csv')

        # If perm CSV file doesn't already exist, create it
        if self.perm_file.exists is False:
            self.perm_file.write_content([keys])        # Write header line
            print(f"Created perm file :: {self.path}")

        # Get perm file contents
        self.data = self.perm_file.get_content()

        # Create temporary working file and copy contents to it
        self.temp_file = FileCSV(f'{self.path}-temp.csv')
        self.temp_file.write_content(self.data)
        print(f"Copied contents to temp file ::  {f'{self.path}-temp.csv'}")

        # Used by App class to determine read range
        self.length = self.get_length()

    def get_length(self):
        try:
            return len(self.data)
        except TypeError as err:
            print(f"ERR: TypeError - {err} - "
                  f"when attempting to measure CSV file length")
            pass

    def get_header_index(self, n):
        """
        Returns a string's index in the CSV data's header row.

        TODO: Handle exceptions when no matching string is found.

        :param n: string to be found in CSV header row
        :return: string's index in the header row
        """
        try:
            return self.data[0].index(n.strip())
        except IndexError as err:
            print(f"ERR: IndexError - {err} - "
                  f"when attempting to get index of a header. "
                  f"self.data is {self.data}")
        except TypeError as err:
            print(f"ERR: TypeError - {err} - "
                  f"when attempting to get index of a header. "
                  f"self.data is {self.data}")

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

    def simple_readout(self):
        """Puts out a simple terminal printout of the transaction data."""
        all_transactions = categories       # Dictionary to fill with data

        # Iterate over each row of data, except first row
        for row in self.data[1:]:
            # Keys to populate the dictionary
            trans, cat, sub = row[2], row[3], row[4]

            # Get transaction amount for current row
            try:
                amount = round(float(row[5]), 2)
            except ValueError as err:
                print(f"ValueError ::  {err}  :: Check CSV for name errors.")
                amount = 0.00

            # Tally transaction amounts for each subcategory
            try:
                all_transactions[trans][cat][sub] += amount
            except KeyError as err:
                print(
                    f"KeyError ::  {trans} type {err} not recognized")
                pass

        # Terminal printout of the dictionary
        print(json.dumps(all_transactions, indent=4))
