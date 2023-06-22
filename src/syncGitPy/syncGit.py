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

# Constante

PUSH = "push"

PULL = "pull"


def run(cmd: str | list[str], dossier: str) -> subprocess.CompletedProcess[str]:
    """
    Permet d'exécuter une commande shell via le module subprocess et en capturant les sorties standard en mode texte
    :param dossier: le dossier où exécuter la cmd
    :param cmd: La commande à exécuter
    :return: Le resultat de subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    """
    if isinstance(cmd, str):
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


def sync_local_remote(count: str, dossier: str, branch: str | None = None,
                      remote: str | None = None) -> str:
    """
    Permet de determiner l'action à exécuter pour synchroniser le depot local, puis execute cette action
    :param dossier: le dossier où sync
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
    if res is not None:
        return res.stdout
    else:
        return "Dépôt à jour "


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
    for fold in depot:
        fold = os.getcwd() + os.sep + fold
        sync_git_doss_thread = threading.Thread(target=sync_git_doss, args=(fold, fic_log), name=fold + "_thread")
        list_thread.append(sync_git_doss_thread)
    for t in list_thread:
        t.start()
    en_cours = all(thread.is_alive() for thread in list_thread)
    num_dots = 0
    while en_cours:
        print("Synchronisation", '.' * (num_dots + 1), ' ' * (2 - num_dots), end='\r')
        num_dots = (num_dots + 1) % 3
        time.sleep(0.1)
        en_cours = all(thread.is_alive() for thread in list_thread)
    for t in list_thread:
        t.join()
    if fic_log is not None:
        fic_log.close()
    return 0


def trouver_depot_fic_log(dossier, nom_fic_depot, nom_fic_log) -> tuple[list[str] | None, TextIO | None]:
    """
    Permet de renvoyer fic_log et la liste des dossiers en fonction des données fournit par l'utilisateur
    :param dossier: le nom du dossier à synchroniser
    :param nom_fic_depot: le nom du fichier où sont listés les dépôts
    :param nom_fic_log: le nom du fichier de log
    :return: la liste des depot et le fichier de log (None si pas de fichier)
    """
    fic_log = None
    depot = None
    if len(nom_fic_depot) > 0 and len(nom_fic_log) > 0:
        depot = lire_fic_depot(nom_fic_depot)
        with open(nom_fic_log, "w") as fic_log:
            ecrire_entete(fic_log, dossier)
    elif len(nom_fic_log) != 0:
        fic_log = open(nom_fic_log, "w")
    elif len(nom_fic_depot) != 0:
        depot = lire_fic_depot(nom_fic_depot)
    if len(nom_fic_depot) == 0:
        depot = trouver_depot(dossier)
    return depot, fic_log


def lire_fic_depot(fic_depot: str) -> list[str]:
    with open(fic_depot, "r") as fic_depot:
        depot = fic_depot.readlines()
    return depot


def sync_git_doss(fold: str, fic_log: TextIO | None):
    """
    Permet de synchroniser un dossier
    :param fic_log: Le fichier de Log (par défaut None)
    :param fold: Le chemin vers le dossier (absolue ou relatif)
    """
    fold = fold.strip()
    os.chdir(fold)
    branch, count, remote = trouver_branch_count_remote(fold)
    log = sync_local_remote(count, fold, branch, remote)
    if fic_log is not None:
        fic_log.write(fold + " :\n")
        fic_log.write(log + "\n")
    else:
        print(fold + " :")
        print(log)


def trouver_branch_count_remote(dossier: str) -> tuple[str, str, str]:
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


def trouver_depot(dossier) -> list[str]:
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
