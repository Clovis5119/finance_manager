import os
import csv
import calendar


class FileCSV:
    """A class for handling CSV file contents."""

    def __init__(self, filename):
        """Initializes a file by checking if it exists."""
        self.filename = filename
        self.exists = self.check_file_exists()

        # Sets the CSV format for writing
        csv.register_dialect('default', delimiter=',', lineterminator='\r')

    def check_file_exists(self):
        """Returns TRUE if file exists, FALSE if not."""
        try:
            with open(self.filename):
                return True
        except FileNotFoundError:
            return False

    def get_content(self):
        """
        Returns content of CSV file as a list of lists.
        Could add option to return with/without header row.

        TODO: This shouldn't happen if the file was created via the program,
         but if an entry trips the unicode decode, add a function that can
         identify exactly what line in the CSV file caused it.
        """
        try:
            with open(self.filename, encoding='utf-8') as f_obj:
                reader = csv.reader(f_obj, delimiter=',',
                                    quoting=csv.QUOTE_NONE)

                # Removes leading and trailing whitespace
                return [[x.strip() for x in row] for row in reader]

        # If you get this, try different encoding settings
        except UnicodeDecodeError as error_code:
            print(f"*ERR: UnicodeDecodeError when attempting to read "
                  f"content:\n\t{error_code}")
            return None

    def write_content(self, new_content):
        """Overwrites CSV file with new content."""

        try:
            with open(f'{self.filename}', 'w') as f_obj:
                writer = csv.writer(f_obj, dialect='default')
                for row in new_content:
                    writer.writerow(row)
        except TypeError:
            print('*ERR: TypeError when attempting to write content.')

        self.exists = True

    def clear_content(self):
        """Clears the file of content, without deleting the file."""
        with open(self.filename, 'w') as f_obj:
            f_obj.truncate(0)

    def delete_file(self):
        """Deletes the file."""
        if self.exists:
            os.remove(self.filename)
            self.exists = False
        else:
            print(f"Cannot delete file {self.filename}. It does not exist.")


class DirReader:
    """A class to identify the range of years and months in a directory."""

    def __init__ (self, directory):
        self.directory = directory

    def get_files(self):
        return os.listdir(self.directory)

    def get_years(self):
        """Returns list of years found in directory."""
        years = []
        for date in self.get_files():
            if date[:4] not in years:
                years.append(date[:4])
        return sorted(years)

    def get_months(self, year):
        """Returns list of months for a given year in the directory."""
        months = []
        for date in self.get_files():
            if date[:4] == year and date[8:12] != 'temp':
                month = int(date[5:7])
                months.append(calendar.month_name[month])
        return months

