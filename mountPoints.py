#!/bin/python3

# coding=UTF-8
#
#   Fichier     :   mountPoints.py
#
#   Auteur(s)   :   Andrea Francia Trivolzio & JHB
#
#   Description :   Liste de points de mountage disposant d'une poubelle
#
#   Remarque    :   Basé sur trash-cli par Andrea Francia Trivolzio(PV) Italy
#
#   Dépendances :   Nécessite python-psutil (apt-get install / dnf install)
#
#   Exemple d'usage pour l'utilisateur courant
#
#       mmyList = mountPointTrashes(os.getuid())
#       for fs in myList:
#           print(fs)

import os
try:
    import psutil
except ModuleNotFoundError:
    print("Erreur - Le module 'psutil' n'a pu être importé")
    exit(1)

# Liste des points montage 
#   
#   Generator - "retourne" les dossiers existants
#
def mountPointTrashes(id, display = False):
    fstypes = [
        'cifs', # JHB : for old time kernels allowing CIFS & Samba < 2 compatibility ...
        'nfs',
        'nfs4',
        'p9', # file system used in WSL 2 (Windows Subsystem for Linux)
        'btrfs',
        'fuse', # https://github.com/andreafrancia/trash-cli/issues/250
        'fuse.glusterfs', #https://github.com/andreafrancia/trash-cli/issues/255
        'fuse.mergerfs',
    ]

    fstypes += set([p.fstype for p in psutil.disk_partitions()])
    partitions = Partitions(fstypes)
    for p in psutil.disk_partitions(all=True):
        trashDir = os.path.join(p.mountpoint, f".Trash-{id}")
        if os.path.isdir(trashDir) and \
                partitions.shouldUsedAsTrash(p, display):
            yield trashDir

# La partition peut-elle accueillir une poubelle ?
#
class Partitions:
    def __init__(self, physical_fstypes):
        self.physical_fstypes = physical_fstypes

    def shouldUsedAsTrash(self, partition, display = False):
        if display : print(f"Mount : {partition.mountpoint} - type : {partition.fstype}")
        if ((partition.device, partition.mountpoint,
             partition.fstype) ==
                ('tmpfs', '/tmp', 'tmpfs')):
            return True
        return partition.fstype in self.physical_fstypes

if '__main__' == __name__ :
    myList = mountPointTrashes(os.getuid(), True)
    for fs in myList:
        print(fs)

# EOF