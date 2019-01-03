import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Initial config file")
parser.add_argument("output", help="Translated output config")
parser.add_argument("-d", "--debug", help="Enable debuging to console",action="store_true")
parser.add_argument("-s", "--save", help="Save mapping for future use")
parser.add_argument("-m", "--map", help="Load existing map")
print()

args = parser.parse_args()
config = []
int_index = []
old_int = []
new_int = []
stripped_map = {}

def discover(config):
	for index, line in enumerate(config):
		if line.strip().startswith("interface "):
			int_index.append(index)
			if args.debug:
				print("func discover(config): new interface discovered: " + str(config[index].strip()))
				print("func discover(config): new interface discovered at idx: " + str(index))

def open_config():
	if args.debug:
		print("func open_config(): attempting to open file at: " + args.input)
	try:
		infile = open(args.input, "r")
		config = infile.readlines()
		infile.close()
	except Exception as e:
		print("Error reading input file!")
		print(e)
		if args.debug:
			print("error in open_config()")
			print(repr(e))
	if args.debug:
		print("Configuration recieved successfully!")
		print("Dumping config to console:")
		print(config)
		print()
	return config
def save_config():
	if args.debug:
		print("func save_config(): attempting save to file: " + args.output)
	try:
		outfile = open(args.output, "w+")
		outfile.writelines(config)
		outfile.close()
	except Exception as e:
		print("Error writing config")
		print(e)
		if args.debug:
			print("error in save_config()")
			print(repr(e))
def trans_config():
	if args.debug:
		print("func trans_config(): stripped_map = " + str(stripped_map))
	for idx in int_index:
		if config[idx].strip() in stripped_map:
			print("Discovered interface inside existing map!")
			print(config[idx].strip() + " -> " + stripped_map.get(config[idx].strip())) 
			config[idx] = stripped_map.get(config[idx].strip()) + "\r\n"
		else:
			print("New interface discovered!")
			old_int.append(config[idx].strip())
			answer = input("Enter new interface name or pass for passthru: interface ").strip()
			if answer.lower().startswith("pass"):
				new_int.append(config[idx].strip())
			else:
				config[idx] = "interface " + answer + "\r\n"
				new_int.append("interface " + answer)
	if args.debug:
		print("func trans_config(): old_int: " + str(old_int))
		print("func trans_config(): new_int: " + str(new_int))
def save_map():
	if args.debug:
		print("func save_map(): attempting to save map at file: " + args.save)
	try:
		mapping = str(dict(zip(old_int, new_int)))
		mapfile = open(args.save, "w+")
		mapfile.write(mapping)
		mapfile.close()
	except Exception as e:
		print("Error saving map file")
		print(e)
		if args.debug:
			print("error in save_map()")
			print(repr(e))
def load_map():
	stripped_map = None
	if args.debug:
		print("func load_map() attempting to open map at file: " + args.map)
	try:
		mapfile = open(args.map, "r")
		map = mapfile.read()
		if args.debug:
			print("func load_map(): raw map text: " + map)
		stripped_map = eval(map)
	except Exception as e:
		print("Error openening map")
		print(e)
		if args.debug:
			print("Error in load_map()")
			print(repr(e))
	if not stripped_map:
		if args.debug:
			print("func load_map(): error loading map")
		return {}
	if args.debug:
		print("func load_map(): stripped_map: " + str(stripped_map))
	return stripped_map

config = open_config()
discover(config)
if args.map:
	stripped_map = load_map()
trans_config()
save_config()
if args.save:
	save_map()
