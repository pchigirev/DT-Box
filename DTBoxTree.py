"""
DT-Box
Pavel Chigirev, pavelchigirev.com, 2023-2024
See LICENSE.txt for details
"""

import tkinter as tk
from tkinter import ttk
import Indicators

class DTBoxTreeConfig:
    def __init__(self):
        self.columns = []
        self.buttons = []

    def add_column(self, name:str, width:int):
        self.columns.append([name, width])

    def add_button(self, name:str, function:callable, width:int, padx:int):
        self.buttons.append([name, function, width, padx])

class DTBoxTree:
    def add_row(self):
        self.tree_height_ind += 1
        self.tree.configure(height=self.tree_height_ind)

    def delete_row(self):
        if (self.tree_height_ind >= 2):
            self.tree_height_ind -= 1
            self.tree.configure(height=self.tree_height_ind)

    def toggle(self):
        if self.frame_tree.grid_info():
            self.frame_tree.grid_remove()
        else:
            self.frame_tree.grid()

    def create_tree(self, dtbox_tree_config):
        columns = dtbox_tree_config.columns
        self.frame_tree = ttk.Frame(self.root)
        num_columns = len(columns)
        columns_str_idx = [str(i) for i in range(1, num_columns + 1)]
        self.tree = ttk.Treeview(self.frame_tree, columns=columns_str_idx, show="headings", height=4)
        for i in range(num_columns):
            self.tree.heading(i+1, text=columns[i][0])
            self.tree.column(i+1, width=columns[i][1])

        self.scrollbar = ttk.Scrollbar(self.frame_tree, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.pack(side="left")

    def create_buttons(self, dtbox_tree_config):
        buttons = dtbox_tree_config.buttons
        self.frame_buttons = ttk.Frame(self.root)
        self.label = ttk.Label(self.frame_buttons, text=self.name)
        self.label.pack(side="left")

        for btn in buttons:
            button = ttk.Button(self.frame_buttons, text=btn[0], command=btn[1], width=btn[2])
            button.pack(side="left", padx=(btn[3], 0))

        self.tree_height_ind = 4
        self.add_row2_btn = ttk.Button(self.frame_buttons, text=" + ", command=self.add_row, width=3)
        self.detele_row2_btn = ttk.Button(self.frame_buttons, text=" - ", command=self.delete_row, width=3)
        self.exp_coll2_button = ttk.Button(self.frame_buttons, text="S/H", command=self.toggle, width=5)

        self.add_row2_btn.pack(side="left", padx=(self.indent, 0))
        self.detele_row2_btn.pack(side="left", padx=(5, 0))
        self.exp_coll2_button.pack(side="left", padx=(5, 0))

    def __init__(self, root, label_text, indent): 
        self.root = root
        self.name = label_text
        self.indent = indent
        
if __name__ == '__main__':
    import random

    root = tk.Tk()
    root.title("DT-Box-Tree")
    root.resizable(False, False)

    def on_int_modify_button():
        pass

    def delete_indicator():
        pass

    def on_ind_save_button(tree):
        pass

    def on_ind_load_button(tree):
        pass

    def generate_random_ind_pos():
        symbol = random.choice(Indicators.ind_symbols)
        id = random.randint(1, 100)
        ind_type = "MA" #random.choice(indicator_types)
        tf = random.choice(Indicators.ind_periods)
        params = "Period=20;Shift=0;Mode=MODE_SMA;AppliedPrice=PRICE_CLOSE;"
        return f"{symbol},{id},{ind_type},{tf},{params}"

    def on_ind_add_button(tree):
        cmd = generate_random_ind_pos()
        tree.insert('', 'end', values=cmd.split(","))
        return

    dtbox_tree = DTBoxTree(root, "Indicators:", 10)

    dtbox_tree_config = DTBoxTreeConfig()
    dtbox_tree_config.add_column("Symbol", 55)
    dtbox_tree_config.add_column("Id", 30)
    dtbox_tree_config.add_column("Type", 50)
    dtbox_tree_config.add_column("Timeframe", 75)
    dtbox_tree_config.add_column("Params", 270)

    columns = [
        ["Symbol", 55],
        ["Id", 30], 
        ["Type", 50], 
        ["Timeframe", 75], 
        ["Params", 270]
    ]

    dtbox_tree.create_tree(dtbox_tree_config)

    dtbox_tree_config.add_button("Modify", lambda:on_ind_add_button(dtbox_tree.tree), 10, 10)
    dtbox_tree_config.add_button("Delete", lambda:on_ind_add_button(dtbox_tree.tree), 10, 10)
    dtbox_tree_config.add_button("Save", lambda:on_ind_save_button(dtbox_tree.tree), 5, 57)
    dtbox_tree_config.add_button("Load", lambda:on_ind_load_button(dtbox_tree.tree), 5, 10)

    buttons = [ # [name, function, width, padx]
        ["Modify", lambda:on_ind_add_button(dtbox_tree.tree), 10, 10],
        ["Delete", lambda:on_ind_add_button(dtbox_tree.tree), 10, 10],
        ["Save", lambda:on_ind_save_button(dtbox_tree.tree), 5, 57],
        ["Load", lambda:on_ind_load_button(dtbox_tree.tree), 5, 10]
    ]

    dtbox_tree.create_buttons(dtbox_tree_config)

    dtbox_tree.frame_buttons.grid(row=0, column=0, sticky='w', padx=10, pady=(0, 0))
    dtbox_tree.frame_tree.grid(row=1, column=0, sticky='w', padx=10, pady=(10, 5))

    root.mainloop()