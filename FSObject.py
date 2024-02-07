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

import math, os

#
# Objet du système de fichier (dossier ou fichier) à supprimer / vider
#
class FSObject(object):
    
    # Paramètres & options
    @property
    def options(self):
        return self.params_
    
    @options.setter
    def options(self, value):
        self.params_ = value

    def __init__(self, parameters):
        # Initialisations
        self.options = parameters

    # Est-ce un fichier ?
    def isFile(self):
        return False
    
    # Taille de l'objet (et de tout ce qu'il contient)
    #
    #   element : Nom de l'élément à analyser ou None pour le dossier courant    #
    #   Retourne le tuple (taille en octets, nombre de fichiers, nombre de dossiers inclus)
    def sizes(self, element = "", recurse = False):
        return self.size(), self.files(), 0

    # Taille en octets
    def size(self):
        pass

    # Nombre de fichier(s) contenus
    #   Retourne un entier
    def files(self):
        return 0
    
    # Le fichier existe t'il ?
    #
    #   fName : Nom complet du fichier à tester
    #
    @staticmethod
    def existsFile(fName):
        # Le nom est-il renseigné ?
        if fName is None or 0 == len(fName):
            return False

        # On va essayer d'ouvrir le fichier en lecture
        try:
            file = open(fName, 'r')
            file.close()
            return True
        except FileNotFoundError :
            return False
        except IOError:
            return False

    # Le dossier existe-il ?
    @staticmethod
    def existsFolder(folderName):
        # On vérifie ...
        return os.path.isdir(folderName)

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