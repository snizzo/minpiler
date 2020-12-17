'''
interface for emulating a vm with stack and functions
'''
class VirtualMachine:
    def __init__(self):
        self.stack = Stack(self)

        self.code = []   #stores temp code generated from vm translation layer
        self.source = [] #stores whole source

        self.sysfunc = ['print','printflush']
    
    def print(self):
        self.stack.print()
    
    def encode(self, code:str):
        self.code.append(code)
    
    def funcall(self,fname,fparams=None):
        self.stack.funcall(fname,fparams)

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
    def __init__(self, vmi):
        self.vmi = vmi
        self.stack = []
        self.currentStack = -1

        self.push()

    def funcall(self,fname,params=None):
        params = params.split()
        if fname == "print":
            self.vmi.encode("print {}".format(params[0]))
        elif fname == "flush":
            self.vmi.encode("printflush {}".format(params[0]))
        elif fname == "test":
            self.vmi.encode("test {}".format(" ".join(params)))

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