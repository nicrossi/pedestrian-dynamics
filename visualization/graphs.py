import os
import csv

def parse_output_file(file):
    data = {}
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_key = float(row["time"]) 
            value = {key: float(val) for key, val in row.items() if key != "time"}
            data[time_key] = value
    return data


def parse_output_files(output_folder):
    data = {}
    files = os.listdir(output_folder)
    for file in files:
        if file.endswith('.csv'):
            qin = file.split('_')[1].split('.')[0]
            data[qin] = parse_output_file(os.path.join(output_folder, file))

    return data



