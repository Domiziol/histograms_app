from tkinter import *
import multiprocessing
from parser import write_data, read_window_data, update_date, update_fixture, read_database_data
from datetime import datetime
import psycopg2

class Pulling:
    def __init__(self):
        self.credentials = read_database_data()
        self.conn = psycopg2.connect(
            database = self.credentials['dbname'],
            host = self.credentials['host'],
            user = self.credentials['user'],
            password = self.credentials['password']
            )
        self.cur = self.conn.cursor()
        self.get_fixtures()
        self.get_options()
        self.get_years()

    def get_fixtures(self):     #getting available fixtures from database
        sql = '''SELECT tester_id FROM fct1_test \
            GROUP BY tester_id'''
        
        self.cur.execute(sql)
        fix = self.cur.fetchall()
        self.fixtures = []
        for i in range(len(fix)):
            self.fixtures.append(str(fix[i][0]))

    def get_options(self):      #getting available parameters from database
        sql = '''SELECT id, param_name FROM fct1_params_config \
            ORDER BY id'''
        
        self.cur.execute(sql)
        ops = self.cur.fetchall()
        self.options = []
        for i in range(len(ops)):
            self.options.append(str(ops[i][0]) + "  " + str(ops[i][1]))
    
    def get_years(self):        #getting available years from database
        sql = '''SELECT DATE_PART('YEAR', fct1_test_values.timestamp) as year FROM fct1_test_values \
            GROUP BY year \
            ORDER BY year DESC'''
        
        self.cur.execute(sql)
        years = self.cur.fetchall()
        self.years = []
        for i in range(len(years)):
            self.years.append(str(years[i][0]))
            self.years[i] = self.years[i][:-2]
        

pull = Pulling()
FIXTURES = pull.fixtures
OPTIONS = pull.options
YEARS = pull.years

MONTHS = [
    "1","2","3","4","5","6","7","8","9","10","11","12"
]

DAYS = [
    "1","2","3","4",
    "5","6","7","8",
    "9","10","11","12",
    "13","14", "15","16",
    "17","18","19","20",
    "21","22", "23", "24",
    "25", "26","27", "28",
    "29","30","31"
]

class ConfigButton:
    def __init__(self, master, i):
        def button_pressed():
            conWin = ConfigWindow(master, i)
        self.master = master
        self.button = Button(self.master, text = 'config', command = button_pressed)
        if i == 0:
            self.button.place(x = 195, y = 337)
        if i == 1:
            self.button.place(x = 660, y = 337)
        if i == 2:
            self.button.place(x = 195, y = 710)
        if i == 3:
            self.button.place(x = 660, y = 710)

class ConfigWindow(Toplevel):
    def __init__(self, master, i):
        super().__init__()
        self.master = master
        
        self.title("Configuration Window")
        self.geometry('400x300')
        Label(self, text = "Settings for window no. " + str(i+1)).pack()
        Label(self, text = "Choose the parametr from the list:").pack()

        self.win_data = read_window_data(i)

        self.date_format = '%Y-%m-%d'
        self.date = datetime.strptime(self.win_data['date'], self.date_format)

        self.parameter_operations()
        self.date_and_range_operations()
        self.check_box_operations()

        def exit_btn():
            self.check_fixtures()
            self.get_fixtures_names()
            
            param_num = self.number.get()
            if self.limit_box.get() != '':
                limit = self.limit_box.get()
            else: limit = self.win_data['limit']
            year = self.year.get()
            month = self.month.get()
            day = self.day.get()
            date = str(year)+"-"+str(month)+"-"+str(day)
            p = multiprocessing.Process(target = write_data(i+1, param_num[0:2], limit))
            p.start()
            p.join()

            p2 = multiprocessing.Process(target = update_date(i+1,date))
            p2.start()
            p2.join()

            p3 = multiprocessing.Process(target = update_fixture(i+1,self.fixtures, self.names))
            p3.start()
            
            self.destroy()
            self.update()
        self.save_and_exit = Button(self, text = "Save and Exit", command = exit_btn).pack(side = BOTTOM)
        self.master.wait_window(self)
        
    def parameter_operations(self):
        self.number = StringVar()
        self.number.set(OPTIONS[0])
        options = OptionMenu(self, self.number, *OPTIONS)
        options.config(width=20)
        options.pack(pady=5)
    
    def date_and_range_operations(self):
        Label(self, text = "Choose the data range:").place(x = 75, y = 90)
        Label(self, text = "Gather data until:").place(x = 10, y = 120)
        Label(self, text = "year").place(x=70, y=140)
        Label(self, text = "month").place(x=135, y=140)
        Label(self, text = "day").place(x=200, y=140)
        self.year = StringVar()
        self.year.set(str(self.date.year))
        years = OptionMenu(self, self.year, *YEARS)
        years.place(x = 50, y = 160)

        self.month = StringVar()
        self.month.set(str(self.date.month))
        months = OptionMenu(self, self.month, *MONTHS)
        months.place(x = 133, y = 160)

        self.day = StringVar()
        self.day.set(str(self.date.day))
        days = OptionMenu(self, self.day, *DAYS)
        days.place(x = 190, y = 160)

        Label(self, text = "Number of rows to analize:").place(x = 10, y = 200)
        self.limit_box = Entry(master = self)
        self.limit_box.config(width = 15)
        self.limit_box.place(x = 80, y = 220)
    
    def check_box_operations(self):
        Label(self, text = "Fixtures:").place(x = 260, y = 140)
        self.f = []
        c = []
        for i in range(len(FIXTURES)):
            self.f.append(IntVar())
            c.append(Checkbutton(self, text = f'{FIXTURES[i]}', variable = self.f[i]))
            c[i].place(x=260, y = 160+i*20)

    def check_fixtures(self):
        self.fixtures = "AND ("
        count = 0
        for i in range(len(FIXTURES)):
            if self.f[i].get() == 1:
                if self.fixtures != "AND (":
                    self.fixtures += " OR fct1_test.tester_id = "
                    self.fixtures += "'" + f'{FIXTURES[i]}' + "'"
                else:
                    self.fixtures += "fct1_test.tester_id = "
                    self.fixtures += "'" + f'{FIXTURES[i]}' + "'"
            else: count += 1
        
        if count == 0:
            self.fixtures = ''

        if count == len(FIXTURES):
            for i in range(len(FIXTURES)):
                if self.fixtures != "AND (":
                    self.fixtures += " OR fct1_test.tester_id = "
                    self.fixtures += "'" + f'{FIXTURES[i]}' + "'"
                else:
                    self.fixtures += " fct1_test.tester_id = "
                    self.fixtures += "'" + f'{FIXTURES[i]}' + "'"
        
        self.fixtures += ")"
    
    def get_fixtures_names(self):
        count = len(FIXTURES)
        self.names = ''
        for i in range(len(FIXTURES)):
            if self.f[i].get() == 1:
                self.names += f'{FIXTURES[i]}' + ", "
            else: count += 1
        self.names = self.names[:-2]

        if count == len(FIXTURES) or count == 0:
            self.names = 'all of them'
        


        
        
                

        