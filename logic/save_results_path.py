class SaveFilePath(): 
    def WriteFile(self, path): 
        file = open("parameters.txt", "w")
        file.write(path)
        file.close()        

    def ReadFile(self):
        file = open("parameters.txt", "r")
        content = file.read()
        return content
