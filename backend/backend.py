import os
import psycopg2
import yaml


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
    def __init__(self, db_uri):
        self.db_uri = str(db_uri)
        self.connection = psycopg2.connect(self.db_uri)
        self.connection.autocommit = True

    def updateEntry(self, table, idField, idValue, fieldToUpdate, newValue):
        query = f"UPDATE {table} SET {fieldToUpdate}={newValue} WHERE {idField} = '{idValue}'"
        # print(query)
        try:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
            print("Entry successfully updated.")
        except:
            print("I'm sorry bro, the DB has anxiety")

    def retrieveModels(self, table):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} WHERE SLICED = 0")
                models = cursor.fetchall()
        return models

    def retrieveAllData(self, db_table):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {db_table}")
                data = cursor.fetchall()
        return data

    def retrieveBy(self, table, byFields, byValues):
        data = []
        if len(byFields) == 1 and len(byValues) == len(byFields):
            for f in zip(byFields, byValues):
                sub_query = f"({f[0]}) = ('{f[1]}')"
            query = f"SELECT * FROM {table} WHERE {sub_query}"
            print("SQL Query: " + query)
        
        elif len(byFields) > 1 and len(byValues) == len(byFields):
            fields = ""
            values  = []
            for f in zip(byFields, byValues):
                fields = fields + f[0] + ","
                values.append(f[1])
                sub_query = f"({fields[:-1]}) = {tuple(values)}"
            query = f"SELECT * FROM {table} WHERE {sub_query}"
            print("SQL Query: " + query)
        else:
            print("Something is wrong.")
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
        return data
           
    def createNewEntry(self, table, file, prefix, printer, print_settings, filament, sliced=0):
        exists = self.retrieveBy(table, ["FILE"], [os.path.join(file)])
        with self.connection:
            with self.connection.cursor() as cursor:
                if not exists:
                    cursor.execute(f"INSERT INTO {table} (FILE, PREFIX, PRINTER, PRINT_SETTINGS, FILAMENT, SLICED) VALUES ('{file}', '{prefix}', '{printer}', '{print_settings}', '{filament}', {sliced})")
                    print("Added entry")