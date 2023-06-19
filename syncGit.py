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
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from typing import TextIO

import progressbar

# Constante

PUSH = "push"

PULL = "pull"


def run(cmd: str | list[str], dossier: str) -> subprocess.CompletedProcess[str]:
    """
    Permet d'exécuter une commande shell via le module subprocess et en capturant les sorties standard en mode texte
    :param dossier: le dossier ou executer la cmd
    :param cmd: La commande à exécuter
    :return: Le resultat de subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    """
    if cmd is str:
        cmd = cmd.split()
    result = subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=dossier)
    return result


def ecrire_entete(fic_log: TextIO, dossier: str):
    """
    Permis d'écrire l'en-tête approprié dans le fichier de log
    :param dossier: Le dossier parent des dépôt
    :param fic_log: le fichier où écrire
    """
    fic_log.write("Log de syncGit pour les dépôt dans " + dossier + "\n")
    fic_log.write(str(datetime.now()))
    fic_log.write("\n\n")


def ouvrir_fic(nom_fic_depot: str, nom_fic_log: str) -> tuple[TextIO, TextIO]:
    """
    Permet d'ouvrir le fichier contenant la liste des dépôts et le fichier de log
    :param nom_fic_depot: Le nom du fichier contenant la liste des dépôts
    :param nom_fic_log: Le nom du fichier de log
    :return: un tuple avec les deux fichiers logique
    """
    _ficLog = open(nom_fic_log, "w")
    _ficDepot = open(nom_fic_depot, "r")
    return _ficLog, _ficDepot


def push_pull(action: str, dossier: str, branch: str = None, remote: str = None) -> subprocess.CompletedProcess[str]:
    """
    Permet de pousser le depot local vers le depot distant
    :param dossier: le dossier ou push/pull
    :param action: L'action à réaliser, push ou pull
    :param branch: la branche à pousser
    :param remote: le nom du depot distant
    :return: le resultat de la commande
    :raises ValueError : si seulement la branche ou seulement la remote sont fournies
    """
    if branch is None:
        res = run("git " + action + " --all", dossier=dossier)
    elif remote is not None:
        res = run("git " + action + " " + remote + " " + branch, dossier=dossier)
    else:
        raise ValueError("Si une branche est fournie, alors une remotes doit l'être aussi")
    return res


def sync_local_remote(count: str, dossier: str, fic_log: TextIO | None, branch: str | None = None,
                      remote: str | None = None) -> None:
    """
    Permet de determiner l'action à exécuter pour synchroniser le depot local, puis execute cette action
    :param dossier: le dossier où sync
    :param fic_log: Le fichier de log.
    :param remote: Le nom de la remote du Git
    :param count: Le resultat de la fonction count
    :param branch: La branche local courant du Git
    """
    res = None
    indice = len(count) - 1
    if count != "0 0":
        if count[0] != '0' and count[indice] == '0':
            res = push_pull(PULL, dossier, branch, remote)
        elif count[indice] != '0' and count[0] == '0':
            res = push_pull(PUSH, dossier, branch, remote)
    if fic_log is not None:
        if res is not None:
            fic_log.write(res.stdout)
        else:
            fic_log.write("Dépôt à jour \n\n")


def maj_info(info: dict[str, int], sync_push: bool = False, sync_pull: bool = False):
    if sync_push:
        info["sync"] += 1
    elif sync_pull:
        info["sync"] += 1
    else:
        info["à jour"] += 1


def trouver_branch(dossier) -> str:
    """
    Permet de trouver la branch courant du depot
    :return: la branch courant
    """
    cmd_branch = "git rev-parse --abbrev-ref HEAD"
    cmd_branch = cmd_branch.split()
    branch = run(cmd_branch, dossier)
    branch = branch.stdout.strip()
    return branch


def trouver_upstream(branch: str, dossier) -> str:
    """
    Permet de trouver l'upstream de la branche fournie en paramètre
    :param dossier: le dossier où trouver l'upstream
    :param branch: la branche
    :return: l'upstream
    """
    cmd_upstream = ("git rev-parse --abbrev-ref " + branch + "@{upstream}").split()
    upstream = run(cmd_upstream, dossier)
    upstream = upstream.stdout.strip()
    return upstream


def trouver_count(upstream: str, dossier: str) -> str:
    """
    Permet de savoir si upstream est en avance, en retard ou au meme niveau que le dépôt local
    :param dossier: le dossier où trouver le "count"
    :param upstream: Upstream à comparer avec le depot local
    :return: "0 0" si le depot local est à jour, "0 X" s'il est en retard et "X 0" s'il est en avance
    """
    cmd_count = ("git rev-list --count --left-right " + upstream + "...HEAD").split()
    count = run(cmd_count, dossier)
    count = count.stdout.replace("\t", " ")
    count = count.strip()
    return count


def close_fic(flog: TextIO):
    """
    Permet de fermer un fichier logique
    :param flog: le fichier logique à fermer
    """
    flog.close()


def sync_git_liste_dossier(dossier: str, nom_fic_depot: str = "", nom_fic_log: str = "") -> int:
    """
    Permet de synchroniser des dépôts git locaux avec leur remote
    :param dossier: Le dossier parent du (des) dépôt(s) à synchroniser
    :param nom_fic_depot: le chemin du fichier contenant la liste des dossiers où sont stockés les dépôts
    :param nom_fic_log: Le chemin du fichier où écrire les logs
    :return: 0 si exécution s'est bien passée
    """
    depot, fic_log = trouver_depot_fic_log(dossier, nom_fic_depot, nom_fic_log)
    os.chdir(dossier)
    list_thread: list[threading.Thread] = []
    # progress_bar = init_progress_bar(depot)
    for fold in depot:
        fold = os.getcwd() + os.sep + fold
        sync_git_doss_thread = threading.Thread(target=sync_git_doss, args=(fold, fic_log))
        list_thread.append(sync_git_doss_thread)

    for t in list_thread:
        t.start()
    en_cours = all(thread.is_alive() for thread in list_thread)

    while en_cours:
        eli_count = 0
        print("Synchronisation", '.' * (eli_count + 1), ' ' * (2 - eli_count), end='\r')
        eli_count = (eli_count + 1) % 3
        time.sleep(0.1)
        en_cours = all(thread.is_alive() for thread in list_thread)
    for t in list_thread:
        t.join()
    # progress_bar.update(progress_bar.value + 1)
    if fic_log is not None:
        close_fic(fic_log)
    return 0


def trouver_depot_fic_log(dossier, nom_fic_depot, nom_fic_log):
    """
    Permet de renvoyer fic_log et la liste des dossiers en fonction des données fournit par l'utilisateur
    :param dossier: le nom du dossier à synchroniser
    :param nom_fic_depot: le nom du fichier où sont listés les dépôts
    :param nom_fic_log: le nom du fichier de log
    :return: la liste des depot et le fichier de log (None si pas de fichier)
    """
    fic_log = None
    if len(nom_fic_depot) > 0 and len(nom_fic_log) > 0:
        fic_log, fic_depot = ouvrir_fic(nom_fic_depot, nom_fic_log)
        depot = lire_fic_depot(fic_depot)
        ecrire_entete(fic_log, dossier)
    elif len(nom_fic_log) != 0:
        fic_log = open(nom_fic_log, "w")
    elif len(nom_fic_depot) != 0:
        fic_depot = open(nom_fic_depot, "r")
        depot = lire_fic_depot(fic_depot)
    if len(nom_fic_depot) == 0:
        depot = trouver_depot(dossier)
    return depot, fic_log


def init_progress_bar(depot):
    progress_bar = progressbar.ProgressBar(redirect_stdout=True, max_value=len(depot))
    progress_bar.update(0)
    return progress_bar


def lire_fic_depot(fic_depot):
    depot = fic_depot.readlines()
    close_fic(fic_depot)
    return depot


def sync_git_doss(fold: str, fic_log: TextIO | None):
    """
    Permet de synchroniser un dossier
    :param fic_log: Le fichier de Log (par défaut None)
    :param fold: Le chemin vers le dossier (absolue ou relatif)
    """
    fold = fold.strip()
    os.chdir(fold)
    if fic_log is not None:
        fic_log.write(fold + " :\n")
    branch, count, remote = trouver_branch_count_remote(fold)
    sync_local_remote(count, fold, fic_log, branch, remote)


def trouver_branch_count_remote(dossier: str):
    """
    Permet de trouver le branch courante, la remote du Git et l'écart entre branche local et la remote
    :return: branch : la branche, count : l'écart entre la branch locale et distante, remote : la remote du Git
    """
    branch = trouver_branch(dossier)
    upstream = trouver_upstream(branch, dossier)
    remote = upstream.split("/")[0]
    git_fetch(remote, dossier)
    count = trouver_count(upstream, dossier)
    return branch, count, remote


def trouver_depot(dossier):
    os.chdir(dossier)
    list_dir = os.listdir()
    list_dossier = []
    list_dir = list(filter(os.path.isdir, list_dir))
    for doss in list_dir:
        os.chdir(doss)
        est_un_depot = [f for f in os.listdir('.') if re.match(r'.*\.git$', f)]
        if est_un_depot:
            list_dossier.append(doss)
        os.chdir("..")
    return list_dossier


def git_fetch(remote, dossier):
    """
    Permet de fetch la remote passée en paramètre
    :param dossier: le dossier où fetch
    :param remote: la remote à fetch
    """

    subprocess.run(["git", "fetch", remote], cwd=dossier)
