class VirtualMachine:
    '''
    Interface for emulating a simple vm running on top of mindustry microprocessor
    with stack and functions support
    '''
    def __init__(self):
        self.stack = Stack(self)
        self.vtable = VTable(self)

        self._debug = False

        self.source = [] #stores whole source once has been all computed

        self.sysfunc = ['print','printflush']
        
    def print(self):
        self.stack.print()
    
    def openBlock(self):
        self.stack.pushJump()
    
    def closeBlock(self):
        return self.stack.popJump()
    
    def encode(self, code:str, line = None):
        if self.stack.getContext() == None:
            print("ERROR: Empty stack found!!!")
        else:
            self.stack.encodeOnLocalBlock(code, line)
    
    def funcall(self,fname,fparams=None):
        self.vtable.funcall(fname,fparams)
    
    def flushBlock(self,block):
        self.source.extend(block.getSource())

    #flush stack generated code to source
    def flush(self):
        block = self.stack.pop()
        self.source.extend(block.getCode(0))

    def getSource(self):
        self.flush()
        return '\n'.join(self.source)
    
    def debug(self,t,s):
        out = ""
        if(self._debug):
            out += s
            if(len(t)>1):
                out+="\t\t\t" + str(t[1])
            print(out)

class Block:
    '''
    Structure representing a code block
    '''
    def __init__(self,vmi):
        self.vmi = vmi
        self.code = []
        self.varTranslation = []
    
    def getSize(self):
        return len(self.code)

    def getCode(self, offset):
        return self.code
    
    def translateVariable(self, vfrom, vto):
        if [vfrom, vto] in self.varTranslation:
            return
        self.varTranslation.append([vfrom,vto])
    
    def encode(self, code, line):
        if line == None:
            self.code.append(code)
        else:
            if len(self.code)>=line:
                self.code[line-1] = code
            else:
                print("ERROR: can't recode asm at line: ", line)
    
    def __str__(self):
        out = "---CODE BLOCK---\n"
        for i in range(len(self.code)):
            out += str(i) + "| " + self.code[i] + "\n"
        return out
    
    
class VTable:
    '''
    Manages a function virtual table, bindings function name
    to definition address.
    Handles also builtin system functions.
    '''
    def __init__(self, vmi):
        self.vmi = vmi
        self.functions = []

    def addFunctionToVTable(self, name:str, params:[]):
        self.functions.append([name, params, -1])
    
    def funcall(self,fname,params=None):
        params = params.split()
        if fname == "print":
            self.vmi.encode("print {}".format(params[0]))
        elif fname == "flush":
            self.vmi.encode("printflush {}".format(params[0]))
        elif fname == "test":
            self.vmi.encode("test {}".format(" ".join(params)))

class Stack:
    '''
    Simulates a complete stack with variable translation
    for function calling and recursion.
    '''
    def __init__(self, vmi):
        self.vmi = vmi
        self.stack = []
        self.currentStack = -1

        self.push()
        
        self.tempList = [] # used to provide temp variables to vm
        self.jumpList = [] # used to execute if / while / for ...

    def pushJump(self):
        self.jumpList.append(self.getContext().getSize()) #append line number
    
    def popJump(self):
        return self.jumpList.pop()

    def requestTempVar(self):
        i = 0
        while "tempopvar"+str(i) in self.tempList:
            i += 1
        varname = "tempopvar"+str(i)
        self.tempList.append(varname)
        return varname

    def releaseTempVar(self, varname):
        if not varname in self.tempList:
            return

        self.tempList.remove(varname)

    def getContext(self):
        if self.currentStack <0:
            return None
        return self.stack[self.currentStack]
    
    def getDepth(self):
        return self.currentStack+1

    def addVariable(self, name:str, value):
        pass #FIXME

    def encodeOnLocalBlock(self, code, line = None):
        self.getContext().encode(code, line)

    #push new variable stack block
    def push(self):
        b = Block(self.vmi)
        self.stack.append(b)
        self.currentStack += 1
    
    #remove upper variable block
    def pop(self):
        self.currentStack -= 1
        return self.stack.pop()
    
    def print(self):
        for i in self.stack:
            print(i)

#instantiate just one vm
_vm = VirtualMachine()