import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Initial config file")
parser.add_argument("output", help="Translated output config")
parser.add_argument("-d", "--debug", help="Enable debuging to console",action="store_true")
#parser.add_argument("-s", "--save", help="Save mapping for future use")
#parser.add_argument("-m", "--map", help="Load existing map")
print()

args = parser.parse_args()
config = []
int_index = []
interfaces = []
old_int = []
new_int = []

def discover(config):
	for index, line in enumerate(config):
		if line.strip().startswith("interface "):
			int_index.append(index)
			if args.debug:
				print("new index: " + str(index))

try:
	infile = open(args.input, "r")
	if infile.mode == "r":
		config = infile.readlines()
	else:
		raise Exception("Not this one chief: input file")
except Exception as e:
	print("Error opening input file")
	if args.debug:
		print()
		print(e)

if args.debug:
	print(config)
	print()
discover(config)
for ints in int_index:
	old_int.append(config[ints])
	print("Old interface: ")
	print(config[ints])
	answer = input("new Interface: ")
	if answer.startswith("pass"):
		continue
		new_int.append("pass")
	else:
		config[ints] = "interface " + answer + "\r\n"
		new_int.append("interface " + answer + "\r\n")
print(config)
mapping = dict(zip(old_int, new_int))
if args.debug:
	print("Map: ")
	print(mapping)
try:
	outfile = open(args.output, "w")
	if outfile.mode == "w":
		outfile.writelines(config)
	else:
		raise Exception("Not this one chief: outputfile")
except Exception as e:
	print("Error opening output file")
	if args.debug:
		print()
		print(e)