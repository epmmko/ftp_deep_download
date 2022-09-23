#This code does a deep download of all files in all subdirectory for the ftp web page format

#URLs are from 
#searching google with
#ftp index of /
# I use DB Browser for SQLite to check the download log
#https://sqlitebrowser.org/
#by Ekarit Panacharoensawad, Sep 22, 2022. CC0, No Rights Reserved

#Tested and work on
# http://www.epncb.oma.be/ftp/data/format/
# https://www.ietf.org/ietf-ftp/ietf-mail-archive/73all/
# http://ftp.sun.ac.za/ftp/pub/documentation/debian/package_building/
# https://fernbase.org/ftp/Salvinia_cucullata/Salvinia_asm_v1.2/chloroplast_genome/
# https://mirbase.org/ftp/7.0/

#Strangely work on
# http://ftp.sun.ac.za/ftp/pub/documentation/C-programming/

#Strangely fail on (infinite loop)
# https://dlink-me.com/ftp/OMNA/
#    Get status 406 to just read the html

#Known to not work on
#Not ftp type: https://github.com/Logan1x/Python-Scripts/
#    http://ftp.sun.ac.za/ftp/pub/documentation/
#    Get to a web page after clicking a folder, instead of reaching to the folder of multiple files
#        Get "None" type
#    
#    http://ftp.sun.ac.za/ftp/pub/documentation/network/
#        Contain the link to external website

from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import urllib.error
import sys
import time
import datetime
from pytz import timezone
import ssl
import sqlite3
import os

class DeepDownload():
    '''To use 
       1) create DeepDownload object 
       2) call deep_download, passying None as argument
          This will let the user type the url
            if just press enter, the default URL using during development will be used
       3) if calling deep_download by passing URL, it will do deep download for that URL
       press ctrl+c if need to stop in the middle

       the URL passing to must have "/" (slash) at the end
       
       usage example is in the "test()" function at the end'''
    def __init__(self):
        self.start_time = time.time()
        # Ignore SSL certificate errors
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

        #set the download destination
        for i in range(10000):
            self.download_folder_name = './download_{:04d}'.format(i)
            if(not os.path.exists(self.download_folder_name)):
                os.makedirs(self.download_folder_name)
                break
        else:
            sys.exit("1000 of download folders are already exist, delete and rerun.")
        print("self.download_folder_name",self.download_folder_name)
        #set the history logging database
        self.conn = sqlite3.connect('download_log.sqlite')
        self.cur = self.conn.cursor()
        self.cur.executescript('''
        CREATE TABLE IF NOT EXISTS DownloadLog(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            file_name TEXT,
            header TEXT,
            source_url TEXT,
            time_since_start TEXT
        );
        '''
        )
    def _query_a_tags(self, url:str):
        print('url being queried = ', url)
        html = urlopen(url, context=self.ctx).read()
        soup = BeautifulSoup(html, "html.parser")
        tags = soup('a')
        raw_file_names = []
        for tag in tags:
            raw_file_names.append(tag.get('href', None))
        return raw_file_names
    def _parse_folder_names(self, url:str, raw_file_names:list):
        print("_parse_folder_names: url", url)
        print("_parse_folder_names: raw_file_names", raw_file_names)

        for i in raw_file_names:
            if i != None:
                print(i, len(i))
            if i != None and len(i) != 0 and i[-1] == '/' and i.count('/') == 1:
                print("ok")

        folder_names = [i for i in raw_file_names if i != None and len(i) != 0 and i[-1] == '/' 
            and i.count('/') == 1 and i != './' and i != '../']
        folder_names = list(set(folder_names))
        folder_names = [url + i for i in folder_names]
        return folder_names
    def _parse_file_names(self, url:str, raw_file_names:list):
        file_names = [i for i in raw_file_names if i != None and len(i) != 0 and i[-1] != '/' and i[0] != '?']
        #fail if the file name start with '?'
        file_names = list(set(file_names))
        file_names = [url + i for i in file_names]
        return file_names
    def get_folder_and_file_lists(self, url:str):
        ''' Example: 
            input: r'https://www.maine.gov/dep/ftp/AIR/MOVES/'
            output: ['https://www.maine.gov/dep/ftp/AIR/MOVES/MOVES_RUN_FILES.zip', 'https://www.maine.gov/dep/ftp/AIR/MOVES/METHODS.zip', 'https://www.maine.gov/dep/ftp/AIR/MOVES/INPUTS_TABLES.zip'],
                    ['https://www.maine.gov/dep/ftp/AIR/MOVES/RESULTS/']
        '''
        raw_file_names = self._query_a_tags(url)
        folder_names = self._parse_folder_names(url, raw_file_names)
        file_names = self._parse_file_names(url, raw_file_names)
        return folder_names, file_names
    def scan_nested_folders(self, url_base:str):
        print("url input ", url_base)
        folder_names, self.base_folder_file_names = self.get_folder_and_file_lists(url_base)
        print("folder_names output = ", folder_names)
        print("_ output ", self.base_folder_file_names)
        unvisited_list = folder_names.copy()
        print('unvisited_list',unvisited_list)
        all_folders = []
        while(unvisited_list):
            p = unvisited_list.pop()
            folder_ans, _ = self.get_folder_and_file_lists(p)
            unvisited_list.extend(folder_ans)
            all_folders.append(p)
        self.all_folders = all_folders
        return all_folders
    def scan_all_files_in_nested_folder(self, url_base:str):
        all_folder_names = self.scan_nested_folders(url_base)
            #without considering the base folder
        unvisited_list = all_folder_names.copy()
        all_file_names = []
        while(unvisited_list):
            p = unvisited_list.pop()
            _, file_names = self.get_folder_and_file_lists(p)
            all_file_names.extend(file_names)
            #This add the file name in the subdirectories,
            #but does not consider the files in the base folder
        self.all_file_names = all_file_names
        all_file_names = self.base_folder_file_names + all_file_names
            #adding the base url
        all_folder_names = [self.url_base] + all_folder_names
            #adding source files in the base url
        return all_file_names, all_folder_names
    @staticmethod
    def _mkdir_tree(path):
        path_before_mkdir = os.getcwd()
        path_split = [i for i in path.split('/') if i != ""]
        for path_element in path_split:
            relative_path = './' + path_element
            if os.path.exists(relative_path):
                os.chdir(relative_path)
            else:
                os.mkdir(relative_path)
        os.chdir(path_before_mkdir)
    def deep_download(self, url:str):
        print('in deep_download')
        if url == None:
            #set base url
            self.url_base = input('url for deep download:')
            if(len(self.url_base) < 1):
                self.url_base = r'https://www.maine.gov/dep/ftp/AIR/MOVES/RESULTS/Preliminary%20Results/'
                #for testing
                #r'https://www.maine.gov/dep/ftp/AIR/MOVES/'
                #https://mirbase.org/ftp/7.0/
            url = self.url_base
        else:
            self.url_base = url

        if url[-1] != '/':
            url = url + '/'  
        try:
            file_names, folder_names = self.scan_all_files_in_nested_folder(url)
        except ValueError:
            local_filename = "url_value_error"
            current_source_file = url
            headers = datetime.datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            time_since_start = time.time() - self.start_time
            time_since_start_str = "{:.2f}".format(time_since_start)
            sql_command = "INSERT INTO DownloadLog(file_name,header,source_url,time_since_start) VALUES (?,?,?,?)"
            self.cur.execute(sql_command, (local_filename, str(headers), current_source_file, time_since_start_str))
            print("Invalid input URL")
            print(f"Input URL = {url}")
            print(f"Time of failure = {headers}")
            self.conn.commit()
            self.conn.close()
            sys.exit()
      

        print('file_names', file_names)
        print('folder_names', folder_names)
        destination_folders = []
        for folder in folder_names:
            destination_folders.append(self.download_folder_name + '/' + folder[len(self.url_base):])
        self.destination_folders = destination_folders.copy()
        print("destination_folders",destination_folders)
        #create all destination directory including subdirectories if does not exist
        for destination_folder in destination_folders:
            self._mkdir_tree(destination_folder)
        current_source_file = ""
        try:
            for file_name in file_names:
                current_source_file = file_name
                destination_name = self.download_folder_name + '/' + file_name[len(self.url_base):]
                print("url = ", file_name)
                print("destination_name = ",destination_name)
                time_since_start = time.time() - self.start_time
                time_since_start_str = "{:.2f}".format(time_since_start)
                print("time from start (s) = " + time_since_start_str)
                local_filename, headers = urlretrieve(file_name, destination_name)
                sql_command = "INSERT INTO DownloadLog(file_name,header,source_url,time_since_start) VALUES (?,?,?,?)"
                self.cur.execute(sql_command, (local_filename, str(headers), file_name, time_since_start_str))
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            local_filename = "KeyboardInterrupt"
            headers = datetime.datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            time_since_start = time.time() - self.start_time
            time_since_start_str = "{:.2f}".format(time_since_start)
            sql_command = "INSERT INTO DownloadLog(file_name,header,source_url,time_since_start) VALUES (?,?,?,?)"
            self.cur.execute(sql_command, (local_filename, str(headers), current_source_file, time_since_start_str))
            print("Interruption details")
            print(f"Current URL = {current_source_file}")
            print(f"Interrupt time = {headers}")
        except urllib.error.HTTPError as err:
            local_filename = "This type of url is not suitable for this ftp deep download. It may contain a link to outside. "+str(err)
            headers = datetime.datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            time_since_start = time.time() - self.start_time
            time_since_start_str = "{:.2f}".format(time_since_start)
            sql_command = "INSERT INTO DownloadLog(file_name,header,source_url,time_since_start) VALUES (?,?,?,?)"
            self.cur.execute(sql_command, (local_filename, str(headers), current_source_file, time_since_start_str))
            print("Error details")
            print(f"Current URL = {current_source_file}")
            print(f"Interrupt time = {headers}")
            print(err)
            print(local_filename)
        except Exception as e:
            print("unknown exception, the url may not be compatible")
            print(e)
            print(type(e))
        finally:
            self.conn.commit()
            self.conn.close()

def test():
    deep_download = DeepDownload()
    deep_download.deep_download(None)
    #deep_download.deep_download("https://www.maine.gov/dep/ftp/AIR/MOVES/RESULTS/")
test()
