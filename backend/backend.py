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
        
    def sliceModel(self, model, output, printer, print_settings, filament):
        command = f"prusa-slicer-console.exe --export-gcode {model} --output {output} --load {printer} --load {print_settings} --load {filament}"
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
                port=int(self.db_port),
                database=self.db_name
            )
            conn.autocommit = True
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        self.cursor = conn.cursor()

    def updateEntry(self, db, table, idField, idValue, fieldToUpdate, newValue):
        query = f"UPDATE {db}.{table} SET {fieldToUpdate}={newValue} WHERE {idField} = '{idValue}'"
        #print(query)
        try:
            self.cursor.execute(query)
            print(f"Field {fieldToUpdate} succesfully updated to {newValue}")
        except:
            print(f"Field {fieldToUpdate} unsuccesfully :(")

    def retrieveModels(self, db, table):
        self.cursor.execute(f"SELECT * FROM {db}.{table} WHERE SLICED = 0")
        models = []
        for l in self.cursor:
            models.append(l)    
        return models

    def retrieveAllData(self, db, table):
        data = []
        self.cursor.execute(f"SELECT * FROM {db}.{table}")
        for i in self.cursor:
            data.append(i)
        return data

    def retrieveBy(self, db, table, byFields, byValues):
        data = []
        subComm = ""
        if len(byFields) != 1 and len(byFields) > 0:
            for f in byFields:
                subComm = subComm + f + " "
                subComm = subComm.strip(" ") + ","    
                subComm = subComm[:-1]
                command = f"SELECT * FROM {db}.{table} WHERE ({subComm}) = {byValues}"
        else:
            subComm = byFields
            command = f"SELECT * FROM {db}.{table} WHERE {subComm} = {byValues}"
        # print(command)
        self.cursor.execute(command)
        
        for c in self.cursor:
            data.append(c)
        return data

    def createNewEntry(self, db, table, file, prefix, printer, print_settings, filament, sliced = 0):
        self.cursor.execute(f"INSERT IGNORE INTO {db}.{table} (FILE, PREFIX, PRINTER, PRINT_SETTINGS, FILAMENT, SLICED) VALUES (?, ?, ?, ?, ?, ?)",(file, prefix, printer, print_settings, filament, sliced))
        print("Trying to add new entry, ignoring if already exists.")