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
import subprocess
from datetime import datetime
from typing import TextIO

import progressbar

# Constante

PUSH = "push"

PULL = "pull"


def run(cmd: str) -> subprocess.CompletedProcess[str]:
    """
    Permet d'exécuter une commande shell via le module subprocess et en capturant les sorties standard en mode texte
    :param cmd: La commande à exécuter
    :return: Le resultat de subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    """
    cmd = cmd.split()
    result = subprocess.run(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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


def push_pull(action: str, branch: str = None, remote: str = None) -> subprocess.CompletedProcess[str]:
    """
    Permet de pousser le depot local vers le depot distant
    :param action: L'action à réaliser, push ou pull
    :param branch: la branche à pousser
    :param remote: le nom du depot distant
    :return: le resultat de la commande
    :raises ValueError : si seulement la branche ou seulement la remote sont fournies
    """
    if branch is None:
        res = run("git " + action + " --all")
    elif remote is not None:
        res = run("git " + action + " " + remote + " " + branch)
    else:
        raise ValueError("Si une branche est fournie, alors une remotes doit l'être aussi")
    return res


def sync_local_remote(count: str, fic_log: TextIO | None, branch: str | None = None,
                      remote: str | None = None) -> None:
    """
    Permet de determiner l'action à exécuter pour synchroniser le depot local, puis execute cette action
    :param fic_log: Le fichier de log.
    :param remote: Le nom de la remote du Git
    :param count: Le resultat de la fonction count
    :param branch: La branche local courant du Git
    """
    res = None
    indice = len(count) - 1
    if count != "0 0":
        if count[0] != '0' and count[indice] == '0':
            res = push_pull(PULL, branch, remote)
        elif count[indice] != '0' and count[0] == '0':
            res = push_pull(PUSH, branch, remote)
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


def trouver_branch() -> str:
    """
    Permet de trouver la branch courant du depot
    :return: la branch courant
    """
    cmd_branch = "git rev-parse --abbrev-ref HEAD"
    cmd_branch = cmd_branch.split()
    branch = subprocess.run(cmd_branch, stdout=subprocess.PIPE, text=True)
    branch = branch.stdout.strip()
    return branch


def trouver_upstream(branch: str) -> str:
    """
    Permet de trouver l'upstream de la branche fournie en paramètre
    :param branch: la branche
    :return: l'upstream
    """

    upstream = subprocess.run(cmd_upstream, stdout=subprocess.PIPE, text=True)
    upstream = upstream.stdout.strip()
    return upstream


def trouver_count(upstream: str) -> str:
    """
    Permet de savoir si upstream est en avance, en retard ou au meme niveau que le dépôt local
    :param upstream: Upstream à comparer avec le depot local
    :return: "0 0" si le depot local est à jour, "0 X" s'il est en retard et "X 0" s'il est en avance
    """
    cmd_count = ("git rev-list --count --left-right " + upstream + "...HEAD").split()
    count = subprocess.run(cmd_count, stdout=subprocess.PIPE, text=True)
    count = count.stdout.replace("\t", " ")
    count = count.strip()
    return count


def close_fic(flog: TextIO):
    """
    Permet de fermer un fichier logique
    :param flog: le fichier logique à fermer
    """
    flog.close()


def sync_git_liste_dossier(dossier: str, nom_fic_depot: str, nom_fic_log: str = "") -> int:
    """
    Permet de synchroniser des dépôts git locaux avec leur remote
    :param dossier: Le dossier parent du (des) dépôt(s) à synchroniser
    :param nom_fic_depot: le chemin du fichier contenant la liste des dossiers où sont stockés les dépôts
    :param nom_fic_log: Le chemin du fichier où écrire les logs
    :return: 0 si exécution s'est bien passée
    """
    if len(nom_fic_depot) > 0 and len(nom_fic_log) > 0:
        fic_log, fic_depot = ouvrir_fic(nom_fic_depot, nom_fic_log)
        depot = lire_fic_depot(fic_depot)
        ecrire_entete(fic_log, dossier)
    elif len(nom_fic_log) < 1:
        fic_depot = open(nom_fic_depot, "r")
        depot = lire_fic_depot(fic_depot)
        fic_log = None
    else:
        raise ValueError("Un nom de fichier avec les depot à synchroniser doit être fournit")
    os.chdir(dossier)
    progress_bar = init_progress_bar(depot)
    for fold in depot:
        sync_git_doss(fold, fic_log)
        progress_bar.update(progress_bar.value + 1)
    close_fic(fic_log)
    return 0


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
    branch, count, remote = trouver_branch_count_remote()
    sync_local_remote(count, fic_log, branch, remote)
    print(fold)
    os.chdir("..")


def trouver_branch_count_remote():
    """
    Permet de trouver le branch courante, la remote du git et l'écart entre branche local et la remote
    :return: branch: la branche, count: l'écart entre la branch locale et distante, remote: la remote du Git
    """
    branch = trouver_branch()
    upstream = trouver_upstream(branch)
    remote = upstream.split("/")[0]
    git_fetch(remote)
    count = trouver_count(upstream)
    return branch, count, remote


def git_fetch(remote):
    """
    Permet de fetch la remote passée en paramètre
    :param remote: la remote à fetch
    """
    subprocess.run(["git", "fetch", remote])
