from csv import writer
import time

class Logger:

    """
    Logger writes all the events to the log file.
    File format is a csv, each event organized as: NODE IP, TIME, NANOTIME, EVENT
    IP is needed because it is possible to set up all virtual machines to use the same shared folder,
    and in that case there is only one shared log file for all the client nodes.
    """

    def __init__(self, filepath, my_ip):
        self.filepath = filepath
        self.my_ip = my_ip

    def write_log(self, event):
        with open(self.filepath, 'a') as file:
            writer(file).writerow([self.my_ip, time.ctime(), time.time_ns(), event])
            file.close()
