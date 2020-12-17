import parserlexer
import argparse

import vm

argParser = argparse.ArgumentParser(description='Handle parsing')
argParser.add_argument('-i', action="store", dest="input", default=False)
results = argParser.parse_args()

vmi = vm._vm

inputPath = results.input

inputFile = open(inputPath)

inputData = inputFile.read()

lexer = parserlexer.lexer
parser = parserlexer.parser

parser.parse(inputData)

print(vmi.getSource())