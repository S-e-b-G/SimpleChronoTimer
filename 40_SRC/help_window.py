"""
Help Window Module

USE:
    This module provides a help window for the SimpleChronoTimer application.
"""

##################
# IMPORT SECTION
##################
# STANDARD libraries
from tkinter import Toplevel, Label, Button  # For GUI


###########
# CONSTANTS
###########
HLP_USE = "Chrono et timer simple."
HLP_CMD_1 = "\ts:\tStart/Stop."
HLP_CMD_2 = "\tc:\tMode chrono/reset."
HLP_CMD_3 = "\tt:\tMode timer."
HLP_CMD_4 = "\tAlt+t:\tTop most."
HLP_CMD_5 = "\tr:\tReset."
HLP_CMD_6 = "\t+:\tAgrandit l'affichage."
HLP_CMD_7 = "\t-:\tDiminue l'affichage."
HLP_CMD_8 = "Bouton molette:\tFerme la fenêtre."
HLP_CMD_9 = "Double click:\tMode timer."
HELP_CONTENT = HLP_USE + "\n\n" + HLP_CMD_1 + '\n' + HLP_CMD_2 + \
    '\n' + HLP_CMD_3 + '\n' + HLP_CMD_4 + "\n" + HLP_CMD_5 + '\n' + HLP_CMD_6 + \
    '\n' + HLP_CMD_7 + '\n' + HLP_CMD_8 + '\n' + HLP_CMD_9



##################
# CLASS DEFINITION
##################
class HelpWindow:
    """
    Help Window class that handles the GUI and functionality.
    """
    def __init__(self, parent):
        """
        Initialize the Help Window.

        :param parent: The parent Tkinter window.
        """
        self.parent = parent

        # Create the help window
        self.window = Toplevel(parent)
        self.window.title("Guitar Tab Writer: Help")
        self.window.transient(parent)
        self.window.grab_set()
        # self.window.geometry("400x150")

        # Create a Label for the help content
        l_help_content = HELP_CONTENT
        l_help_label = Label(
            self.window,
            text=l_help_content, justify="left", wraplength=700, font=("Arial", 10))
        l_help_label.pack(padx=20, pady=20)

        # Create an OK Button
        l_ok_button = Button(self.window, text="OK", command=self.window.destroy, default="active")
        l_ok_button.pack(pady=(10, 0))

        # Set the focus to the OK Button
        l_ok_button.focus_set()

        # Bind the "Escape" key to close the HelpWindow
        self.window.bind("<Escape>", lambda event: self.window.destroy())

        return
    # end of function

# end of class

# End of file
