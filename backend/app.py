import os
from backend import Engine, Database
from flask import Flask, config, render_template, request
import yaml
import time

app = Flask(__name__, template_folder="../frontend", static_folder="../frontend/assets")
app.debug = True

@app.route("/setup", methods=["POST", "GET"])
def setup():
    configFile = "../config/AppSettings.yaml"
    if os.path.exists(configFile) == False:
        DB_USER = request.form.get('db_user') 
        DB_PASS = request.form.get('db_pass')
        DB_NAME = request.form.get('db_name')
        DB_TABLE = request.form.get('db_table')
        DB_HOST = request.form.get('db_host')
        DB_PORT = request.form.get('db_port')
        FILES_DIR = request.form.get('files_dir')
        PRESETS_FILE = request.form.get('presets_file')
        OUTPUT_DIR = request.form.get('output_dir')

        # print(DB_USER, DB_PASS, DB_NAME, DB_TABLE, DB_HOST, DB_PORT)
        config = {"DB_USER": DB_USER, "DB_PASS": DB_PASS, "DB_NAME": DB_NAME, "DB_TABLE": DB_TABLE, "DB_HOST": DB_HOST, "DB_PORT": DB_PORT, "FILES_DIR": os.path.join(str(FILES_DIR)), "PRESETS_FILE":  os.path.join(str(PRESETS_FILE)), "OUTPUT_DIR": os.path.join(str(OUTPUT_DIR))}
        
        if request.method == "POST":
            with open(configFile, 'w') as file:
                documents = yaml.dump(config, file)   
            return render_template("alerts/updated_message.html")

    else:
        return render_template("alerts/updated_message.html")
    return render_template("setup.html")        

@app.route("/db")
def showDb():
    try:
        raw_data = db.retrieveAllData(db_name, db_table)
        data = []
        packet = []
        heading = ("ID", "Model", "Preset", "Status")
        for l in raw_data:
            file_name = []
            id = l[0]
            for c in reversed(l[1]):
                if c != r"\ ".strip(" "):
                    file_name.append(c)
                else:
                    break
            model = "".join(reversed(file_name))
            preset = l[2].strip("-")
            if l[6] == 1:
                status = "Sliced"
            else:
                status = "Not sliced"

            data = (id, model, preset, status)
            packet.append(data)  

        return render_template("db.html", headings=heading, data=packet)
    except:
        return render_template("alerts/error_1.html")

@app.route("/", methods=["POST", "GET"])
def home():
    try:
        files, settings = main()
        raw_total = db.retrieveAllData(db_name, db_table)
        raw_sliced = db.retrieveBy(db_name, db_table, ("SLICED",""), (1))
        total = len(raw_total)
        sliced = len(raw_sliced)
        if total != 0:
            percentage = round(sliced/total*100)
        else:
            percentage = "--"
    except:
        return render_template("alerts/error_1.html")
    
    if request.method == "POST":
        if request.form.get("update_btn"):
            updateDB(db_name, db_table, files, settings)
        elif request.form.get("slice_btn"):
            print("PRESSED SLICE")
            models = db.retrieveModels(db_name, db_table)
            sliceAll(models)       
        return render_template("home.html", models_total=total, models_sliced=sliced, models_percentage=percentage)
    else:
        return render_template("home.html", models_total=total, models_sliced=sliced, models_percentage=percentage)

    

def main():
    global db, db_name, db_table, engine, output
    configFile = "../config/AppSettings.yaml"
    # Init engine config 
    try:
        with open(configFile, "r") as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)
    except:
        return render_template("")

    filesDir = configs['FILES_DIR']
    db_user = configs['DB_USER']
    db_pass = configs['DB_PASS']
    db_name = configs['DB_NAME']
    db_table = configs['DB_TABLE']
    db_host = configs['DB_HOST']
    db_port = configs['DB_PORT']
    presetsFile = configs['PRESETS_FILE']
    output = configs['OUTPUT_DIR'] 
    
    engine = Engine(presetsFile, filesDir) 
    db = Database(db_name, db_user, db_pass, db_host, db_port)
    conn =  db.Connect()
    files = engine.discover()    
    settings = engine.loadConfig()

    return [files, settings]

def updateDB(db_name, db_table, files, settings):
    for (name, file) in files.items():
        for s in settings:
            printer = settings[s]['printer']
            print_settings = settings[s]['print_settings']
            filament = settings[s]['filament']   

            if name.startswith(s):
                db.createNewEntry(db_name, db_table, file, s+"-", printer, print_settings, filament)
                print(f"FILE: {file} SLICED: (0 by default)")
 
def sliceAll(models):
    for m in models:
        id = m[0]
        file = m[1]
        printer = m[3]
        print_settings = m[4]
        filament = m[5]
        sliced = m[6]

        if sliced != 0:
            print("Already sliced. IGNORING")
        else:
            print(file, printer, print_settings, filament)
            engine.sliceModel(file, output, printer, print_settings, filament)
            db.updateEntry(db_name, db_table, "ID", id, "SLICED", 1)

