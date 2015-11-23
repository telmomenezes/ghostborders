import json


class Config:
    def __init__(self, file_path):
        with open(file_path) as data_file:    
            self.data = json.load(data_file)
