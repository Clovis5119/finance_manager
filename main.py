"""
TODO:
 - Expand menu bar
    - Add options submenu
    - Create class for setting options
 - Allow user to create new year file
    - Add + button in dropdown year menu
 - Allow user to create new month file
    - Add + button in dropdown month menu
 - Allow user to set transaction file directory
 - Allow user to set their own categories
 - Allow user to apply category changes to all existing files
 - Set up an options file for convenient styling
    - Turn this into a menu for the user, eventually
 - Provide option for creating beautiful Excel sheet based on yearly data
 - Provide transaction history search options, global and by type
 - Allow nesting transaction types within single purchase
    - So user can collapse and see the total or breakdown in the GUI
 - Handle user inputing non UTF-8 characters
 - Add handling for recurring transactions

"""

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from datetime import datetime
from calendar import monthrange
from reader import MonthlyFinances
from file_handler import DirReader
from categories import categories as cats


def format_month(m):
    """
    Format a month name into a number.

    :param m: Month name as str, ex 'August'
    :return: Month # as double-digit str, ex '08'
    """
    m = datetime.strptime(m, '%B').month
    return f"{m:02}"


def get_day_list(year, month):
    """:returns: list of days for a given year and month."""
    y, m = int(year), int(month)
    return list(range(1, monthrange(y, m)[1] + 1))


class App:

    def __init__(self, master):

        # Default to the current year and month
        date_now = datetime.now()
        self.year = date_now.strftime('%Y')       # Ex: 2023
        self.month = date_now.strftime('%B')      # Ex: 'August'
        self.month_num = date_now.strftime('%m')  # Ex: '08'

        # Set root to constant variable
        self.master = master

        # Initialize empty variables
        self.content = None         # Content to fill treeview
        self.drop_month = None      # Tk options menu widget
        self.selected_year = None   # Tk var for currently selected year
        self.selected_month = None  # Tk var for currently selected month

        # Set window title
        self.master.title("Finance Manager")

        # Set window size
        width = 735
        height = 630
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2,
                                    (screenheight - height) / 2)
        self.master.geometry(alignstr)
        self.master.resizable(width=False, height=False)

        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label='Exit', command=self.master.destroy)
        menubar.add_cascade(label='File', menu=file_menu, underline=0)

    def build_gui(self):
        """Build all the GUI elements."""

        # Create treeview (main window)
        # Change mode to 'extended' to enable multiple selection
        # Change mode to 'browse' to enable single selection
        self.tree = ttk.Treeview(self.master, selectmode='browse')

        # self._set_listbox()
        self._set_treeview()
        self._create_btn_income()
        self._create_btn_expense()
        self._create_btn_edit()
        self._create_btn_delete()
        self._create_drop_year()
        self._create_drop_month()
        self._create_btn_new_month()
        self._create_btn_readout()
        self._create_btn_save()
        self.fill_tree()

    def fill_tree(self, content_added=False, new_month=False):
        """Fill the treeview with content."""

        # Clear the box of any content
        self.tree.delete(*self.tree.get_children())

        # Get new data from new instance.
        # TODO: Optimize to limit repeat instances.

        # Avoids creating a new instance of the same data
        if content_added:
            pass
        elif new_month:
            self.content = MonthlyFinances(self.year, self.month_num)
            self.selected_year.set(self.year)
            self.selected_month.set(self.month)
        else:
            self.content = MonthlyFinances(self.year, self.month_num)

        # Get column index for headers we care about.
        # TODO: Create settings file that includes header preferences.
        c0 = self.content.get_header_index('Day')
        c1 = self.content.get_header_index('Company')
        c2 = self.content.get_header_index('Subcategory')
        c3 = self.content.get_header_index('Amount')

        # Fill the treeview data, row by row
        for row in range(1, self.content.length):

            # Get the data for each column
            col0 = self.content.get_value(row, c0)
            col1 = self.content.get_value(row, c1)
            col2 = self.content.get_value(row, c2)
            col3 = self.content.get_value(row, c3)

            # Then arrange and format it
            text = [f"{col0}", f"{col1}", f"{col2}", f"{col3}"]

            # Then insert it in the treeview
            self.tree.insert(parent='', index=row, text='', values=text)

    def get_selection(self):
        """
        Returns info about the user's current selection in the treeview.

        - iid: Tkinter internal ID for a treeview item
        - index: The item's position in the treeview

        :return: iid, index
        """
        iid = self.tree.focus()                 # Internal ID
        index = self.tree.index(iid) + 1        # Index
        return iid, index

    def change_months(self):
        """
        Change the dropdown menu displaying available months for selection.
        This function should be triggered whenever the user selects a new
        year. This is necessary because it is unlikely there is data for
        each month of every available year.
        """

        # Get updated list of available months based on selected year
        month_list = path.get_months(self.year)

        # Clear current menu contents
        menu = self.drop_month["menu"]
        menu.delete(0, "end")

        # Repopulate menu based on contents of month list
        for month in month_list:
            menu.add_command(label=month,
                             command=lambda value=month:
                             self.selected_month.set(value))

        # If selected month isn't valid, change to most recent valid month
        month_name = self.selected_month.get()

        # If month name is out of range, set it to one within the range
        if month_name not in month_list:
            new_month = month_list[-1]

            # This automatically triggers the change_month function,
            # which loops back to repop, so refill isn't required
            self.selected_month.set(new_month)

        # If month name is in range, fill the treeview box
        else:
            self.content.close_month()
            self.fill_tree()

    def _set_treeview(self):
        """"""
        # Create main treeview
        self.tree['columns'] = ('Day', 'Company', 'Category', 'Amount')

        # Scroll bar
        tree_scroll = ttk.Scrollbar(self.tree)
        tree_scroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column('Day', anchor=tk.W, width=35)
        self.tree.column('Company', anchor=tk.W, width=170)
        self.tree.column('Category', anchor=tk.W, width=170)
        self.tree.column('Amount', anchor=tk.W, width=100)

        self.tree.heading("#0", text='', anchor=tk.CENTER)
        self.tree.heading('Day', text='Day', anchor=tk.CENTER)
        self.tree.heading('Company', text='Company', anchor=tk.CENTER)
        self.tree.heading('Category', text='Category', anchor=tk.CENTER)
        self.tree.heading('Amount', text='Amount', anchor=tk.CENTER)

        self.tree.place(x=20, y=50, width=475, height=560)

    def _create_btn_income(self):
        """"""
        def btn_income_command():
            PopUpTransaction(self.master, transaction='Income')

        # Create income button
        btn_income = tk.Button(self.master)
        btn_income["bg"] = "#5fb878"
        ft = tkFont.Font(family='Times', size=10)
        btn_income["font"] = ft
        btn_income["fg"] = "#000000"
        btn_income["justify"] = "center"
        btn_income["text"] = "Add Income"
        btn_income.place(x=510, y=50, width=200, height=30)
        btn_income["command"] = btn_income_command

    def _create_btn_expense(self):
        """"""
        def btn_expense_command():
            PopUpTransaction(self.master, transaction='Expense')

        # Create expense button
        btn_expense = tk.Button(self.master)
        btn_expense["bg"] = "#ff7800"
        ft = tkFont.Font(family='Times', size=10)
        btn_expense["font"] = ft
        btn_expense["fg"] = "#000000"
        btn_expense["justify"] = "center"
        btn_expense["text"] = "Add Expense"
        btn_expense.place(x=510, y=100, width=200, height=30)
        btn_expense["command"] = btn_expense_command

    def _create_btn_edit(self):
        """"""
        def btn_edit_command():
            """"""
            iid, index = self.get_selection()

            if iid:
                edit_row = self.content.data[index]
                PopUpTransaction(self.master, existing_values=edit_row)

        # Create edit button
        btn_edit = tk.Button(self.master)
        btn_edit["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        btn_edit["font"] = ft
        btn_edit["fg"] = "#000000"
        btn_edit["justify"] = "center"
        btn_edit["text"] = "Edit Selection"
        btn_edit.place(x=510, y=150, width=200, height=30)
        btn_edit["command"] = btn_edit_command

    def _create_btn_delete(self):
        """"""

        def btn_del_command():
            """Delete selected data, if any."""

            # Get info about current user selection
            iid, index = self.get_selection()

            # Delete line from treeview and CSV if one is selected
            if iid:
                self.tree.delete(iid)           # Tree view
                self.content.del_row(index)     # CSV file

        # Create delete button
        btn_del = tk.Button(self.master)
        btn_del["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        btn_del["font"] = ft
        btn_del["fg"] = "#000000"
        btn_del["justify"] = "center"
        btn_del["text"] = "Delete Selection"
        btn_del.place(x=510, y=200, width=200, height=30)
        btn_del["command"] = btn_del_command

    def _create_btn_readout(self):
        """A button that displays a simple summary readout."""
        def btn_readout_command():
            self.content.simple_readout()

        # Create income button
        btn_save = tk.Button(self.master)
        btn_save["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=10)
        btn_save["font"] = ft
        btn_save["fg"] = "#000000"
        btn_save["justify"] = "center"
        btn_save["text"] = "Summary Readout"
        btn_save.place(x=510, y=530, width=200, height=30)
        btn_save["command"] = btn_readout_command

    def _create_btn_save(self):
        """"""
        def btn_save_command():
            self.content.commit_changes()

        # Create income button
        btn_save = tk.Button(self.master)
        btn_save["bg"] = "#8b8bef"
        ft = tkFont.Font(family='Times', size=10)
        btn_save["font"] = ft
        btn_save["fg"] = "#000000"
        btn_save["justify"] = "center"
        btn_save["text"] = "Save Changes"
        btn_save.place(x=510, y=580, width=200, height=30)
        btn_save["command"] = btn_save_command

    def _create_drop_year(self):
        """"""
        # Get the list of available years based on files in directory
        year_list = path.get_years()

        # Create and set TK string variable for selected year
        self.selected_year = tk.StringVar()
        self.selected_year.set(self.year)

        # Create dropdown widget, setting initial year and menu options
        drop_year = tk.OptionMenu(self.master, self.selected_year, *year_list)

        # Format and place dropdown widget
        drop_year["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        drop_year["font"] = ft
        drop_year["fg"] = "#000000"
        drop_year["justify"] = "center"
        drop_year.place(x=20, y=10, width=100, height=30)

        def change_year(*args):
            """Update selected year if it changes."""
            if self.year == self.selected_year.get():
                pass
            else:
                self.year = self.selected_year.get()
                self.change_months()

        self.selected_year.trace('w', change_year)

    def _create_drop_month(self):
        """Create month dropdown"""

        def change_month(*args):
            """Update selected month."""

            # Get the currently selected month from TK string var
            month_name = self.selected_month.get()
            self.month_num = format_month(month_name)

            # Update box contents
            self.change_months()

        # Get the list of available months based on selected year
        month_list = path.get_months(self.year)

        # Create and set TK string variable for selected month
        self.selected_month = tk.StringVar()
        self.selected_month.set(self.month)

        # Create dropdown widget, setting initial month and menu options
        self.drop_month = tk.OptionMenu(self.master, self.selected_month,
                                        self.month, *month_list)

        # Format and place dropdown widget
        self.drop_month["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.drop_month["font"] = ft
        self.drop_month["fg"] = "#000000"
        self.drop_month["justify"] = "center"
        self.drop_month.place(x=120, y=10, width=100, height=30)

        # Triggered by changes in selected month
        self.selected_month.trace('w', change_month)

    def _create_btn_new_month(self):
        """Creates a button for adding a new month."""

        def btn_new_month_command():
            PopUpNewMonth(self.master)

        # Create new-month button
        btn_new_month = tk.Button(self.master)
        btn_new_month["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=14)
        btn_new_month["font"] = ft
        btn_new_month["fg"] = "#000000"
        btn_new_month["justify"] = "center"
        btn_new_month["text"] = "+"
        btn_new_month.place(x=222, y=11, width=27, height=27)
        btn_new_month["command"] = btn_new_month_command


class PopUpTransaction:

    def __init__(self, parent, existing_values=None, transaction='Expense'):

        # Determines default values and close-out behavior
        self.existing_values = existing_values

        # Serves as the top-level menu for categories and subcategories
        self.transaction_type = transaction             # May not be needed
        self.transaction_key = transaction

        # Create a top-level window as the popup
        self.popup = tk.Toplevel(parent)
        self.popup.grab_set()                   # Prevent parent interaction
        self.popup.configure(takefocus=True)    # Doesn't seem to work

        # Set popup window title
        self.popup.title("Entry Edit")

        # Bind ESCAPE key to dismiss function
        self.popup.bind('<Escape>', lambda event=None: self.dismiss())

        # Window size parameters
        width, height = 1120, 65

        # Set the size; not sure how it works, I just copied it
        screenwidth = self.popup.winfo_screenwidth()
        screenheight = self.popup.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2,
                                    (screenheight - height) / 2)
        self.popup.geometry(alignstr)
        self.popup.resizable(width=False, height=False)

        # Establish dictionary of initial values for the popup's entry fields
        self.initial_values = {
            'Day': str(datetime.now().day),
            'Vendor': '',
            'Type': self.transaction_key,
            'Category': '',
            'Subcategory': '',
            'Amount': '',
            'Note': '',
        }

        # Set default lists, starting with transaction types
        self.transaction_list = [*cats]

        # Set default category list and initial value
        self.category_list = [*cats[self.transaction_key]]
        self.initial_values['Category'] = self.category_list[0]

        # Set default subcategory list and initial value
        self.subcat_list = [*cats[self.transaction_key][self.category_list[0]]]
        self.initial_values['Subcategory'] = self.subcat_list[0]

        # Assemble the popup UI
        self.build_gui()

        # If values already provided, set them as the initial values
        if existing_values:
            self.set_existing_values()

        # At this stage all initial values should be set
        # Assign these values to their appropriate Tk StringVars
        self.selected_day.set(self.initial_values['Day'])
        self.selected_type.set(self.initial_values['Type'])
        self.vendor_var.set(self.initial_values['Vendor'])
        self.selected_cat.set(self.initial_values['Category'])
        self.selected_subcat.set(self.initial_values['Subcategory'])
        self.amount_var.set(self.initial_values['Amount'])
        self.note_var.set(self.initial_values['Note'])

    def dismiss(self, update=False):
        """
        Destroys the popup, in case it's needed outside of clicking the
        window's X button.

        Can send out entered data before destruction, if needed.

        :param update: Set to True if entries in the popup fields should be
        saved, or False to simply close the popup window.
        """
        if update:
            self.save_fields()

        # Release the main GUI window and destroy the popup
        self.popup.grab_release()
        self.popup.destroy()

    def save_fields(self):
        """
        Send out user-entered values.
        TODO: Some kind of data validation for the entry boxes.
        """
        # Gather all user-set values into a list
        # Conveniently this is already in a CSV friendly format
        entry = [self.selected_day.get(),
                 self.vendor_var.get(),
                 self.selected_type.get(),
                 self.selected_cat.get(),
                 self.selected_subcat.get(),
                 self.amount_var.get(),
                 self.note_var.get()]

        # If popup was prompted as part of an edit, replace the entry
        if self.existing_values:
            app.content.replace_row(self.existing_values, entry)

        # Otherwise, insert the new entry
        else:
            app.content.add_row(entry)

        # Update content in the main GUI's treeview
        app.fill_tree(content_added=True)

    def build_gui(self):
        """Assemble of the popup's GUI elements"""

        # Transaction day (ex: 3, when rent is due)
        self._create_frm_day()
        self._create_drop_day()

        # Transaction vendor (ex: Amazon, Steam)
        self._create_frm_vendor()
        self._create_ent_vendor()

        # Transaction type (ex: Income, Expense)
        self._create_frm_type()
        self._create_drop_type()

        # Transaction category (ex: Housing, Utilities)
        self._create_frm_cat()
        self._create_drop_cat()

        # Transaction subcategory (ex: Rent, Internet)
        self._create_frm_subcat()
        self._create_drop_subcat()

        # Transaction amount (ex: 383.59)
        self._create_frm_amount()
        self._create_ent_amount()

        # Transaction note (ex: Why did I purchase yet another game?)
        self._create_frm_note()
        self._create_ent_note()

        # Save button to confirm changes
        self._create_btn_save()

    def set_existing_values(self):
        """
        Populate the dictionary of initial values with those determined
        by the user's selection.
        """

        # Gets each (k)ey in the dictionary and its (i)ndex, then sets the
        # key's value to that of the existing value at that index
        for i, k in enumerate(self.initial_values):
            try:
                self.initial_values[k] = self.existing_values[i]
            except IndexError as err:
                print(f"IndexError: {err}. Likely caused by absent note.")

    def change_categories(self, *args):
        """Delete and repopulate list of categories."""

        # Update list of available categories based on transaction type
        self.transaction_key = self.selected_type.get()
        self.category_list = [*cats[self.transaction_key]]

        # Clear current menu contents
        menu = self.drop_cat['menu']
        menu.delete(0, 'end')

        # Repopulate menu with new category list
        for cat in self.category_list:
            menu.add_command(label=cat,
                             command=lambda value=cat:
                             self.selected_cat.set(value))

        self.selected_cat.set(self.category_list[0])

    def change_subcategories(self, *args):
        """Delete and repopulate list of sub-categories."""

        # Update list of available subcategories based on selected category
        new_cat = self.selected_cat.get()
        subcats = [*cats[self.transaction_key][new_cat]]

        # Clear current menu contents
        menu = self.drop_subcat['menu']
        menu.delete(0, 'end')

        # Repopulate menu with new subcategory list
        for sub in subcats:
            menu.add_command(label=sub,
                             command=lambda value=sub:
                             self.selected_subcat.set(value))

        self.selected_subcat.set(subcats[0])

    def _create_frm_day(self):
        """Create label frame for the day dropdown."""

        # Create the label frame
        self.lbl_day = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_day["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_day["font"] = ft
        self.lbl_day["fg"] = "#000000"
        self.lbl_day['labelanchor'] = 'n'
        self.lbl_day['text'] = 'Day'
        self.lbl_day['padx'] = 5
        self.lbl_day['pady'] = 5
        self.lbl_day.place(x=6, y=0, width=70, height=60)

    def _create_drop_day(self):
        """
        Dropdown menu for the day of the month.

        TODO:
         - Populate list of possible days based on selected month
        """

        # Set the list of available days for the selected month
        day_list = get_day_list(app.year, app.month_num)

        # Create TK string variable for selected day
        self.selected_day = tk.StringVar()

        # Create dropdown widget, setting initial year and menu options
        drop_day = tk.OptionMenu(self.lbl_day, self.selected_day, *day_list)

        # Format and place dropdown widget
        drop_day["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        drop_day["font"] = ft
        drop_day["fg"] = "#000000"
        drop_day["justify"] = "center"
        drop_day.pack()

    def _create_frm_vendor(self):
        """Label frame for the company / vendor entry box."""

        # Create the label frame
        self.lbl_vendor = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_vendor["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_vendor["font"] = ft
        self.lbl_vendor["fg"] = "#000000"
        self.lbl_vendor['labelanchor'] = 'n'
        self.lbl_vendor['text'] = 'Company'        # Placeholder
        self.lbl_vendor['padx'] = 5
        self.lbl_vendor['pady'] = 5
        self.lbl_vendor.place(x=80, y=0, width=200, height=60)

    def _create_ent_vendor(self):
        """Entry box for the corporation / company / vendor."""

        # Create the entry box
        ent_vendor = tk.Entry(self.lbl_vendor)

        # Create and assign StringVar that will retrieve entered text
        self.vendor_var = tk.StringVar()
        ent_vendor['textvariable'] = self.vendor_var

        # TODO: use built-in validation tool if needed
        # ent_vendor['validate'] = ?

        # Format and place dropdown widget
        ent_vendor["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=10)
        ent_vendor["font"] = ft
        ent_vendor["fg"] = "#000000"
        ent_vendor["justify"] = "left"
        ent_vendor.place(x=2, y=3, width=180, height=25)

    def _create_frm_type(self):
        """Create a label frame for the category."""

        # Create the label frame
        self.lbl_type = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_type["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_type["font"] = ft
        self.lbl_type["fg"] = "#000000"
        self.lbl_type['labelanchor'] = 'n'
        self.lbl_type['text'] = 'Type'
        self.lbl_type['padx'] = 5
        self.lbl_type['pady'] = 5
        self.lbl_type.place(x=284, y=0, width=120, height=60)

    def _create_drop_type(self):
        """
        Create a dropdown menu for the entry type.

        TODO:
         - Change color of button depending on Expense or Income.
        """

        # Upon transaction type change, set color and change categories
        def change_transaction(*args):
            if self.selected_type.get() == 'Expense':
                drop_type["bg"] = '#ff7800'
                drop_type['activebackground'] = '#ff7800'
            elif self.selected_type.get() == 'Income':
                drop_type["bg"] = '#5fb878'
                drop_type['activebackground'] = '#5fb878'
            else:
                pass            # Shouldn't happen, just a backup
            self.change_categories(self, *args)

        # Create Tk StringVar for selected transaction type
        self.selected_type = tk.StringVar()

        # Create dropdown widget
        drop_type = tk.OptionMenu(
            self.lbl_type, self.selected_type, *self.transaction_list)

        # Format and place dropdown widget
        drop_type["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        drop_type["font"] = ft
        drop_type["fg"] = "#000000"
        drop_type["justify"] = "center"
        drop_type.pack()

        # When user selects a new transaction type, change the categories
        self.selected_type.trace('w', change_transaction)

    def _create_frm_cat(self):
        """Create a label frame for the category."""

        # Create the label frame
        self.lbl_cat = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_cat["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_cat["font"] = ft
        self.lbl_cat["fg"] = "#000000"
        self.lbl_cat['labelanchor'] = 'n'
        self.lbl_cat['text'] = 'Category'
        self.lbl_cat['padx'] = 5
        self.lbl_cat['pady'] = 5
        self.lbl_cat.place(x=408, y=0, width=140, height=60)

    def _create_drop_cat(self):
        """
        Create a dropdown menu for the entry type.

        TODO:
         - List order should be either alphabetical or user-defined
        """

        # Create Tk StringVar for selected transaction category
        self.selected_cat = tk.StringVar()

        # Create dropdown widget
        self.drop_cat = tk.OptionMenu(self.lbl_cat, self.selected_cat,
                                      *self.category_list)

        # Format and place dropdown widget
        self.drop_cat["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.drop_cat["font"] = ft
        self.drop_cat["fg"] = "#000000"
        self.drop_cat["justify"] = "center"
        self.drop_cat.pack()

        # When user selects a new category, change the subcategories
        self.selected_cat.trace('w', self.change_subcategories)

    def _create_frm_subcat(self):
        """Create a label frame for the category."""

        # Create the label frame
        self.lbl_subcat = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_subcat["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_subcat["font"] = ft
        self.lbl_subcat["fg"] = "#000000"
        self.lbl_subcat['labelanchor'] = 'n'
        self.lbl_subcat['text'] = 'Subcategory'
        self.lbl_subcat['padx'] = 5
        self.lbl_subcat['pady'] = 5
        self.lbl_subcat.place(x=552, y=0, width=200, height=60)

    def _create_drop_subcat(self):
        """
        Create a dropdown menu for the entry type.

        TODO:
         - List order should be either alphabetical or user-defined
        """

        # Create Tk StringVar for selected transaction subcategory
        self.selected_subcat = tk.StringVar()

        # Create dropdown widget
        self.drop_subcat = tk.OptionMenu(self.lbl_subcat, self.selected_subcat,
                                         *self.subcat_list)

        # Format and place dropdown widget
        self.drop_subcat["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.drop_subcat["font"] = ft
        self.drop_subcat["fg"] = "#000000"
        self.drop_subcat["justify"] = "center"
        self.drop_subcat.pack()

    def _create_frm_amount(self):
        """Label frame for the amount entry box."""

        # Create the label frame
        self.lbl_amount = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_amount["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_amount["font"] = ft
        self.lbl_amount["fg"] = "#000000"
        self.lbl_amount['labelanchor'] = 'n'
        self.lbl_amount['text'] = 'Amount'
        self.lbl_amount['padx'] = 5
        self.lbl_amount['pady'] = 5
        self.lbl_amount.place(x=756, y=0, width=80, height=60)

    def _create_ent_amount(self):
        """Entry box for the expense / income amount."""

        # Create the entry box
        ent_amount = tk.Entry(self.lbl_amount)

        # Create and assign Tk StringVar that will retrieve entered amount
        self.amount_var = tk.StringVar()
        ent_amount['textvariable'] = self.amount_var

        # Format and place dropdown widget
        ent_amount["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=10)
        ent_amount["font"] = ft
        ent_amount["fg"] = "#000000"
        ent_amount["justify"] = "center"
        ent_amount.place(x=2, y=3, width=60, height=25)

    def _create_frm_note(self):
        """Label frame for the note entry box."""

        # Create the label frame
        self.lbl_note = tk.LabelFrame(self.popup)

        # Format and place the frame
        self.lbl_note["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.lbl_note["font"] = ft
        self.lbl_note["fg"] = "#000000"
        self.lbl_note['labelanchor'] = 'n'
        self.lbl_note['text'] = 'Note'
        self.lbl_note['padx'] = 5
        self.lbl_note['pady'] = 5
        self.lbl_note.place(x=842, y=0, width=210, height=60)

    def _create_ent_note(self):
        """Entry box for the note."""

        # Create the entry box
        ent_note = tk.Entry(self.lbl_note)

        # Create and assign StringVar that will retrieve entered text
        self.note_var = tk.StringVar()

        ent_note['textvariable'] = self.note_var

        # TODO: use built-in validation tool if needed
        # ent_vendor['validate'] = ?

        # Format and place dropdown widget
        ent_note["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=10)
        ent_note["font"] = ft
        ent_note["fg"] = "#000000"
        ent_note["justify"] = "left"
        ent_note.place(x=2, y=3, width=190, height=25)

    def _create_btn_save(self):
        """Create a button to confirm entry."""

        # Create the button
        self.btn_save = tk.Button(self.popup)

        # Format and place the button
        self.btn_save["bg"] = "#8b8bef"
        ft = tkFont.Font(family='Times', size=10)
        self.btn_save["font"] = ft
        self.btn_save["fg"] = "#000000"
        self.btn_save['text'] = 'Confirm'
        self.btn_save['padx'] = 5
        self.btn_save['pady'] = 5
        self.btn_save.place(x=1056, y=8, width=59, height=50)

        # Set button's command and bind ENTER key to it
        self.btn_save.config(command=lambda: self.dismiss(update=True))
        self.popup.bind('<Return>', lambda event=None: self.btn_save.invoke())


class PopUpNewMonth:

    def __init__(self, parent):

        # Create a top-level window as the popup
        self.popup = tk.Toplevel(parent)
        self.popup.grab_set()                   # Prevent parent interaction
        self.popup.configure(takefocus=True)    # Doesn't seem to work

        # Set popup window title
        self.popup.title("New Month")

        # Bind ESCAPE key to dismiss function
        self.popup.bind('<Escape>', lambda event=None: self.dismiss())

        # Window size parameters
        width, height = 240, 35

        # Set the size; not sure how it works, I just copied it
        screenwidth = self.popup.winfo_screenwidth()
        screenheight = self.popup.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2,
                                    (screenheight - height) / 2)
        self.popup.geometry(alignstr)
        self.popup.resizable(width=False, height=False)

        # Assemble the popup UI
        self.build_gui()

    def dismiss(self, update=False):
        """
        Destroys the popup, in case it's needed outside of clicking the
        window's X button.

        Can send out entered data before destruction, if needed.

        :param update: Set to True if entries in the popup fields should be
        saved, or False to simply close the popup window.
        """
        if update:
            y = self.year_var.get()
            m = self.selected_month.get()

            num_m = month_to_num(m)
            print(num_m)

            app.year, app.month, app.month_num = y, m, num_m
            app.fill_tree(new_month=True)

        # Release the main GUI window and destroy the popup
        self.popup.grab_release()
        self.popup.destroy()

    def build_gui(self):
        """Build out the pop-up GUI."""
        self._create_ent_year()
        self._create_drop_month()
        self._create_btn_accept()

    def _create_ent_year(self):
        """Entry box for the user's chosen year."""

        # Create the entry box
        ent_year = tk.Entry(self.popup)

        # Create and assign Tk StringVar that will retrieve entered amount
        self.year_var = tk.StringVar()
        ent_year['textvariable'] = self.year_var
        self.year_var.set('Year')

        # Format and place dropdown widget
        ent_year["bg"] = "#ffffff"
        ft = tkFont.Font(family='Times', size=10)
        ent_year["font"] = ft
        ent_year["fg"] = "#000000"
        ent_year["justify"] = "center"
        ent_year.place(x=5, y=2, width=60, height=27)

    def _create_drop_month(self):

        # Set month list
        month_list = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'October',
            'December',
        ]

        # Create and set TK string variable for selected month
        self.selected_month = tk.StringVar()
        self.selected_month.set('Month')

        # Create dropdown widget, setting initial month and menu options
        self.drop_month = tk.OptionMenu(self.popup, self.selected_month,
                                        *month_list)

        # Format and place dropdown widget
        self.drop_month["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times', size=10)
        self.drop_month["font"] = ft
        self.drop_month["fg"] = "#000000"
        self.drop_month["justify"] = "center"
        self.drop_month.place(x=70, y=0, width=100, height=30)

    def _create_btn_accept(self):
        """Create a button to confirm entry."""

        # Create the button
        self.btn_save = tk.Button(self.popup)

        # Format and place the button
        self.btn_save["bg"] = "#8b8bef"
        ft = tkFont.Font(family='Times', size=10)
        self.btn_save["font"] = ft
        self.btn_save['text'] = 'Accept'
        self.btn_save['padx'] = 5
        self.btn_save['pady'] = 5
        self.btn_save.place(x=175, y=1, width=60, height=27)

        # Set button's command and bind ENTER key to it
        self.btn_save.config(command=lambda: self.dismiss(update=True))
        self.popup.bind('<Return>', lambda event=None: self.btn_save.invoke())


def month_to_num(m):
    """
    :param m: Name of month in full, e.g. 'August'
    :return: Padded month number, e.g. '08'
    """
    return {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }[m]


# Set default file directory
path = DirReader('C:/Create/Code/projects/finances/test_dir')


if __name__ == "__main__":
    root = tk.Tk()          # Create root TK window
    app = App(root)         # Initialize GUI with root as parent
    app.build_gui()         # Build GUI elements
    root.mainloop()

    app.content.close_month()
