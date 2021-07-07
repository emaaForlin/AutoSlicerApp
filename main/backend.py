import yaml
import os
import mariadb
import sys

class Engine:
    def __init__(self, PresetFile, FilesDir):
        self.presetFile = PresetFile
        self.filesDir = FilesDir

    def loadConfig(self):
        with open(self.presetFile, 'r') as file:
            presets = yaml.load(file, Loader=yaml.FullLoader)
        return presets

    def discover(self):
        fileList = {}
        with os.scandir(self.filesDir) as models:
            for model in models:
                if os.path.isfile(model) and model.name.endswith(".stl"):
                   # print(model.name)
                    fileList[model.name] = str(self.filesDir) + model.name
                else:
                    pass
                    #print(f"'{model.name}' is not a stl file or it is a directory")
        return fileList
        
    def sliceModel(self, model, printer, print_settings, filament):
        command = f"prusa-slicer-console.exe --export-gcode {model} --output .\output\ --load {printer} --load {print_settings} --load {filament}"
        # print(command)
        os.system(command)


class Database:
    def __init__(self, db_name, db_user, db_pass, db_host, db_port=3306):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_port = db_port
    
    def Connect(self):
        try:
            conn = mariadb.connect(
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )
            conn.autocommit = True
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        
        cursor = conn.cursor()
        return cursor

