"""
DT-Box
Pavel Chigirev, pavelchigirev.com, 2023-2024
See LICENSE.txt for details
"""

import os
import tkinter as tk
from tkinter import colorchooser
from tkinter import ttk
import csv
from tkinter import filedialog
import webbrowser

import queue
import Helpers
import Commands
import Orders
import Indicators
from DTBoxTree import *

class DTBoxUI:
    def close_selected_order(self):
        tree = self.dtbox_tree_orders.tree
        selected_items = tree.selection()
        for selected_item in selected_items:
            vals = tree.item(selected_item, "values")
            cmd = Commands.cmd_cancel_pending_order + "," + vals[1]
            self.q_send.put(cmd)
            tree.delete(selected_item)

    def close_selected_position(self):
        tree = self.dtbox_tree_positions.tree
        selected_items = tree.selection()
        for selected_item in selected_items:
            vals = tree.item(selected_item, "values")
            cmd = Commands.cmd_close_position + "," + vals[1]
            self.q_send.put(cmd)
            tree.delete(selected_item)

    def part_close_selected_position(self):
        tree = self.dtbox_tree_positions.tree
        sel = tree.selection()
        
        if (len(sel) == 0):
            return

        item = sel[0]
        
        # Retrieve item values
        item_values = tree.item(item, 'values')
        
        # Create a new Toplevel window
        new_window = tk.Toplevel(self.root)
        new_window.title("Patially close")
        new_window.resizable(False, False)
        new_window.transient(self.root)
        new_window.grab_set()
        new_window.iconbitmap(self.icon_path)
        
        # Position the window
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        step = 20
        new_window.geometry(f"+{x + step}+{y + step}")

        fields = ["Symbol", "Ticket", "Time", "Type", "Volume", "Price", "SL", "TP"]
        
        for i, field in enumerate(fields):
            label = tk.Label(new_window, text=field + ":")
            label.grid(row=i, column=0, sticky="e")
        
            label2 = tk.Label(new_window, text=item_values[i])
            label2.grid(row=i, column=1, sticky="w")

        to_close_label =  tk.Label(new_window, text="To close volume:")
        to_close_label.grid(row=i+1, column=0, sticky="w", pady=(15,0))

        entry = tk.Entry(new_window)
        entry.grid(row=i+1, column=1, sticky="e", padx=(0, 20), pady=(15,0))
        entry.insert(0, item_values[4])

        # Create "Modify" and "Cancel" buttons
        modify_button = tk.Button(new_window, text="Modify", command=lambda: self.part_close(new_window, item_values[1], entry))
        modify_button.grid(row=i+2, column=0, columnspan=2, pady=(10,10))

    def part_close(self, new_window, ticket, to_close_vol_entry):
        cmd = Commands.cmd_part_close_position + "," + ticket + "," + to_close_vol_entry.get()
        self.q_send.put(cmd)
        new_window.destroy()

    def modify_order_position(self, isOrder, tree, cmd):
        # Get the selected item
        sel = tree.selection()
        
        if (len(sel) == 0):
            return

        item = sel[0]
        
        # Retrieve item values
        item_values = tree.item(item, 'values')
        
        # Create a new Toplevel window
        new_window = tk.Toplevel(self.root)
        new_window.title("Modify Values")
        new_window.resizable(False, False)
        new_window.transient(self.root)
        new_window.grab_set()
        new_window.iconbitmap(self.icon_path)
        
        # Position the window
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        step = 20
        new_window.geometry(f"+{x + step}+{y + step}")

        fields = ["Symbol", "Ticket", "Time", "Type", "Volume", "Price", "SL", "TP"]
        
        entries = []
        
        for i, field in enumerate(fields):
            # Create a Label and Entry for each field
            label = tk.Label(new_window, text=field + ":")
            label.grid(row=i, column=0, sticky="e", padx=(50, 5))
        
            # Pre-populate the Entries for SL and TP with the selected row values
            columns_to_modify = ["Volume", "Price", "SL", "TP"] if isOrder else ["SL", "TP"]
            if field in  columns_to_modify:
                entry = tk.Entry(new_window)
                entry.grid(row=i, column=1, sticky="w", padx=(0, 20))
                entry.insert(0, item_values[i])
                entries.append(entry)
            else:
                label2 = tk.Label(new_window, text=item_values[i])
                label2.grid(row=i, column=1, sticky="w", padx=(0, 20))
        
        # Create "Modify" and "Cancel" buttons
        modify_button = tk.Button(new_window, text="Modify", command=lambda: self.modify_values(new_window, cmd, item_values[1], entries))
        modify_button.grid(row=len(fields), column=0, columnspan=2, pady=(10,10))

    def modify_values(self, popup, cmd, ticket, entries):
        full_smd = cmd + "," + ticket
        for entry in entries:
            full_smd += "," + entry.get()
        self.q_send.put(full_smd)
        popup.destroy()

    def clear_tree(slef, tree):
        items = tree.get_children()
        # Delete all items
        for item in items:
            tree.delete(item)

    def option_changed(self, *args):
        order_type = self.selected_choice.get()
        if (order_type == "Limit" or order_type == "Stop"):
            self.label_price.configure(state="normal")
            self.price_entry.configure(state="normal")
        else:
            self.label_price.configure(state="disabled")
            self.price_entry.configure(state="disabled")

    def on_ind_add_button(self, *args):
        ind_type = self.selected_ind.get()
        if ("(MA)" in ind_type):
            self.add_modify_indicator(True, "Add new Moving Average", Commands.cmd_new_indicator + ",MA",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.ma_params,
                                Indicators.ma_param_types,
                                Indicators.ma_def_values,
                                [None, None, self.md_str_var, self.pr_str_var])
        
        if ("(CCI)" in ind_type):
            self.add_modify_indicator(True, "Add new Commodity Channel Index", Commands.cmd_new_indicator + ",CCI",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.cci_params,
                                Indicators.cci_param_types,
                                Indicators.cci_def_values,
                                [None, self.pr_str_var])
        
        if ("(BB)" in ind_type):
            self.add_modify_indicator(True, "Add new Bollinger Bands", Commands.cmd_new_indicator + ",BB",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.bb_params,
                                Indicators.bb_param_types,
                                Indicators.bb_def_values,
                                [None, None, None, self.pr_str_var])
            
        if ("MACD" in ind_type):
            self.add_modify_indicator(True, "Add new MACD", Commands.cmd_new_indicator + ",MACD",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.macd_params,
                                Indicators.macd_param_types,
                                Indicators.macd_def_values,
                                [None, None, None, self.pr_str_var])
            
        if ("(SD)" in ind_type):
            self.add_modify_indicator(True, "Add new Standard Deviation", Commands.cmd_new_indicator + ",SD",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.sd_params,
                                Indicators.sd_param_types,
                                Indicators.sd_def_values,
                                [None, None, None, self.pr_str_var])
        
        if ("(ATR)" in ind_type):
            self.add_modify_indicator(True, "Add new Average True Range", Commands.cmd_new_indicator + ",ATR",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.atr_params,
                                Indicators.atr_param_types,
                                Indicators.atr_def_values,
                                [None, None])
            
        if ("(SO)" in ind_type):
            self.add_modify_indicator(True, "Add new Stochastic Oscillator", Commands.cmd_new_indicator + ",SO",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.so_params,
                                Indicators.so_param_types,
                                Indicators.so_def_values,
                                [None, None, None, self.md_str_var, self.st_str_var, None, None])
            
        if ("SAR" in ind_type):
            self.add_modify_indicator(True, "Add new Parabolic SAR", Commands.cmd_new_indicator + ",SAR",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.sar_params,
                                Indicators.sar_param_types,
                                Indicators.sar_def_values,
                                [None, None, None])
        
        if ("TEMA" in ind_type):
            self.add_modify_indicator(True, "Add new Triple EMA", Commands.cmd_new_indicator + ",TEMA",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.tema_params,
                                Indicators.tema_param_types,
                                Indicators.tema_def_values,
                                [None, None, self.pr_str_var, None])
        
        if ("AMA" in ind_type):
            self.add_modify_indicator(True, "Add new Adaptive Moving Average", Commands.cmd_new_indicator + ",AMA",
                                Indicators.ind_symbols[0],
                                Indicators.ind_periods[0],
                                Indicators.ama_params,
                                Indicators.ama_param_types,
                                Indicators.ama_def_values,
                                [None, None, None, None, self.pr_str_var, None])

    def parse_ind_params_line(self, param_line):
        params = []
        pairs = param_line[:-1].split(';')
        for pair in pairs:
            params.append(pair.split("=")[1])
        return params

    def on_ind_modify_button(self, *args):
        tree = self.dtbox_tree_indicators.tree
        selected_items = tree.selection()
        for selected_item in selected_items:
            vals = tree.item(selected_item, "values")
            type = vals[2]
            current_params = self.parse_ind_params_line(vals[4])
            if (type == "MA"): 
                self.add_modify_indicator(False, "Modify Movind Average", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],     
                                vals[3],
                                Indicators.ma_params,
                                Indicators.ma_param_types,
                                current_params,
                                [None, None, self.md_str_var, self.pr_str_var, None])

            if (type == "CCI"): 
                self.add_modify_indicator(False, "Modify Commodity Channel Index", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],    
                                vals[3],
                                Indicators.cci_params,
                                Indicators.cci_param_types,
                                current_params,
                                [None, self.pr_str_var, None])
            
            if (type == "BB"): 
                self.add_modify_indicator(False, "Modify Bollinger Bands", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.bb_params,
                                Indicators.bb_param_types,
                                current_params,
                                [None, None, None, self.pr_str_var])
            
            if (type == "MACD"): 
                self.add_modify_indicator(False, "Modify Bollinger Bands", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.macd_params,
                                Indicators.macd_param_types,
                                current_params,
                                [None, None, None, self.pr_str_var])
            
            if (type == "SD"): 
                self.add_modify_indicator(False, "Modify Standard Deviation", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.sd_params,
                                Indicators.sd_param_types,
                                current_params,
                                [None, None, self.md_str_var, self.pr_str_var, None])
                
            if (type == "ATR"): 
                self.add_modify_indicator(False, "Modify Average True Range", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.atr_params,
                                Indicators.atr_param_types,
                                current_params,
                                [None, None])
            
            if (type == "SO"): 
                self.add_modify_indicator(False, "Modify Stochastic Oscillator", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.so_params,
                                Indicators.so_param_types,
                                current_params,
                                [None, None, None, self.md_str_var, self.st_str_var, None, None])
            
            if (type == "SAR"): 
                self.add_modify_indicator(False, "Modify Parabolic SAR", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.sar_params,
                                Indicators.sar_param_types,
                                current_params,
                                [None, None, None])
                
            if (type == "TEMA"):
                self.add_modify_indicator(False, "Modify Triple EMA", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.tema_params,
                                Indicators.tema_param_types,
                                current_params,
                                [None, None, self.pr_str_var, None])
                
            if (type == "AMA"):
                self.add_modify_indicator(False, "Modify Adapive Moving Average", Commands.cmd_change_indicator + "," + vals[1],
                                vals[0],
                                vals[3],
                                Indicators.ama_params,
                                Indicators.ama_param_types,
                                current_params,
                                [None, None, None, None, self.pr_str_var, None])
            
    def add_modify_indicator(self, isAdd, title, cmd, symbol, timeframe, param_names, param_types, param_values, string_vars):
        new_window = tk.Toplevel()
        new_window.title(title)
        new_window.resizable(False, False)
        new_window.transient(self.root)
        new_window.grab_set()
        new_window.iconbitmap(self.icon_path)
        
        # Position the window
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        step = 20
        new_window.geometry(f"+{x + step}+{y + step}")
        
        entries = []
        validate_i = new_window.register(Helpers.validate_int)
        validate_fl = new_window.register(Helpers.validate_float)

        # Symbol
        label = tk.Label(new_window, text="Symbol:")
        label.grid(row=0, column=0, sticky="e", padx=(50, 5))

        if (isAdd):
            entry = ttk.Combobox(new_window, textvariable=self.sm_str_var, width=17) 
            entry["values"] = Indicators.ind_symbols
            entry.current(Indicators.ind_symbols.index(symbol))
            entry.grid(row=0, column=1, sticky="w", padx=(0, 20))
            entries.append(entry)
        else:
            label = tk.Label(new_window, text=symbol)
            label.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # Timeframe
        label = tk.Label(new_window, text="Timeframe:")
        label.grid(row=1, column=0, sticky="e", padx=(50, 5))

        if (isAdd):
            entry = ttk.Combobox(new_window, textvariable=self.tf_str_var, width=17) 
            entry["values"] = Indicators.ind_periods
            entry.current(Indicators.ind_periods.index(timeframe))
            entry.grid(row=1, column=1, sticky="w", padx=(0, 20))
            entries.append(entry)
        else:
            label = tk.Label(new_window, text=timeframe)
            label.grid(row=1, column=1, sticky="w", padx=(0, 20))

        for i, field in enumerate(param_names):
            # Create a Label and Entry for each field
            label = tk.Label(new_window, text=field + ":")
            label.grid(row=i + 2, column=0, sticky="e", padx=(50, 5))
            
            if (param_types[i] == "int"):
                entry = tk.Entry(new_window, validate='key', validatecommand=(validate_i, '%P'), width=20)
                entry.insert(0, param_values[i])
                entry.grid(row=i + 2, column=1, sticky="w", padx=(0, 20))
            elif (param_types[i] == "double"):
                entry = tk.Entry(new_window, validate='key', validatecommand=(validate_fl, '%P'), width=20)
                entry.insert(0, param_values[i])
                entry.grid(row=i + 2, column=1, sticky="w", padx=(0, 20))
            elif (param_types[i] == "color"):
                entry = tk.Entry(new_window, width=10)
                clr = param_values[i] if '#' in param_values[i] else Helpers.rgb_to_hex(Helpers.str_to_color(param_values[i]))
                entry.insert(0, clr)
                entry.config(bg = clr)
                entry.grid(row=i + 2, column=1, sticky="w", padx=(0, 20), pady=(3, 0))
                color_button = tk.Button(new_window, text="Pick color", command=lambda e=entry: self.update_color_entry(e))
                color_button.grid(row=i + 2, column=1, sticky="w", padx=(63, 0))
            else:
                val_selected = string_vars[i]
                entry = ttk.Combobox(new_window, textvariable=val_selected, width=17) 
                entry["values"] = param_types[i]
                entry.current(param_types[i].index(param_values[i]))
                entry.grid(row=i + 2, column=1, sticky="w", padx=(0, 20))
            
            entries.append(entry)

        # Create "Add" or "Modify" buttons
        modify_button = tk.Button(new_window, text=("Add" if isAdd else "Modify"), command=lambda: self.add_modify_ind_params(new_window, cmd, entries))
        modify_button.grid(row=len(param_names) + 2, column=0, columnspan=2, pady=(10,10))

    def update_color_entry(self, color_entry):
        color = colorchooser.askcolor(title="Choose color", color=color_entry.get())[1] 
        if color:
            color_entry.delete(0, tk.END) 
            color_entry.insert(0, color)  
            color_entry.config(bg=color)

    def add_modify_ind_params(self, popup, cmd, entries):
        for entry in entries:
            val = entry.get()
            if '#' in val: val = Helpers.color_to_str(Helpers.hex_to_rgb(val))
            cmd += "," + val
        self.q_send.put(cmd)
        popup.destroy()

    def on_ind_delete_button(self, *args):
        tree = self.dtbox_tree_indicators.tree
        selected_items = tree.selection()
        for selected_item in selected_items:
            vals = tree.item(selected_item, "values")
            cmd = Commands.cmd_delete_indicator + "," + vals[1]
            self.q_send.put(cmd)
            tree.delete(selected_item)

    def on_ind_save_button(self):
        tree = self.dtbox_tree_indicators.tree
        cols = tree["columns"]
        filename = filedialog.asksaveasfilename(defaultextension=".bxi",
            filetypes=[("BXI files", "*.bxi"), ("All files", "*.*")])

        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(tree["displaycolumns"])
                
                for item in tree.get_children(''):
                    row_data = [tree.set(item, col) for col in cols]
                    writer.writerow(row_data)

    def delete_all_inidicators(self):
        tree = self.dtbox_tree_indicators.tree
        for item in tree.get_children():
            vals = tree.item(item, "values")
            cmd = Commands.cmd_delete_indicator + "," + vals[1]
            self.q_send.put(cmd)
            tree.delete(item)

    def on_ind_load_button(self):
        filename = filedialog.askopenfilename(filetypes=(("BXI files", "*.bxi"),))
        if filename:
            with open(filename, 'r') as file:
                self.delete_all_inidicators()
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    params = row[4][:-1].split(";")
                    param_str = ""
                    for p in params:
                        param_str += "," + p.split("=")[1]
                    cmd = Commands.cmd_new_indicator + "," + row[2] + "," + row[0] + "," + row[3] + param_str
                    self.q_send.put(cmd)

    def on_buy_button(self, *args):
        cmd_str = Commands.cmd_send_new_order + "," + self.selected_symbol.get() + ",true," + Orders.short_order_types[self.selected_choice.get()] + "," + self.price_entry.get() + "," + self.volume_entry.get() + "," + self.sl_entry.get() + "," + self.tp_entry.get()
        self.q_send.put(cmd_str)

    def on_sell_button(self, *args):
        cmd_str = Commands.cmd_send_new_order + "," + self.selected_symbol.get() + ",false," + Orders.short_order_types[self.selected_choice.get()] + "," + self.price_entry.get() + "," + self.volume_entry.get() + "," + self.sl_entry.get() + "," + self.tp_entry.get()
        self.q_send.put(cmd_str)

    def set_always_on_top(self):
        self.root.wm_attributes("-topmost", self.always_on_top.get())

    def link_callback(self, event):
        webbrowser.open_new(r"https://pavelchigirev.com/")

    def __init__(self, root, icon_path, q_send, q_recv, on_closing):
        self.root = root
        self.root.title("DT-Box-0.1: Waiting for strategy")
        self.root.resizable(False, False)

        self.icon_path = icon_path
        self.root.iconbitmap(self.icon_path)

        self.q_send = q_send
        self.q_recv = q_recv

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        self.sm_str_var = tk.StringVar()
        self.tf_str_var = tk.StringVar()
        self.md_str_var = tk.StringVar()
        self.pr_str_var = tk.StringVar()
        self.st_str_var = tk.StringVar()

        self.style = ttk.Style()
        self.style.theme_use("vista")

        # Create a BooleanVar to track whether the checkbox is checked
        self.always_on_top = tk.BooleanVar()
        self.always_on_top.set(True)
        self.root.wm_attributes("-topmost", 1)

        # Create a callback function to set or unset the always-on-top attribute
        def set_always_on_top():
            self.root.wm_attributes("-topmost", self.always_on_top.get())

        # Indicators
        self.frame_ind = ttk.Frame(self.root)
        self.label_ind = ttk.Label(self.frame_ind, text="New indicator:")
        self.label_ind.pack(side="left")

        self.selected_ind = tk.StringVar()
        self.dropdown_ind = ttk.Combobox(self.frame_ind, textvariable=self.selected_ind, width=30) 
        self.dropdown_ind["values"] = Indicators.ind_types
        self.dropdown_ind.current(0)  
        self.dropdown_ind.pack(side="left", padx=(10, 0))

        buy_button = ttk.Button(self.frame_ind, text="Add", command=self.on_ind_add_button, width=5)
        buy_button.pack(side="left", padx=(10, 0))

        # Indicators tree
        self.dtbox_tree_indicators = DTBoxTree(self.root, "Indicators:", 10)
        
        dtbox_tree_ind_config = DTBoxTreeConfig()
        dtbox_tree_ind_config.add_column("Symbol", 55)
        dtbox_tree_ind_config.add_column("Id", 30)
        dtbox_tree_ind_config.add_column("Type", 50)
        dtbox_tree_ind_config.add_column("Timeframe", 75)
        dtbox_tree_ind_config.add_column("Params", 270)
        self.dtbox_tree_indicators.create_tree(dtbox_tree_ind_config)

        dtbox_tree_ind_config.add_button("Modify", self.on_ind_modify_button, 10, 10)
        dtbox_tree_ind_config.add_button("Delete", self.on_ind_delete_button, 10, 10)
        dtbox_tree_ind_config.add_button("Save", self.on_ind_save_button, 5, 57)
        dtbox_tree_ind_config.add_button("Load", self.on_ind_load_button, 5, 10)
        self.dtbox_tree_indicators.create_buttons(dtbox_tree_ind_config)

        self.dtbox_tree_orders = DTBoxTree(self.root, "Pending orders:", 130)
        
        dtbox_tree_orders_config = DTBoxTreeConfig()
        dtbox_tree_orders_config.add_column("Symbol", 55)
        dtbox_tree_orders_config.add_column("Ticket", 45)
        dtbox_tree_orders_config.add_column("Time", 110)
        dtbox_tree_orders_config.add_column("Type", 45)
        dtbox_tree_orders_config.add_column("Volume", 60)
        dtbox_tree_orders_config.add_column("Price", 55)
        dtbox_tree_orders_config.add_column("SL", 55)
        dtbox_tree_orders_config.add_column("TP", 55)
        self.dtbox_tree_orders.create_tree(dtbox_tree_orders_config)

        dtbox_tree_orders_config.add_button("Modify", lambda: self.modify_order_position(True, self.dtbox_tree_orders.tree, Commands.cmd_modify_pending_order), 10, 10) 
        dtbox_tree_orders_config.add_button("Cancel", self.close_selected_order, 10, 10)
        self.dtbox_tree_orders.create_buttons(dtbox_tree_orders_config)

        self.frame_nord0 = ttk.Frame(self.root)
        self.label_nord = ttk.Label(self.frame_nord0, text="New order:")
        self.label_nord.pack(side="left")
        self.checkbutton = tk.Checkbutton(self.frame_ind, text="Always on Top", variable=self.always_on_top, command=self.set_always_on_top)

        self.frame_nord1 = ttk.Frame(self.root)
        self.label_price = ttk.Label(self.frame_nord1, text="Price:", state='disabled')
        self.validate_price= self.frame_nord1.register(Helpers.validate_float)
        self.price_entry = ttk.Entry(self.frame_nord1, validate='key', validatecommand=(self.validate_price, '%P'), width=10, state='disabled')
        self.label_price.pack(side="left", padx=(10, 0))
        self.price_entry.pack(side="left", padx=(39, 0))

        self.frame_nord2 = ttk.Frame(self.root)
        self.label_vol = ttk.Label(self.frame_nord2, text="Volume:")
        self.validate_vol= self.frame_nord2.register(Helpers.validate_float)
        self.default_volume = tk.StringVar()
        self.default_volume.set("0.01")
        self.volume_entry = ttk.Entry(self.frame_nord2, validate='key', textvariable=self.default_volume, validatecommand=(self.validate_vol, '%P'), width=10)
        self.label_vol.pack(side="left", padx=(10, 0))
        self.volume_entry.pack(side="left", padx=(24, 0))

        self.selected_choice = tk.StringVar()
        self.selected_choice.trace("w", self.option_changed)
        self.dropdown = ttk.Combobox(self.frame_nord0, textvariable=self.selected_choice, width=7) 
        self.dropdown["values"] = Orders.order_types
        self.dropdown.current(0)  
        self.dropdown.pack(side="left", padx=(10, 0))
        self.checkbutton.pack(side="left", padx=(50, 0))

        self.label_symb = ttk.Label(self.frame_nord0, text="Symbol:")
        self.label_symb.pack(side="left",  padx=(11, 0))
        self.selected_symbol = tk.StringVar()
        self.dd_sym = ttk.Combobox(self.frame_nord0, textvariable=self.selected_symbol, width=7) 
        self.dd_sym["values"] = Indicators.ind_symbols
        self.dd_sym.current(0)  
        self.dd_sym.pack(side="left", padx=(26, 0))

        self.label_sl = ttk.Label(self.frame_nord1, text="Stop Loss:")
        self.validate_sl = self.frame_nord1.register(Helpers.validate_float)
        self.sl_entry = ttk.Entry(self.frame_nord1, validate='key', validatecommand=(self.validate_sl, '%P'), width=10)
        self.label_sl.pack(side="left", padx=(10, 0))
        self.sl_entry.pack(side="left", padx=(16, 0))

        self.label_tp = ttk.Label(self.frame_nord2, text="Take Profit:")
        self.validate_tp = self.frame_nord2.register(Helpers.validate_float)
        self.tp_entry = ttk.Entry(self.frame_nord2, validate='key', validatecommand=(self.validate_tp, '%P'), width=10)
        self.label_tp.pack(side="left", padx=(10, 0))
        self.tp_entry.pack(side="left", padx=(10, 0))

        self.buy_button = ttk.Button(self.frame_nord1, text="Buy", command=self.on_buy_button, width=10)
        self.sell_button = ttk.Button(self.frame_nord2, text="Sell", command=self.on_sell_button, width=10)
        self.buy_button.pack(side="left", padx=(10, 0))
        self.sell_button.pack(side="left", padx=(10, 0))

        self.dtbox_tree_positions = DTBoxTree(self.root, "Open positions:", 26)
        self.dtbox_tree_positions.create_tree(dtbox_tree_orders_config)
        dtbox_tree_positions_config = DTBoxTreeConfig()
        dtbox_tree_positions_config.add_button("Modify", lambda: self.modify_order_position(False, self.dtbox_tree_positions.tree, Commands.cmd_modify_open_position), 10, 10)
        dtbox_tree_positions_config.add_button("Partially Close", self.part_close_selected_position, 14, 10)
        dtbox_tree_positions_config.add_button("Close", self.close_selected_position, 10, 10)
        self.dtbox_tree_positions.create_buttons(dtbox_tree_positions_config)

        self.frame_footer = ttk.Frame(self.root)
        link = tk.Label(self.frame_footer, text="https://pavelchigirev.com/", fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", self.link_callback)

        # Grid layout
        self.frame_ind.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 7))
        self.dtbox_tree_indicators.frame_buttons.grid(row=1, column=0, sticky='w', padx=10, pady=(0, 7))
        self.dtbox_tree_indicators.frame_tree.grid(row=2, column=0, sticky='w', padx=10, pady=(0, 7))
        self.frame_nord0.grid(row=3, column=0, sticky='w', padx=10, pady=(10, 5))
        self.frame_nord1.grid(row=4, column=0, sticky='w', pady=(0, 5))
        self.frame_nord2.grid(row=5, column=0, sticky='w', pady=(0, 15))
        self.dtbox_tree_orders.frame_buttons.grid(row=6, column=0, padx=10, pady=(0, 7), sticky='w')
        self.dtbox_tree_orders.frame_tree.grid(row=7, column=0, padx=10, pady=(0, 7), sticky='nsew')
        self.dtbox_tree_positions.frame_buttons.grid(row=8, column=0, padx=10, pady=(0, 7), sticky='w')
        self.dtbox_tree_positions.frame_tree.grid(row=9, column=0, padx=10, pady=(0, 3), sticky='nsew')
        self.frame_footer.grid(row=10, padx=10, pady=(0, 3), sticky='e')

        # Configure column and row weights
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.root.grid_rowconfigure(i, weight=1)

    def process_cmds(self):
        while not self.q_recv.empty():
            cmd = self.q_recv.get()
            #q_send.put(cmd)
            values = cmd.split(',')

            if (values[0] == "cmd_cs"):
                self.root.title("DT-Box-0.1: " + values[1])
                if (values[1] == "Waiting for strategy"):
                    self.clear_tree(self.dtbox_tree_indicators.tree)
                    self.clear_tree(self.dtbox_tree_orders.tree)
                    self.clear_tree(self.dtbox_tree_positions.tree)

            if (values[0] == Commands.cmd_all_indicators):
                self.clear_tree(self.dtbox_tree_indicators.tree)
                pos_num = int(values[1])
                for i in range(0, pos_num):
                    step = i * 5
                    self.dtbox_tree_indicators.tree.insert('', 'end', values=
                                    [
                                        values[step + 2], 
                                        values[step + 3], 
                                        values[step + 4], 
                                        values[step + 5],
                                        values[step + 6]])   
                    

            if (values[0] == Commands.cmd_all_pending_orders):
                self.clear_tree(self.dtbox_tree_orders.tree)
                pos_num = int(values[1])
                for i in range(0, pos_num):
                    step = i * 8
                    self.dtbox_tree_orders.tree.insert('', 'end', values=
                                    [
                                        values[step + 2], 
                                        values[step + 3], 
                                        values[step + 4], 
                                        values[step + 5], 
                                        values[step + 6], 
                                        values[step + 7], 
                                        values[step + 8], 
                                        values[step + 9]])   
                        
            if (values[0] == Commands.cmd_all_open_positions):
                self.clear_tree(self.dtbox_tree_positions.tree)
                pos_num = int(values[1])
                for i in range(0, pos_num):
                    step = i * 8
                    self.dtbox_tree_positions.tree.insert('', 'end', values=
                                    [
                                        values[step + 2], 
                                        values[step + 3], 
                                        values[step + 4], 
                                        values[step + 5], 
                                        values[step + 6], 
                                        values[step + 7], 
                                        values[step + 8], 
                                        values[step + 9]])
        
        self.root.after(100, self.process_cmds)

if __name__ == '__main__':
    root = tk.Tk()
    q_send = queue.Queue()
    q_recv = queue.Queue()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(script_dir, 'Logo1.ico')
    dt_box = DTBoxUI(root, icon_path, q_send, q_recv)
    root.mainloop()