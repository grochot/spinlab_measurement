
import json 
class SaveParameters(): 

    def __init__(self): 
        pass
           
    def WriteFile(self, data): 
        json_object = json.dumps(data, indent=4)
        with open("parameters.json", "w") as outfile:
            outfile.write(json_object)     

    def ReadFile(self):
        with open('parameters.json', 'r') as openfile:
            json_object = json.load(openfile)
        return json_object
    
