# ******************************************************************************
#  Copyright (c) 2023. Guillaume Baron
#
#  SyncGit - Le script python pour synchroniser les dépôt git
#
#  SyncGit is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#   Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SyncGit program is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with this
#  program. If not, see <https://www.gnu.org/licenses/>.
# ******************************************************************************
import argparse
import json
import pathlib

srcPath = str(pathlib.Path(__file__).parent.resolve()) + "/"

with open(srcPath + "fr-fr.json") as jsonFile:
    txtData = json.load(jsonFile)


def create_parser():
    args_parser = argparse.ArgumentParser(prog=txtData["prog"],
                                          description=txtData["description"],
                                          epilog=txtData["epilog"])
    args_parser.add_argument(txtData["arg1"]["name"], metavar=txtData["arg1"]["metavar"], help=txtData["arg1"]["help"])
    args_parser.add_argument(txtData["arg2"]["name"], txtData["arg2"]["short_name"], metavar=txtData["arg2"]["metavar"],
                             help=txtData["arg2"]["help"]
                             )
    args_parser.add_argument(txtData["arg3"]["name"], txtData["arg3"]["short_name"], metavar=txtData["arg3"]["metavar"],
                             help=txtData["arg3"]["help"])
    return args_parser
