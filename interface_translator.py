# Andrew Piroli
# MIT License
#
# Copyright (c) 2018-2020 AndrewPiroli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import argparse
import sys
import logging


class IntTranslate:
    def __init__(self):
        self.config = []
        self.int_index = []
        self.old_int = []
        self.new_int = []
        self.stripped_map = {}
        logging.basicConfig(format="", level=logging.DEBUG)
        self.log = logging.getLogger("IntTranslate")
        self.log.setLevel(logging.CRITICAL)

    def discover(self):
        for idx, line in enumerate(self.config):
            if line.strip().startswith("interface "):
                self.int_index.append(idx)
                self.log.debug(
                    "func discover(config): new interface discovered: "
                    + str(self.config[idx].strip())
                )
                self.log.debug(
                    "func discover(config): new interface discovered at idx: "
                    + str(idx)
                )

    def open_config(self):
        self.log.debug(
            "func open_config(): attempting to open file at: " + self.args.input
        )
        try:
            infile = open(self.args.input, "r")
            self.config = infile.readlines()
            infile.close()
        except Exception as e:
            self.log.critical("Error reading input file!")
            self.log.critical(e)
            self.log.debug("error in open_config()")
            self.log.debug(repr(e))
        self.log.debug("Configuration recieved successfully!")
        self.log.debug("Dumping config to console:")
        self.log.debug(self.config)
        self.log.debug("")

    def save_config(self):
        self.log.debug(
            "func save_config(): attempting save to file: " + self.args.output
        )
        try:
            outfile = open(self.args.output, "w+", newline="\n")
            outfile.writelines(self.config)
            outfile.close()
        except Exception as e:
            self.log.critical("Error writing config")
            self.log.critical(e)
            self.log.debug("error in save_config()")
            self.log.debug(repr(e))

    def trans_config(self):
        self.log.debug("func trans_config(): stripped_map = " + str(self.stripped_map))
        for idx in self.int_index:
            if self.config[idx].strip() in self.stripped_map:
                self.log.critical("Discovered interface inside existing map!")
                self.log.critical(
                    self.config[idx].strip()
                    + " -> "
                    + self.stripped_map.get(self.config[idx].strip())
                )
                self.config[idx] = (
                    self.stripped_map.get(self.config[idx].strip()) + "\n"
                )
            else:
                self.log.critical("New interface discovered!")
                self.old_int.append(self.config[idx].strip())
                self.log.critical(self.config[idx].strip())
                answer = input(
                    "Enter new interface name or pass for passthru: interface "
                ).strip()
                if answer.lower().startswith("pass"):
                    self.new_int.append(self.config[idx].strip())
                else:
                    self.config[idx] = "interface " + answer + "\n"
                    self.new_int.append("interface " + answer)
        self.log.debug("func trans_config(): old_int: " + str(self.old_int))
        self.log.debug("func trans_config(): new_int: " + str(self.new_int))

    def save_map(self):
        if self.args.reverse:
            self.log.critical("")
            self.log.critical("Warning!")
            self.log.critical("You have selected to reverse AND save the map!")
            self.log.critical(
                "Please confirm this is intended and the original map will not be overwritten"
            )
            if input("Is this OK (y/N): ").strip().lower().startswith("y"):
                self.log.critical("Saving map anyway!")
            else:
                self.log.critical("Map save aborted!")
                return
        self.log.debug(
            "func save_map(): attempting to save map at file: " + self.args.save
        )
        try:
            mapping = str(dict(zip(self.old_int, self.new_int)))
            mapfile = open(self.args.save, "w+", newline="\n")
            mapfile.write(mapping)
            mapfile.close()
        except Exception as e:
            self.log.critical("Error saving map file")
            self.log.critical(e)
            self.log.debug("error in save_map()")
            self.log.debug(repr(e))

    def load_map(self):
        self.stripped_map = None
        self.log.debug(
            "func load_map() attempting to open map at file: " + self.args.map
        )
        try:
            mapfile = open(self.args.map, "r")
            map = mapfile.read()
            self.log.debug("func load_map(): raw map text: " + map)
            self.security_check(map)
            self.stripped_map = eval(map)
        except AssertionError as e:
            sys.exit(e)
        except Exception as e:
            self.log.critical("Error openening map")
            self.log.critical(e)
            self.log.debug("Error in load_map()")
            self.log.debug(repr(e))
        if not self.stripped_map:
            self.log.debug("func load_map(): error loading map")
            return {}
        self.log.debug("func load_map(): stripped_map: " + str(self.stripped_map))

    @staticmethod
    def int_array_fixup(map):
        old_int = map.keys()
        new_int = map.values()
        return [old_int, new_int]

    def security_check(
        self, mapfile,
    ):  # Screen the map file because we will call eval() on it, try to prevent code injection by the user
        if any(
            [
                disallowed in mapfile
                for disallowed in [
                    "(",
                    ")",
                    "import",
                    "def",
                    "if",
                    "else",
                    "catch",
                    "=",
                    "with",
                    "as",
                ]
            ]
        ):
            raise AssertionError(
                "Security: Map file failed security check! The map file should only contain a python dictionary, NOT code."
            )
        else:
            self.log.debug("security_check(mapfile): Map pass security check.")

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("input", help="Initial config file")
        parser.add_argument("output", help="Translated output config")
        parser.add_argument(
            "-d", "--debug", help="Enable debuging to console", action="store_true"
        )
        parser.add_argument("-s", "--save", help="Save mapping for future use")
        parser.add_argument("-m", "--map", help="Load existing map")
        parser.add_argument(
            "-r", "--reverse", help="Reverse the translation map", action="store_true"
        )
        self.args = parser.parse_args()
        if self.args.debug:
            self.log.setLevel(logging.DEBUG)
        self.open_config()
        self.discover()
        if self.args.map:
            self.load_map()
            if self.args.reverse:
                if self.args.debug:
                    self.log.critical("main: reversing loaded map file")
                rev_map = {v: k for k, v in self.stripped_map.items()}
                self.stripped_map = rev_map
            fixup = self.int_array_fixup(self.stripped_map)
            self.old_int = list(fixup[0])
            self.new_int = list(fixup[1])
            fixup = None
        self.trans_config()
        self.save_config()
        if self.args.save:
            self.save_map()


if __name__ == "__main__":
    IntTranslate().main()
