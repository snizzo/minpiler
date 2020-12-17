'''
interface for emulating a vm with stack and functions
'''
class VirtualMachine:
    def __init__(self):
        self.stack = Stack()

        self.code = []   #stores temp code generated from vm translation layer
        self.source = [] #stores whole source
    
    def print(self):
        self.stack.print()
    
    def encode(self, code:str):
        self.code.append(code)
    
    #flush temp code to source
    def flush(self):
        self.source.extend(self.code)

    def getSource(self):
        self.flush()
        return '\n'.join(self.source)

'''
handles functions tables
'''
class VTable:
    def __init__(self):
        self.functions = []

    def addFunctionToVTable(self, name:str, params:[]):
        self.functions.append([name, params, -1])

class Stack:
    def __init__(self):
        self.stack = []
        self.currentStack = -1

        self.push()

    def getContext(self):
        return self.stack[self.currentStack]

    def addVariable(self, name:str, value):
        self.getContext().append([name,value])

    #push new variable stack block
    def push(self):
        self.stack.append([])
        self.currentStack += 1
    
    #remove upper variable block
    def pop(self):
        self.stack.pop()
        self.currentStack -= 0
    
    def print(self):
        for i in self.stack:
            print(i)

#instantiate just one vm
_vm = VirtualMachine()