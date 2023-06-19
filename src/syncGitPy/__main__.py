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

from src.syncGitPy.syncGit import sync_git_liste_dossier


def main():
    parser = argparse.ArgumentParser(prog="SyncGit",
                                     description="Permet de synchroniser les gits locaux et distant",
                                     epilog="Copyright (c) 2023 - Guillaume Baron")

    parser.add_argument("dossier", metavar="DOSS")
    parser.add_argument("--fic_dossier", metavar="FIC_DOSS", required=False)
    parser.add_argument("--fic_log", required=False)
    res = parser.parse_args()
    sync_git_liste_dossier(res.dossier)


if __name__ == "__main__" :
    main()