import sys 
import os
import json 

class SaveFilePath(): 

    def get_executable_path(self):
        if getattr(sys, 'frozen', False):
            # Jeśli jest to wersja skompilowana przez PyInstaller
            return os.path.dirname(sys.executable)+"/logic"
        else:
            # Jeśli jest to wersja uruchamiana z kodu źródłowego
            return os.path.dirname(os.path.abspath(__file__))

   

    def WriteFile(self, path): 
        # Znajdź lokalizację pliku exe
        executable_path = self.get_executable_path()

         # Stwórz nazwę pliku logów
        parameters_file_path = os.path.join(executable_path, 'parameters.json')
        with open(parameters_file_path, 'r') as openfile:
            json_object = json.load(openfile)
            json_object['path'] = path
        with open(parameters_file_path, "w") as outfile:
            outfile.write(json_object)        

    def ReadFile(self):
        #Znajdź lokalizację pliku exe
        executable_path = self.get_executable_path()

        # Stwórz nazwę pliku logów
        parameters_file_path = os.path.join(executable_path, 'parameters.json')
       
        with open(parameters_file_path, 'r') as openfile:
            json_object = json.load(openfile)
        return json_object['path']
        


