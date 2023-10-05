import multiprocessing
from ui import MainWindow
from datetime import datetime
from parser import update_date, update_fixture


def open_window():
    app = MainWindow()
    p2 = multiprocessing.Process(target = app.update_plots())
    p2.start()
    app.mainloop()

if __name__== "__main__":

    current_date = datetime.today()

    for i in range(4):
        update_date(i+1, current_date.strftime('%Y-%m-%d')) #setting the current date
        update_fixture(i+1, '', 'all of them')              #setting current settings for chosen fixtures as all of them
        # string for the sql query is '', considered fixtures are 'all'

        
    p1 = multiprocessing.Process(target = open_window).start()
   

    
    