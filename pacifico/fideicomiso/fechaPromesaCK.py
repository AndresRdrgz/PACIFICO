import json
from datetime import datetime, timedelta

def checkDiaHabil(fechaCalculo):
    # Load the JSON data
    json_file_path = '/Users/andresrdrgz_/Documents/PACIFICO/financiera/pacifico/fideicomiso/calendario.json'
    with open(json_file_path, 'r') as file:
        data = [json.loads(line) for line in file]

    # Convert fechaCalculo to a date object
    fecha_date = fechaCalculo.date()

    # Search for the corresponding date in the JSON data
    for record in data:
        record_date = datetime.utcfromtimestamp(record["FECHA"] / 1000).date()
        if record_date == fecha_date:
            return record["TIPO DIA"]

    # If the date is not found, return None or an appropriate message
    return "Date not found"

def calculoFechaPromesa():
    no_patrono = 512
    diasprom1 = 10
    diasprom2 = 5
    fechaCalculo = datetime.now()
    ii = 0
    auxLibres = 0

    if 638 <= no_patrono <= 654 and no_patrono != 646:
        ii = diasprom2
    else:
        ii = diasprom1

    if no_patrono == 620:
        ii += 4

    for i in range(1, ii + 1):
            
        tipoDia = checkDiaHabil(fechaCalculo)
        #print(f"TIPO DIA for {fechaCalculo.strftime('%Y-%m-%d')}: {tipoDia}")
        if tipoDia == "HABIL":
            pass
        else:
            #add one day to fechaCalculo
            fechaCalculo += timedelta(days=1)
            auxLibres += 1
        fechaCalculo += timedelta(days=1)
    
    tipoDia = checkDiaHabil(fechaCalculo)
    if tipoDia != "HABIL":
        fechaCalculo += timedelta(days=1)
        auxLibres += 1
    
    
    #print(f"Fecha promesa: {fechaCalculo.strftime('%Y-%m-%d')}")
    return fechaCalculo
        

    
    

# Example usage
calculoFechaPromesa()