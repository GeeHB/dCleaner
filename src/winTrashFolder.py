#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   winTrashFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet winTrashFolder pour la modélisation de la poubelle Windows
#
#   Remarque    :
#
from typing import override

import parameters
from basicFolder import basicFolder


#
# Objet du système de fichier (dossier ou fichier) à supprimer / vider
#
class winTrashFolder(basicFolder):

    # Taille en octets (ou None en cas d'erreur)
    @override
    def size(self)->int:
        # Pas de connaissance de la taille
        return 0

    # Nombre de fichier(s) contenu(s)
    @override
    def files(self)->int:
        # Pour être certain de lancer le nettoyage
        return 1

    # Taille du dossier (et de tout ce qu'il contient)
    #
    #   element : Nom du dossier à analyser ou None pour le dossier courant
    #
    #   Retourne le tuple (taille en octets, nombre de fichiers, nombre de dossiers inclus)
    @override
    def sizes(self, element:str = "", recurse:bool = False)->tuple[int,int,int]:
        return 0, self.files(), self.size()

    # Constructeur
    #
    def __init__(self, options:parameters.options, pMaxSize:int = 0):
        super().__init__(options, pMaxSize)

    # Initalisation
    #
    #   name : Nom du dossier (ou None si dossier 'vierge')
    #
    #  Retourne le tuple (Ok? , message d'erreur)
    @override
    def init(self, name : str | None = None):
        if parameters.WINDOWS_TRASH !=  name:
            return False, f"{name} n'est pas un dossier de poubelle Windows"

        # Ok
        self.name_: str = name if name is not None and len(name)>0 else ""
        self.valid_ : bool= True
        return True, ""

# EOF
