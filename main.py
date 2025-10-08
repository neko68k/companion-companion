#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
import platform
import tkinter as tk
from tkinter import ttk
from screeninfo import get_monitors
#import serial.tools.list_ports
import json
import pyautogui
import signal

from stereo import SwizzleFrame
import image

def handle_sigint(signum, frame):
    child.destroy()
    root.destroy()

def check_for_interrupt():
    root.after(100, check_for_interrupt)

def get_serial_ports():
    """
    Returns a list of available serial ports with their descriptions.
    """
#    ports = serial.tools.list_ports.comports()
#    port_list = []
#    for port in ports:
#        port_list.append(port.device)
    port_list = ['none']
    return port_list

def close_window(event):
    child.destroy()
    root.destroy()

def show_window():
    global root
    global child
    signal.signal(signal.SIGINT, handle_sigint)

    root = tk.Tk()
    root.title("Tkinter Frame Example")

    # Create a main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill="both", expand=True)

    # Create a sub-frame for input fields
    input_frame = ttk.Frame(main_frame, relief="groove", borderwidth=2, padding="5")
    input_frame.pack(pady=10)

    ports = get_serial_ports()

    variable = tk.StringVar(root)
    variable.set(ports[0])  # Set the default value

    dropdown = tk.OptionMenu(input_frame, variable, *ports).grid(row=0, column=1)

    # Add widgets to the input_frame
    ttk.Label(input_frame, text="Device:").grid(row=0, column=0, sticky="w")
    # ttk.Entry(input_frame).grid(row=0, column=1)

    ttk.Label(input_frame, text="Password:").grid(row=1, column=0, sticky="w")
    ttk.Entry(input_frame, show="*").grid(row=1, column=1)

    # Create a sub-frame for buttons
    button_frame = ttk.Frame(main_frame, padding="5")
    button_frame.pack()

    # Add widgets to the button_frame
    # ttk.Button(button_frame, text="Login").pack(side="left", padx=5)
    # ttk.Button(button_frame, text="Cancel").pack(side="left", padx=5)


    glwindow_geom = ""
    m_x = 0
    m_y = 0

    for m in get_monitors():
        if(m.width == 1440 and m.height == 2560):
            print(m)
            glwindow_geom = f'{m.width}x{m.height}+{m.x}+{m.y}'
            m_x = m.width
            m_y = m.height
            break

    child = tk.Toplevel(root)
    child.title("Child Window")
    child.transient(root) 
    child.geometry(glwindow_geom) # Position relative to screen
    
    if(platform.system() == "Windows"):
        # fullscreen windowed for Windows because this shit is honestly as fucked up as possible for like 2 decades now
        child.overrideredirect(True)
        child.state('zoomed')
    else:
        child.attributes('-fullscreen', True)

    child.focus_force()

    child.bind('<Escape>', close_window)

    with open('deviceConfig.json', 'r') as f:
        dev_info = json.load(f)

    # texture, width, height = image.load(Path('examples') / 'quilt_preview_result.png')
    texture, width, height = image.load(Path('examples') / 'out1.png')
    # texture, width, height = image.load(Path('examples') / 'USA_Baby_quilt_cv2.png')


    glframe = SwizzleFrame(child)
    glframe.SetShaderParams(dev_info['config']['obliquity'], dev_info['config']['lineNumber'], dev_info['config']['deviation'])
    glframe.SetImage(texture, width, height)
    glframe.animate = 1
    glframe.pack(fill="both", expand=True)

    pyautogui.FAILSAFE = False
    pyautogui.moveTo(m_x, m_y)

    check_for_interrupt()
    root.mainloop()


root = None
child = None
show_window()


