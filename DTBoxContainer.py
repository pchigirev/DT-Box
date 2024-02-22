"""
DT-Box
Pavel Chigirev, pavelchigirev.com, 2023-2024
See LICENSE.txt for details
"""

import os
import tkinter as tk
from SocketServer import *

import queue
import threading
import time

import Commands
from DTBoxTree import *
from DTBoxUI import *

# cd src
# pyinstaller -F -i "Logo1.ico" --add-data "Logo1.ico;." --noconsole -n "DT-Box-0.1" DTBoxContainer.py

script_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(script_dir, 'Logo1.ico')

class DTBoxContainer:
    def __init__(self):
        self.root = tk.Tk()
        self.q_send = queue.Queue()
        self.q_recv = queue.Queue()
        self.dtbox = DTBoxUI(self.root, icon_path, self.q_send, self.q_recv, self.on_closing)

        self.socket_server = SocketSrv('127.0.0.1', 16500)
        self.is_shut_down = False

        self.th_process_q_send = None
        self.th_process_q_recv = None
        self.th_watch_connection = None

        th_server_restart = threading.Thread(target=self.restart_connection)
        th_server_restart.start()

        self.root.after(1000, self.dtbox.process_cmds)
        self.root.mainloop()
    
    def restart_connection(self):
        if (self.is_shut_down):
            return
            
        if (self.socket_server.accept_client()):
            self.q_recv.put("cmd_cs,Strategy connected")
            while not self.q_send.empty():
                self.q_send.get()

            self.th_process_q_send = threading.Thread(target=self.socket_server.process_q_send, args=(self.q_send,))
            self.th_process_q_send.start()

            self.th_process_q_recv = threading.Thread(target=self.socket_server.process_q_recv, args=(self.q_recv,))
            self.th_process_q_recv.start()

            self.th_watch_connection = threading.Thread(target=self.watch_connection)
            self.th_watch_connection.start()

        else:
            return

    def watch_connection(self):
        while (not self.is_shut_down):
            if (not self.socket_server.is_client_set):
                self.q_recv.put("cmd_cs,Waiting for strategy")

                th_restart = threading.Thread(target=self.restart_connection)
                th_restart.start()  

                return
                
            self.q_send.put(Commands.cmd_heartbeat)
            time.sleep(1)

    def on_closing(self):
        self.is_shut_down = True
        self.socket_server.is_client_set = False

        if (self.th_process_q_send != None):
            self.th_process_q_send.join()

        if (self.th_process_q_recv != None):
            self.th_process_q_recv.join()

        if (self.th_watch_connection != None):
            self.th_watch_connection.join()

        self.socket_server.shutdown()

        self.root.destroy()

if __name__ == '__main__': DTBoxContainer()