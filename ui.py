from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psycopg2
import numpy as np
from parser import read_database_data, read_window_data
from config_win import ConfigButton


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        self.title("Histograms for chosen FCT test parametres")
        self.geometry('880x745')

        self.frame = []
        self.buttons = []
        for i in range(4):
            self.frame.append(Plotter(self, i))
            self.buttons.append(ConfigButton(self, i))

    def update_plots(self):         #this runs all the time, updating plots one by one
        for i in range(4):
            self.frame[i].plotting()        
        self.after(100, self.update_plots())



class Plotter:      # placing and drawing plots
    def __init__(self, master, win_num):
        self.master = master
        self.figure = plt.Figure(dpi = 70)
        self.figure.subplots_adjust()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        if win_num == 0:
            self.canvas.get_tk_widget().grid(column=0, row = 0)
        if win_num == 1:
            self.canvas.get_tk_widget().grid(column=1, row = 0)
        if win_num == 2:
            self.canvas.get_tk_widget().grid(column=0, row = 1, pady=35)
        if win_num == 3:
            self.canvas.get_tk_widget().grid(column=1, row = 1, pady=35)
        self.num = win_num

    def plotting(self):
        database = Database(self.num)
        records, par_data = database.run_query()
        
        min=float(par_data[0][2])
        max=float(par_data[0][3])
        b=round(np.sqrt(len(records)))      #calculating bins for histogram
        more = 0
        a = 0.05        # *100 -> percentage of possible fails

        x=[]
        for r in records:
            if r[0]!='' and r[0] is not None:
                x.append(float(r[0]))
                if float(r[0]) < min or float(r[0]) > max:
                    more +=1

        x_min = [min, min]      #vertical plots that are showing min and max 
        x_max = [max, max]

        self.ax.cla()        
        self.ax.set_xlabel("values, range from min to max set in param config")
        self.ax.set_ylabel("frequency")
        self.ax.set_title("For parameter: "+str(par_data[0][1]) + " fixtures: " + database.win_data['names'])
        
        y_p,x_p,_ = self.ax.hist(x, bins=b, range=(0.8*min,1.2*max))
    
        if more > a*len(x):
            col = 'red'
        else: col = '#1f77b4'
        self.ax.hist(x, bins=b, range=(0.8*min,1.2*max), color = col)
        ymax = y_p.max()
        y= [0, ymax]
        self.ax.plot(x_min, y, 'green')
        self.ax.plot(x_max, y, 'green')
        
        #only for drawing (GUI)
        self.canvas.draw()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
class Database:
    def __init__(self, win_num):
        self.credentials = read_database_data()
        self.conn = psycopg2.connect(
            database = self.credentials['dbname'],
            host = self.credentials['host'],
            user = self.credentials['user'],
            password = self.credentials['password']
            )
        self.cur = self.conn.cursor()
        self.win_data = read_window_data(win_num)
        
    def run_query(self):        # pulling the data for particular window
        limit = self.check_limit()
        
        sql='''SELECT fct1_test_values.value FROM fct1_test_values \
            INNER JOIN fct1_test ON fct1_test.id = fct1_test_values.fct1_test_id \
            WHERE fct1_test_values.param_config_id=''' +str(self.win_data['param'])+ ''' \
            ''' +str(self.win_data['string']) +''' \
            AND DATE(fct1_test_values.timestamp) <=' '''+str(self.win_data['date'])+ '''' \
            ORDER BY fct1_test_values.timestamp DESC LIMIT '''+str(limit) 
        
        params='''SELECT id, param_name, param_value_min, param_value_max FROM fct1_params_config \
            WHERE id=''' +str(self.win_data['param'])
        
        self.cur.execute(sql)
        records = self.cur.fetchall()
        self.cur.execute(params)
        par_data=self.cur.fetchall()
        self.conn.close()

        return records, par_data
    
    def check_limit(self):      #checking if limit in data.ini is not higher than possible number of rows
        count = '''SELECT COUNT(id) FROM fct1_test_values\
            WHERE param_config_id=''' +str(self.win_data['param']) + ''' \
            AND DATE(fct1_test_values.timestamp) <=' '''+str(self.win_data['date']) + '''' \
            '''
        self.cur.execute(count)
        many = self.cur.fetchall()
        if int(many[0][0]) < int(self.win_data['limit']):
            limit = many[0][0]
        else: limit = self.win_data['limit']
        return limit

