import argparse

from syncGit import sync_git_liste_dossier

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="SyncGit",
                                     description="Permet de synchroniser les gits locaux et distant",
                                     epilog="Copyright (c) 2023 - Guillaume Baron")

    parser.add_argument("dossier", metavar="DOSS")
    parser.add_argument("--fic_dossier", metavar="FIC_DOSS", required=False)
    parser.add_argument("--fic_log", required=False)
    res = parser.parse_args()
    sync_git_liste_dossier(res.dossier)
