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
try:
    import winsound                 # for the timer elapsed sound (Windows only)
except ImportError:
    winsound = None
try:
    import ctypes                   # to locate the monitor showing the timer (Windows only)
    from ctypes import wintypes
except ImportError:
    ctypes = None



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
MESSAGE_FONT_FAMILY = "Segoe UI"  # elegant, stays legible even at small sizes
MESSAGE_FONT_MIN    = 8



"""
    GLOBAL VARIABLES
"""



"""
    CLASS/FUNCTIONS DEFINITION
"""
class TimerSettingsDialog(simpledialog.Dialog):
    """
    Dialog asking for the timer duration, whether an elapsed message should
    be displayed when the countdown reaches 00:00:00, and an optional
    message to display below the counter while the timer is running.
    """
    def __init__(self, parent, title, initial_time="", initial_message_enabled=True,
                 initial_display_message=""):
        self.initial_time = initial_time
        self.initial_message_enabled = initial_message_enabled
        self.initial_display_message = initial_display_message
        self.time_value = None
        self.message_enabled = initial_message_enabled
        self.display_message = initial_display_message
        self.entry_time = None
        self.message_var = None
        self.entry_display_message = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Temps ([[HH.]MM.]SS) :").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_time = tk.Entry(master)
        self.entry_time.insert(0, self.initial_time)
        self.entry_time.grid(row=0, column=1, padx=5, pady=5)

        self.message_var = tk.BooleanVar(value=self.initial_message_enabled)
        tk.Checkbutton(master,
                       text="Afficher un message quand le minuteur est écoulé",
                       variable=self.message_var).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(master, text="Message affiché sous le compteur (optionnel) :").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 0))
        self.entry_display_message = tk.Entry(master)
        self.entry_display_message.insert(0, self.initial_display_message)
        self.entry_display_message.grid(
            row=3, column=0, columnspan=2, sticky="we", padx=5, pady=(0, 5))

        return self.entry_time  # initial focus

    def apply(self):
        self.time_value = self.entry_time.get()
        self.message_enabled = self.message_var.get()
        self.display_message = self.entry_display_message.get().strip()


class ChronoApp:
    def __init__(self, master):
        # Class definition
        self.master = master
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.original_timer_value = None
        self.timer_message_enabled = True  # show a message when the timer elapses
        self.timer_display_message = ""  # optional message shown below the counter
        self.timer_elapsed = False  # keep the message visible after the countdown ends
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
        self.label_message = tk.Label(master,
                                   font=(MESSAGE_FONT_FAMILY, self.message_font_size(), "italic"),
                                   text='', pady=0, borderwidth=0, highlightthickness=0)
        self.label_message.config(fg=CHRONO_DIGITS_COLOR)
        self.label_message.config(bg=CHRONO_BACKGD_COLOR)
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
        self.label_message.config(fg=TIMER_DIGITS_COLOR)
        self.label_message.config(bg=TIMER_BACKGD_COLOR)
        # self.label_keys.config(fg=TIMER_KEYS_COLOR)
        # self.label_keys.config(bg=TIMER_BACKGD_COLOR)
        root.configure(background=TIMER_BACKGD_COLOR)

    def set_timer_elapsed_colors(self):
        self.label_time.config(fg=TIMER_DIG_ELP_COLOR)
        self.label_time.config(bg=TIMER_BCK_ELP_COLOR)
        self.label_message.config(fg=TIMER_DIG_ELP_COLOR)
        self.label_message.config(bg=TIMER_BCK_ELP_COLOR)
        # self.label_keys.config(fg=TIMER_DIG_ELP_COLOR)
        # self.label_keys.config(bg=TIMER_BCK_ELP_COLOR)
        root.configure(background=TIMER_BACKGD_COLOR)


    def set_chrono_mode(self):
        print("chrono")
        self.mode = 'chrono'
        self.set_chrono_colors()
        self.update_message_label()
        # self.label_keys.text = KEYS_TEXT

    def set_chrono_colors(self):
        self.label_time.config(fg=CHRONO_DIGITS_COLOR)
        self.label_time.config(bg=CHRONO_BACKGD_COLOR)
        self.label_message.config(fg=CHRONO_DIGITS_COLOR)
        self.label_message.config(bg=CHRONO_BACKGD_COLOR)
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
        dialog = TimerSettingsDialog(self.master, "Minuteur",
                                      initial_message_enabled=self.timer_message_enabled,
                                      initial_display_message=self.timer_display_message)
        timer_input = dialog.time_value
        if timer_input:
            self.timer_message_enabled = dialog.message_enabled
            self.timer_display_message = dialog.display_message
            self.timer_elapsed = False
            self.update_message_label()
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


    def get_current_monitor_geometry(self):
        """
        Return (left, top, width, height) of the monitor currently showing
        the main window. Falls back to the primary screen if unavailable.
        """
        if ctypes is not None:
            try:
                hwnd = self.master.winfo_id()
                monitor = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST

                class MONITORINFO(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", wintypes.DWORD),
                        ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD),
                    ]

                info = MONITORINFO()
                info.cbSize = ctypes.sizeof(MONITORINFO)
                ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(info))
                rect = info.rcWork
                return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
            except Exception: # pylint: disable=broad-except
                pass
        return 0, 0, self.master.winfo_screenwidth(), self.master.winfo_screenheight()


    def play_timer_elapsed_sound(self):
        if winsound is not None:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                return
            except Exception: # pylint: disable=broad-except
                pass
        self.master.bell()


    def show_timer_elapsed_message(self):
        top = tk.Toplevel(self.master)
        top.title("Minuteur")
        top.resizable(False, False)
        top.attributes("-topmost", True)

        tk.Label(top, text="Le temps est écoulé !",
                 padx=20, pady=20).pack()
        ok_button = tk.Button(top, text="OK", width=10, default="active",
                               command=top.destroy)
        ok_button.pack(pady=(0, 10))

        # OK must be triggered by Enter/Return even though it is not focused
        # by default; the user must press Tab to actually select it.
        top.bind('<Return>', lambda event: top.destroy())
        top.protocol("WM_DELETE_WINDOW", top.destroy)

        # Center the window on the monitor showing the timer
        top.update_idletasks()
        screen_left, screen_top, screen_width, screen_height = self.get_current_monitor_geometry()
        win_width = top.winfo_width()
        win_height = top.winfo_height()
        pos_x = screen_left + (screen_width - win_width) // 2
        pos_y = screen_top + (screen_height - win_height) // 2
        top.geometry(f"+{pos_x}+{pos_y}")

        top.focus_set()  # focus the window, not the OK button
        top.grab_set()
        top.lift()


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
        self.timer_elapsed = False
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
        self.update_message_label()


    def message_font_size(self):
        return max(MESSAGE_FONT_MIN, round(self.font_size_time / 2))


    def update_message_label(self):
        """Show the optional message below the counter, timer mode only (kept
        visible once the countdown has elapsed, until the next reset)."""
        self.label_message.config(font=(MESSAGE_FONT_FAMILY, self.message_font_size(), "italic"))
        if (self.mode == 'timer' or self.timer_elapsed) and self.timer_display_message:
            self.label_message.config(text=self.timer_display_message)
            # Let the window grow to fit the extra label, even if a previous
            # drag froze its size via pack_propagate(False).
            self.master.pack_propagate(True)
            self.label_message.pack(side="top", fill="both", pady=0)
        else:
            self.label_message.pack_forget()


    def font_size_increase(self, event=None):
        self.font_size_time *= FONT_SIZE_INCR
        self.font_size_keys *= FONT_SIZE_INCR

        self.label_time.config(font=("DSEG7 Classic", round(self.font_size_time)))
        self.update_message_label()
        # self.label_keys.config(font=('Arial', round(self.font_size_keys)))

        # Allow the window to adjust its size based on the new font size
        self.master.pack_propagate(True)

        return


    def font_size_decrease(self, event=None):
        self.font_size_time *= FONT_SIZE_DECR
        self.font_size_keys *= FONT_SIZE_DECR

        self.label_time.config(font=("DSEG7 Classic", round(self.font_size_time)))
        self.update_message_label()
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
                    self.timer_elapsed = True  # keep showing the timer message despite the mode switch
                    self.update_message_label()
                    self.play_timer_elapsed_sound()
                    if self.timer_message_enabled:
                        self.show_timer_elapsed_message()
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
