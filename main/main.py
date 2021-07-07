from backend import Engine, Database
import pathlib

global DB_NAME, DB_TABLE, DB_USER, DB_PASS, DB_HOST, DB_PORT
DB_NAME = "app"
DB_TABLE = "toSlice"
DB_USER = "slicer"
DB_PASS = "slicer"
DB_HOST = "192.168.0.8"
DB_PORT = 3306


def updateEntry(cursor, db, table, idField, idValue, fieldToUpdate, newValue):
    query = f"UPDATE {db}.{table} SET {fieldToUpdate}={newValue} WHERE {idField} = '{idValue}'"
    #print(query)
    try:
        cursor.execute(query)
        print(f"Field {fieldToUpdate} succesfully updated to {newValue}")
    except:
        print(f"Field {fieldToUpdate} unsuccesfully :(")
    
def retrieveModels(cursor, db, table):
    cursor.execute(
        f"SELECT * FROM {db}.{table} WHERE SLICED = 0"
    )
    models = []
    for l in cursor:
        models.append(l)    
    return models

def createNewEntry(cursor, db, table, file, prefix, printer, print_settings, filament):
    sliced = 0 
    cursor.execute(f"INSERT IGNORE INTO {db}.{table} (FILE, PREFIX, PRINTER, PRINT_SETTINGS, FILAMENT, SLICED) VALUES (?, ?, ?, ?, ?, ?)",(file, prefix, printer, print_settings, filament, sliced))
    print("Trying to add new entry, ignoring if already exists.")

def updateDB(cursor, files, settings):
    for (name, file) in files.items():
        for s in settings:
            printer = settings[s]['printer']
            print_settings = settings[s]['print_settings']
            filament = settings[s]['filament']
            
            if name.startswith(s):
                createNewEntry(cursor, DB_NAME, DB_TABLE, file + str(r"\ ") ,str(s+"-"), printer, print_settings, filament)
                print(f"FILE: {file} PREFIX:  SLICED: (0 by default)")




def main():
    # Configuration data
    db = Database(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)
    engine = Engine("presets.yaml", "D:\\Users\\emaa_forlin\\3D_Objects\\")
    cursor = db.Connect()
    files = engine.discover()    
    settings = engine.loadConfig()

    # Update DB when starts
    updateDB(cursor, files, settings)
    models = retrieveModels(cursor, DB_NAME, DB_TABLE)

    for m in models:
        id = m[0]
        file = m[1][:-2]
        printer = m[3]
        print_settings = m[4]
        filament = m[5]
        sliced = m[6]

        if sliced != 0:
            print("Already sliced. IGNORING")
        else:
            # print(file, printer, print_settings, filament)
            engine.sliceModel(file, printer, print_settings, filament)
            updateEntry(cursor, DB_NAME, DB_TABLE, "ID", id, "SLICED", 1)

main()