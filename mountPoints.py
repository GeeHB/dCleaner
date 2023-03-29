# coding=UTF-8
#
#   Fichier     :   mountPoints.py
#
#   Auteur      :   JHB
#
#   Description :   Liste de points de mountage disposant d'une poubelle
#
#   Remarque    : Basé sur trash-cli par Andrea Francia Trivolzio(PV) Italy
#
#   Exemple d'usage pour l'utilisateur courant
#
#       mmyList = mountPointTrashes(os.getuid())
#       for fs in myList:
#           print(fs)

import os.path

# Liste des points montage 
#   
#   Generator - "retourne" les dossiers existants
#
def mountPointTrashes(id):
    import psutil
    fstypes = [
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
                partitions.shouldUsedAsTrash(p):
            yield trashDir

# La partition peut-elle accueillir une poubelle ?
#
class Partitions:
    def __init__(self, physical_fstypes):
        self.physical_fstypes = physical_fstypes

    def shouldUsedAsTrash(self, partition):
        if ((partition.device, partition.mountpoint,
             partition.fstype) ==
                ('tmpfs', '/tmp', 'tmpfs')):
            return True
        return partition.fstype in self.physical_fstypes

#