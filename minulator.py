import argparse

argParser = argparse.ArgumentParser(description='Handle parsing')
argParser.add_argument('-i', action="store", dest="input", default=False)
results = argParser.parse_args()

inputPath = results.input
code = open(inputPath, 'r').readlines()

#cleaning newlines
for i in range(0,len(code)):
    code[i] = code[i].rstrip('\n')

variables = []

class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return "Variable("+self.name+":"+str(self.value)+")"
    
    def __repr__(self):
        return "Variable("+self.name+":"+str(self.value)+")"

def emulate(code):
    for i in range(0,len(code)):
        line = code[i]
        words = line.split(" ")
        if len(words)==0:
            continue
        # set op
        if(words[0]) == "set":
            
            variables.append(Variable(words[1], words[2]))
        # add
        elif (words[0]) == "add":
            variables.append(Variable(words[1], words[2]))
            

emulate(code)
print(variables)