import json
import os
from pathlib import Path

def search_restriccion(marca, modelo, file_path=None):
   
    if file_path is None:
        base_dir = Path(__file__).resolve().parent
        file_path = os.path.join(base_dir, 'suraMarcasLin.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Create the target string by concatenating marca and modelo
        target = f"{marca}{modelo}".upper()
        
        # Search in the JSON data
        for entry in data:
            if f"{entry['MARCA']}{entry['LINEA']}".upper() == target:
                return entry.get('RESTRICCION', None)

        # If not found, return None
        return None

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the file format.")
        return None

def search_idChasis(marca, modelo, file_path=None):
   
    if file_path is None:
        base_dir = Path(__file__).resolve().parent
        file_path = os.path.join(base_dir, 'suraMarcasLin.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Create the target string by concatenating marca and modelo
        target = f"{marca}{modelo}".upper()
        
        # Search in the JSON data
        for entry in data:
            if f"{entry['MARCA']}{entry['LINEA']}".upper() == target:
                
                print("entry.get('COD.1', None): ", entry.get('COD.1', None))
                return entry.get('COD.1', None)

        # If not found, return None
        return None

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the file format.")
        return None


def obtenerPorcentaje(idChasis):
    print ("OBtener porcentaje - idChasis: ", idChasis)
    porcentajes = {
        "01": "4%",
        "02": "-3%",
        "05": "6%"
    }

    return porcentajes.get(idChasis, None)  # Return None if no matching idChasis is found
