"""
    USE:
        Display a simple chrono / timer

    INSTALLATION:
        pip install tkinter
        pip install pyautogui

"""



"""
    IMPORT SECTION
"""
import tkinter as tk                # for windows display
import tkinter.font                 # Fonts management
from tkinter import simpledialog    # to display a dialog window
from datetime import datetime       # for time management
#from datetime import timedelta      # for time management
import pyautogui                    # Mouse position
import sys                          # To exit
from help_window import HelpWindow  # For the help window



"""
    GLOBAL CONSTANTS
"""
# Windows colors
CHRONO_DIGITS_COLOR = "#000000"
CHRONO_KEYS_COLOR   = "#888888"
CHRONO_BACKGD_COLOR = "#BCE2F2"
TIMER_DIGITS_COLOR  = "#555555"
TIMER_KEYS_COLOR    = CHRONO_KEYS_COLOR #"#666666"
TIMER_BACKGD_COLOR  = "#BCF2CA"
TIMER_DIG_ELP_COLOR = "#FFFFFF" # Timer elapsed
TIMER_KEY_ELP_COLOR = "#CCCCCC" # Timer elapsed
TIMER_BCK_ELP_COLOR = "#DD2222"
KEYS_TEXT           = "c: chrono   t: timer   r: reset\ns: start   Alt+t: top-most"

# Sizes
FONT_SIZE_TIME      = 30
FONT_SIZE_KEYS      = 5
FONT_SIZE_INCR      = 1.25
FONT_SIZE_DECR      = 0.8



"""
    GLOBAL VARIABLES
"""



"""
    CLASS/FUNCTIONS DEFINITION
"""
class ChronoApp:
    def __init__(self, master):
        # Class definition
        self.master = master
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.original_timer_value = None
        self.mode = 'chrono'  # 'chrono' or 'timer'
        self.is_button_1 = False
        self.after_id = None

        # Text definition
        self.font_size_time = FONT_SIZE_TIME
        self.font_size_keys = FONT_SIZE_KEYS
        self.label_time = tk.Label(master,
                                   font=("DSEG7 Classic", self.font_size_time),
                                   text='00:00:00')
        self.label_time.config(fg=CHRONO_DIGITS_COLOR)
        self.label_time.config(bg=CHRONO_BACKGD_COLOR)
        self.label_time.pack(side="top", fill="both", expand=True)
        # self.label_keys = tk.Label(master,
        #                            font=('Arial', self.font_size_keys),
        #                            text=KEYS_TEXT)
        # self.label_keys.config(fg=CHRONO_KEYS_COLOR)
        # self.label_keys.config(bg=CHRONO_BACKGD_COLOR)
        # self.label_keys.pack(side="bottom", fill="both", expand=True)

        # Associate functions to events
        self.master.bind('<Button-1>',          self.press_button_1)
        self.master.bind("<ButtonRelease-1>",   self.release_button_1)
        self.master.bind("<Motion>",            self.move_window)
        self.master.bind('<Double-Button-1>',   self.double_click)
        self.master.bind('<Button-3>',          self.reset)
        #self.master.bind('<space>',             self.toggle_start)
        self.master.bind('s',                   self.toggle_start)
        self.master.bind('c',                   self.c_key)
        self.master.bind('t',                   self.t_key)
        self.master.bind('r',                   self.reset)
        self.master.bind('+',                   self.font_size_increase)
        self.master.bind('-',                   self.font_size_decrease)
        self.master.bind("<F1>",                self.open_help_window)

        self.update_display()
        # Kick off the single perpetual display-update loop (runs regardless of is_running)
        self.update_time()


    def press_button_1(self, event):
        self.is_button_1 = True

    def release_button_1(self, event):
        self.is_button_1 = False

    def move_window(self, event):
        # Get the coordinates of the mouse pointer
        x, y = pyautogui.position()
        # Move the window to the new coordinates
        if self.is_button_1:
            root.pack_propagate(False)
            root.geometry("+{}+{}".format(x, y))
            root.update()


    def top_most(self, event):
        root.wm_attributes("-topmost", True)


    def close_app(self, event):
        """
        Exits the application cleanly, closing all windows.
        """
        # self.master.quit()
        self.master.quit()  # Quit the main event loop
        self.master.destroy()  # Destroy the main window
        sys.exit(0)  # Exit the program
    # end of function



    def set_timer_mode(self):
        self.mode = 'timer'
        # Set timer value
        self.set_timer()


    def set_timer_colors(self):
        self.label_time.config(fg=TIMER_DIGITS_COLOR)
        self.label_time.config(bg=TIMER_BACKGD_COLOR)
        # self.label_keys.config(fg=TIMER_KEYS_COLOR)
        # self.label_keys.config(bg=TIMER_BACKGD_COLOR)
        root.configure(background=TIMER_BACKGD_COLOR)

    def set_timer_elapsed_colors(self):
        self.label_time.config(fg=TIMER_DIG_ELP_COLOR)
        self.label_time.config(bg=TIMER_BCK_ELP_COLOR)
        # self.label_keys.config(fg=TIMER_DIG_ELP_COLOR)
        # self.label_keys.config(bg=TIMER_BCK_ELP_COLOR)
        root.configure(background=TIMER_BACKGD_COLOR)


    def set_chrono_mode(self):
        print("chrono")
        self.mode = 'chrono'
        self.set_chrono_colors()
        # self.label_keys.text = KEYS_TEXT

    def set_chrono_colors(self):
        self.label_time.config(fg=CHRONO_DIGITS_COLOR)
        self.label_time.config(bg=CHRONO_BACKGD_COLOR)
        # self.label_keys.config(fg=CHRONO_KEYS_COLOR)
        # self.label_keys.config(bg=CHRONO_BACKGD_COLOR)
        root.configure(background=CHRONO_BACKGD_COLOR)


    def c_key(self,event):
        self.set_chrono_mode()
        self.reset(event)


    def t_key(self,event):
        if event.state == 0x20008:
            self.top_most()
            print("Alt+t")
        else:
            self.set_timer_mode()
        #print(f"{event}")

    def double_click(self, event):
        if self.mode == 'timer':
            self.set_timer()
        else:
            self.set_timer_mode()


    def split_timer(self, timer_str: str) -> list:
        """
        Split a timer string into 2-character parts, grouping from the right.
        Example: "100" → ['1', '00']
        """
        # Split into individual characters
        chars = list(timer_str)

        # Group into pairs from the right
        parts = []
        while chars:
            if len(chars) >= 2:
                parts.insert(0, ''.join(chars[-2:]))  # Take last 2 chars
                chars = chars[:-2]  # Remove the last 2 chars
            else:
                parts.insert(0, ''.join(chars))  # Take remaining chars
                chars = []  # Clear the list

        return parts


    def set_timer(self, event=None):
        # Stop any running countdown first, so the background update loop can't
        # race with this mode/value change while the modal dialog is open.
        self.is_running = False
        self.set_timer_colors()
        timer_input = simpledialog.askstring("Timer", "Enter time ([[HH.]MM.]SS):")
        if timer_input:
            try:
                parts = timer_input.split('.')
                #
                if len(parts) == 1:  # If only seconds are provided
                    # self.original_timer_value = parts[0]
                    l_timer_parts = self.split_timer(parts[0])
                    if(len(l_timer_parts)==1): # Secs only
                        self.original_timer_value = int(l_timer_parts[0])
                    elif(len(l_timer_parts)==2): # Min, sec
                        self.original_timer_value = (60*int(l_timer_parts[0]) +
                                                     int(l_timer_parts[1]))
                    else: # Hr, Min, Sec
                        self.original_timer_value = (3600*int(l_timer_parts[0]) +
                                                       60*int(l_timer_parts[1]) +
                                                          int(l_timer_parts[2]) )
                else:
                    parts = [int(part) for part in parts]
                    if len(parts) == 2:  # If minutes and seconds are provided
                        self.original_timer_value = parts[0]*60+parts[1]
                    elif len(parts) == 3:  # If hours, minutes, and seconds are provided
                        self.original_timer_value = parts[0]*3600+parts[1]*60+parts[2]
                #end if

                # Add 1 second so that the timer displays the full time
                # before starting to count down
                self.original_timer_value += 1
                self.elapsed_time = 0
                self.update_display()
                self.timer_start()
            except (ValueError, IndexError):
                pass


    def chrono_start(self):
        self.is_running = True
        self.start_time = datetime.now().timestamp()
        self.realign_update_loop()

    def chrono_stop(self):
        self.is_running = False
        self.elapsed_time += (datetime.now().timestamp() - self.start_time)
        self.update_display()

    def timer_start(self):
        self.is_running = True
        self.start_time = datetime.now().timestamp()
        self.realign_update_loop()

    def timer_stop(self):
        self.is_running = False
        self.elapsed_time += (datetime.now().timestamp() - self.start_time)
        self.update_display()


    def toggle_start(self, event=None):
        if self.mode == 'chrono':
            if not self.is_running:
                self.chrono_start()
            else:
                self.chrono_stop()
        elif self.mode == 'timer':
            if not self.is_running:
                self.timer_start()
            else:
                self.timer_stop()


    def reset(self, event=None):
        if self.mode == 'chrono':
            self.is_running = False
            self.start_time = None
            self.elapsed_time = 0
            self.set_chrono_colors()
            self.update_display()
        elif self.mode == 'timer':
            self.set_timer_colors()
            self.is_running = False
            self.start_time = None
            self.elapsed_time = 0
            self.set_timer_colors()
            self.update_display()


    def font_size_increase(self, event=None):
        self.font_size_time *= FONT_SIZE_INCR
        self.font_size_keys *= FONT_SIZE_INCR

        self.label_time.config(font=("DSEG7 Classic", round(self.font_size_time)))
        # self.label_keys.config(font=('Arial', round(self.font_size_keys)))

        # Allow the window to adjust its size based on the new font size
        self.master.pack_propagate(True)

        return


    def font_size_decrease(self, event=None):
        self.font_size_time *= FONT_SIZE_DECR
        self.font_size_keys *= FONT_SIZE_DECR

        self.label_time.config(font=("DSEG7 Classic", round(self.font_size_time)))
        # self.label_keys.config(font=('Arial', round(self.font_size_keys)))

        # Allow the window to adjust its size based on the new font size
        self.master.pack_propagate(True)

        return



    def realign_update_loop(self):
        """Cancel any pending tick and refresh now, so ticks stay aligned to start_time."""
        if self.after_id is not None:
            self.master.after_cancel(self.after_id)
            self.after_id = None
        self.update_time()

    def update_time(self):
        if self.is_running:
            if self.mode == 'chrono':
                delta = self.elapsed_time + (datetime.now().timestamp() - self.start_time)
            elif self.mode == 'timer':
                delta = self.original_timer_value - self.elapsed_time - (datetime.now().timestamp() - self.start_time)
                delta = max(delta, 0)

                # Stop the timer if it reaches zero
                if delta == 0:
                    self.is_running = False
                    #self.set_timer_elapsed_colors()
                    # switch into chrono mode with timer elapsed colors
                    self.set_chrono_mode()
                    self.chrono_start()  # already realigns/reschedules the tick loop
                    self.set_timer_elapsed_colors()
                    return

            seconds = int(delta)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            self.label_time.config(text=f'{hours:02d}:{minutes:02d}:{seconds:02d}')
        self.after_id = self.master.after(1000, self.update_time)


    def update_display(self):
        if self.mode == 'chrono':
            delta = self.elapsed_time
        elif self.mode == 'timer':
            delta = self.original_timer_value - self.elapsed_time
            delta = max(delta, 0)
        seconds = int(delta)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        self.label_time.config(text=f'{hours:02d}:{minutes:02d}:{seconds:02d}')


    def open_help_window(self, event=None): # pylint: disable=unused-argument
        """
        Open the help window.
        """
        HelpWindow(self.master)

        return
    # end of function



if __name__ == '__main__':
    # Create the window
    root = tk.Tk()
    root.title('Chrono/Timer')
    # Set the colors
    #root.config(foreground="white")
    root.configure(background=CHRONO_BACKGD_COLOR)
    # Does not display the title bar
    root.overrideredirect(True)
    # Set the window always on top
    root.wm_attributes("-topmost", True)
    # Launch the app
    app = ChronoApp(root)
    # Bind the scroll-wheel button click event to the close_app method
    root.bind('<Button-2>', app.close_app)
    root.mainloop()

# end of file
