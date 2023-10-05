from configparser import ConfigParser
import os
import sys

def get_dir():      #getting current directory for data.ini file
    script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    dir = str(script_directory)+'/data.ini'

    return dir

def write_data(win, par, limit):    #updating file data.ini with new parameter and limit for the specific plot
    config = ConfigParser()
    dir = get_dir()
    config.read(dir)
    nwin = str(win)
    npar = str(par)
    nlimit = str(limit)

    config[nwin]['param'] = npar
    config[nwin]['limit'] = nlimit

    with open(dir,'w') as data_file:
        config.write(data_file) 
    data_file.close()

def update_date(win, date):     #updating 'until date' in data.ini  
    config = ConfigParser()
    dir = get_dir()
    config.read(dir)
    ndate = str(date)
    nwin = str(win)

    for i in range(4):
        config[nwin]['date'] = ndate
    
    with open(dir,'w') as data_file:
        config.write(data_file) 
    data_file.close()

def read_database_data():       #reading data.ini for information (credentials) to database
    dir = get_dir()             
    config = ConfigParser()
    config.read(dir)

    credentials = {
        'host': config['database']['host'],
        'user': config['database']['user'],
        'password': config['database']['password'],
        'dbname': config['database']['dbname']
    }
    return credentials

def read_window_data(win):      #reading all data for creating specific plot
    dir = get_dir()
    config = ConfigParser()
    config.read(dir)
    number = str(win+1)

    win_data = {
        'param': config[number]['param'],
        'limit': config[number]['limit'],
        'frame_rate': config[number]['frame_rate'],
        'date': config[number]['date'],
        'string': config[number]['string'],
        'names': config[number]['names']
    }
    return win_data

def update_fixture(win, fix, names):        #update data when new fixtures are chosen
    dir = get_dir()
    config = ConfigParser()
    config.read(dir)
    nwin = str(win)

    config[nwin]['string'] = fix #it's a string that is a fragment of SQL query that is responsible for pulling data
    config[nwin]['names'] = names   #for specific fixtures

    with open(dir,'w') as data_file:
        config.write(data_file) 
    data_file.close()