#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Blablabla."""

# Python 3 compatibility
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import date
import sys
if sys.version < '3':
    import Tkinter as tk
    import ttk as tk_ttk
    import tkMessageBox as tk_msg_box
else:
    import tkinter as tk
    import tkinter.ttk as tk_ttk
    import tkinter.messagebox as tk_msg_box

import shared


prev_child = child = childs = last_upd = None


def start():
    """Print banner, read/create data & log file and start gui."""
    global prev_child, child, childs, last_upd

    def plus_btn(*args):
        """Blablabla."""
        if int(days_var.get()) < 0:
            days_var.set(0)
        else:
            days_var.set(min(shared.MAX_DAYS, int(days_var.get()) + 1))

    def minus_btn(*args):
        """Blablabla."""
        if int(days_var.get()) > shared.MAX_DAYS:
            days_var.set(shared.MAX_DAYS)
        else:
            days_var.set(max(0, int(days_var.get()) - 1))

    def days_scale_chg(*args):
        """Blablabla."""
        days_var.set(int(float(days_var.get())))  # fix increment to integer

    def childs_combo_chg(*args):
        """Blablabla."""
        global child, prev_child

        try:
            int(days_var.get())
        except ValueError:  # as err:
        #except ValueError:  # , err:
            days_var.set(0)

        if 0 <= int(days_var.get()) <= shared.MAX_DAYS:
            childs[prev_child] = int(days_var.get())
            child = prev_child = childs_combo.get()
            days_var.set(childs[child])
        else:
            childs_combo.set(prev_child)
            tk_msg_box.showwarning('AVISO',
                                   'O número de dias tem que estar entre ' +
                                   '0 e ' + shared.MAX_DAYS_STR)

    def set_upd_btn(upd):
        """Blablabla."""
        global last_upd

        try:
            int(days_var.get())
        except ValueError:
            days_var.set(0)

        if 0 <= int(days_var.get()) <= shared.MAX_DAYS:
            childs[childs_combo.get()] = int(days_var.get())
            if upd:
                last_upd = shared.auto_upd_datafile(childs, last_upd)
            else:
                last_upd = date.today()
                shared.update_file(childs, last_upd)
            last_upd_var.set(value=str(last_upd))
        else:
            tk_msg_box.showwarning('AVISO',
                                   'O número de dias tem que estar entre ' +
                                   '0 e ' + shared.MAX_DAYS_STR)

    def confirm_exit():
        """Blablabla."""
        if tk_msg_box.askokcancel("Sair", "Tem a certeza que pretende sair?"):
            root.destroy()
            sys.exit(0)  # ToDo: other return codes

    def digits_only(up_down, idx, value, prev_val, char, val_type, source,
                    widget):
        """Blablabla."""
        return char in '0123456789' and len(value) <= len(shared.MAX_DAYS_STR)

    def center(window):
        """Blablabla."""
        window.update_idletasks()
        width = window.winfo_width()
        frm_width = window.winfo_rootx() - window.winfo_x()
        win_width = width + 2 * frm_width
        height = window.winfo_height()
        titlebar_height = window.winfo_rooty() - window.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = window.winfo_screenwidth() // 2 - win_width // 2
        y = window.winfo_screenheight() // 2 - win_height // 2
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        if window.attributes('-alpha') == 0:
            window.attributes('-alpha', 1.0)
        window.deiconify()

    def show_help(*args):
        """Blablabla."""
        tk_msg_box.showinfo('Ajuda', shared.usage())

    print(shared.banner())
    childs, last_upd = shared.open_create_datafile()

    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)

    # for exit confirmation
    win.protocol("WM_DELETE_WINDOW", confirm_exit)

    win.title('Dias de castigo')

    # not resizable
    win.resizable(False, False)

    # resizable (limits)
    #win.minsize(250, 125)
    #win.maxsize(500, 250)

    # needed by center function?
    #win.attributes('-alpha', 0.0)

    win.bind("<F1>", show_help)
    win.bind("+", plus_btn)
    win.bind("-", minus_btn)

    # menu
    win.option_add('*tearOff', False)
    menubar = tk.Menu(win)
    win.config(menu=menubar)
    filemenu = tk.Menu(menubar)
    helpmenu = tk.Menu(menubar)

    menubar.add_cascade(label="Ficheiro", menu=filemenu, underline=0)
    menubar.add_cascade(label="Ajuda", menu=helpmenu, underline=0)

    filemenu.add_command(label="Sair", underline=0, command=confirm_exit)

    helpmenu.add_command(label="Ajuda", underline=0, command=show_help,
                         accelerator='F1')
    helpmenu.add_separator()
    helpmenu.add_command(label="Sobre", underline=0, state='disabled')

    # ToDo: log menu item
    ## filemenu.add_separator()
    ## check = StringVar(value=1)
    ## filemenu.add_checkbutton(label='Log', variable=check, onvalue=1,
    ##                          offvalue=0)

    frame = tk_ttk.Frame(win, padding='3 3 3 3')
    frame.grid(column=0, row=0, sticky='WNES')

    # if the main window is resized, the frame should expand
    #frame.columnconfigure(0, weight=1)
    #frame.rowconfigure(0, weight=1)

    # must convert to list for Python 3 compatibility
    prev_child = child = list(childs.keys())[0]

    child_lbl = tk.StringVar(value='Criança:')
    last_upd_lbl = tk.StringVar(value='Última atualização:')

    days_var = tk.StringVar(value=childs[child])
    last_upd_var = tk.StringVar(value=str(last_upd))

    # 1st row
    tk_ttk.Button(frame, text='+', command=plus_btn).grid(column=3, row=1)
    days_scale = tk_ttk.Scale(frame, orient=tk.VERTICAL, length=100,
                              from_=shared.MAX_DAYS, to=0,
                              command=days_scale_chg, variable=days_var)
    days_scale.grid(column=4, row=1, rowspan=3)

    # 2nd row
    tk_ttk.Label(frame, textvariable=child_lbl).grid(column=1, row=2)
    childs_combo = tk_ttk.Combobox(frame, state='readonly',  # width=10,
                                   values=list(childs.keys()))
    childs_combo.grid(column=2, row=2)
    childs_combo.set(child)
    childs_combo.bind('<<ComboboxSelected>>', childs_combo_chg)

    # validate command, used below by some widgets
    vcmd = (win.register(digits_only),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    days_entry = tk_ttk.Entry(frame, width=len(shared.MAX_DAYS_STR) + 1,
                              justify=tk.RIGHT, textvariable=days_var,
                              validate='key', validatecommand=vcmd)
    days_entry.grid(column=3, row=2)  # , sticky='WE')  # for expanding
    tk.Spinbox(frame, from_=0, to=shared.MAX_DAYS,
               width=len(shared.MAX_DAYS_STR) + 1, justify=tk.RIGHT,
               textvariable=days_var, validate='key',
               validatecommand=vcmd).grid(column=5, row=2)

    # 3rd row
    tk_ttk.Button(frame, text='-', command=minus_btn).grid(column=3, row=3)

    # 4th row
    # lambda is necessary so that the function is called on button creation
    tk_ttk.Button(frame, text='Atualizar',
                  command=lambda: set_upd_btn(upd=True)).grid(column=1, row=4)
    tk_ttk.Label(frame, textvariable=last_upd_lbl).grid(column=2, row=4,
                                                        sticky='E')
    tk_ttk.Label(frame, textvariable=last_upd_var).grid(column=3, row=4,
                                                        sticky='W')
    tk_ttk.Button(frame, text='Atribuir',
                  command=lambda: set_upd_btn(upd=False)).grid(column=4, row=4,
                                                               columnspan=2)
    # remove if windows is non resizable
    #tk_ttk.Sizegrip(frame).grid(column=999, row=999, sticky=(E,S))

    # padding around all widgets
    for widget in frame.winfo_children():
        widget.grid_configure(padx=5, pady=5)

    days_entry.focus()

    # center window
    center(win)

    root.mainloop()
