# coding=UTF-8
#
#   Fichier     :   FSObject.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de la classe FSObject
#
#   Remarque    : 
#

import math

#
# Objet du système de fichier (dossier ou fichier) à supprimer / vider
#
class FSObject(object):
    
    # Est-ce un fichier ?
    def isFile(self):
        return False
    
    # Taille de l'objet (et de tout ce qu'il contient)
    #
    #   element : Nom de l'élément à analyser ou None pour le dossier courant
    #
    #   Retourne le tuple (taille en octets, nombre de fichiers, nombre de dossiers inclus)
    def sizes(self, element = "", recurse = False):
        return self.size(), self.files(), 0

    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        pass

    # Nombre de fichier(s) contenus
    #   Retourne un entier
    def files(self):
        return 0

    # Représentation d'une taille (en octets)
    #   Conversion int -> str
    #
    #   size : Taille en octets à convertir
    #
    #   Retourne une chaine de caractères
    @staticmethod
    def size2String(size):
        
        if size < 0:
            size = 0

        # Unités
        sizeUnits = ["octet(s)", "ko", "Mo", "Go", "To", "Po"]
        
        # Version 3  - La plus "matheuse" et la plus ouverte aussi
        #  necessite le module math

        # on effectue un log base 1024 (= log 2 / 10)
        #   attention logn(0) n'existe pas !!!
        index = 0 if size == 0 else int(math.log(size,2) / 10) 
        if index >= len(sizeUnits) : index = len(sizeUnits) - 1 # Indice max
        return str(round(size/2**(10*index),2)) + " " + sizeUnits[index]
    
    # Gestion des pluriels ...
    #
    #   reoturne le pluriel ou le singulier d'une chaine
    #
    @staticmethod
    def count2String(typeStr, count):
        
        try:
            myStr = f"{count} {typeStr}"
            if count > 1:
                myStr+="s"
        except:
            # Par défaut on retourne rien ...
            myStr = ""

        return myStr
    
    # EOF