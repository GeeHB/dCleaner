# coding=UTF-8
#
#   File     :   basicFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet basicFolder
#                   Cet objet modélise un dossier lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
#   Version     :   0.5.2
#
#   Date        :   27 jan. 2023
#

import os, random, datetime, math
from parameters import FILESIZE_MAX, FILESIZE_MIN, PATTERN_MIN_LEN, PATTERN_MAX_LEN, PATTERN_BASE_STRING
from sharedTools.colorizer import textColor

# Classe basicFolder - un dossier de remplissage ou à vider ...
#
class basicFolder:

    # Données membres
    valid_ = False                      # L'objet est-il correctement initialisé ?
    name_ = ""                          # Nom complet du dossier
    params_ = None
    maxPatternSize_ = PATTERN_MAX_LEN   # Taille maximale du motif aléatoire
    sizes_ = None                       # Taille et # fichiers contenus

    # Constructeur
    def __init__(self, options, pMaxSize = 0):
        # Initialisation des données membres
       self._valid = False
       self.name_ = ""
       self.params_ = options
       self.maxPatternSize_ = pMaxSize if (pMaxSize > PATTERN_MIN_LEN and pMaxSize < PATTERN_MAX_LEN) else PATTERN_MAX_LEN
       size_ = None
        
    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self, name):

        self.name_ = name

        # Initialisation du générateur aléatoire
        random.seed()

        # Le dossier existe t'il ?
        if False == os.path.isdir(self.name_):
            return False, "Le dossier '" +  self.name_ + "' n'existe pas"
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
    # Nom du dossier courant
    def name(self):
        return self.name_

    # Génération d'un fichier
    #   retourne le tuple (nom du fichier crée, taille en octets, taille du motif aléatoire)
    def newFile(self, fileSize = 0, maxFileSize = 0):
        return self._pattern2File("", fileSize, maxFileSize)

    # Remplissage et renommage d'un fichier existant
    #   retourne le tuple (nom du fichier crée, taille en octets, taille du motif aléatoire)
    def fillFile(self, name):
        return self._pattern2File(name)
    
    # Suppression d'un fichier (le nom doit être complet)
    #   retourne le tuple (nom du fichier, nombre d'octets libérés) ou ("" , 0) en cas d'erreur
    def deleteFile(self, name, clearContent = True):
        size = 0
        if True == self.valid_:
            # Le fichier doit exister
            if self._fileExists(name):
                try:
                    
                    # Replacement du contenu
                    if clearContent:
                        # Nouveau nom
                        name = self._renameFile(name)

                        if len(name) > 0:
                            # Nouveau contenu (on itère l'effacement)
                            for count in range(self.params_.iterate_):
                                self._pattern2File(name)
                    
                    # Effacement
                    if len(name)>0:
                        size = os.path.getsize(name)
                        os.remove(name)
                    
                        # On retourne le nom court
                        values = os.path.split(name)
                        return values[1], size
                except:
                    if self.params_.verbose_:
                        print(self.params_.color_.colored("Erreur lors de la tentative de suppression de " + name, textColor.ROUGE))
                    pass 

        # Rien n'a été fait
        return "", size

    # Vidage du dossier
    #
    #       folder : nom complet du dossier à vider ("" => dossier courant)
    #       recurse : Vidage recursive des sous-dossiers
    #       remove : Suppression du dossier (-1 : pas de suppression; 0 : Suppression du dossier et de tous les descendants; n : suppression à partir de la profondeur n)
    #   
    #   Retourne Le tuple (# supprimé, message d'erreur / "")
    #
    def empty(self, folder = "", recurse = False, remove = -1):
        if False == self.valid_:
            return 0, "Objet non initialisé"

         # Quel dossier vider ?
        if 0 == len(folder):
            folder = self.name_

        count = 0

        # Vidage du dossier
        try:
            # Analyse récursive du dossier
            for entry in os.scandir(folder):
                if entry.is_file():
                    # Un fichier
                    fullName = os.path.join(folder, entry.name)
                    res = self.deleteFile(fullName)
                    count += 1
                elif entry.is_dir():
                    if recurse:
                        # Un sous dossier => appel récursif
                        fullName = os.path.join(folder, entry.name)
                        subCount, message = self.empty(fullName, True, remove - 1 if remove > 0 else remove)
                        
                        # Une erreur ?
                        if len(message):
                            return 0, message

                        count+=subCount
            
            # Suppression du dossier courant?
            if 0 == remove:
                os.rmdir(folder)
        except:
            return 0, "Erreur lors du vidage de "+self.params_.folder_
        
        
        # Dossier vidé
        return count, ""

    # Taille du dossier (et de tout ce qu'il contient)
    #   Retourne le tuple (taille en octets, nombre de fichiers)
    def sizes(self, folder = ""):   
        if False == self.valid_ :
            # Pas ouvert
            return 0,0

        totalSize = 0
        totalFiles = 0
        try:
            # Par défaut, moi !
            if 0 == len(folder):
                folder = self.params_.folder_
            
            # On regarde tous les éléments du dossier
            for entry in os.scandir(folder):
                if entry.is_file():
                    # Un fichier
                    totalSize += entry.stat().st_size
                    totalFiles += 1
                elif entry.is_dir():
                    # Un sous dossier => appel récursif
                    total = self.sizes(entry.path)
                    totalSize += total[0]
                    totalFiles += total[1]

        except NotADirectoryError:
            # ?
            return os.path.getsize(folder), 1
        except PermissionError:
            # Je n'ai pas les droits ...
            return 0, 0
        return totalSize, totalFiles

    # Taille en octets
    #   retourne un entier
    def size(self):
        # Déja caclculé ?
        if None == self.sizes_:
            self.sizes_ = self.sizes()
        return self.sizes_[0]

    # Nombre de fichiers
    #   Retourne un entier
    def files(self):
        # Déja caclculé ?
        if None == self.sizes_:
            self.sizes_ = self.sizes()
        return self.sizes_[1]
        
    # Représentation d'une taille (en octets)
    #   Retourne une chaine de caractères
    def size2String(self, size):
        
        if size < 0:
            size = 0

        # Unités
        sizeUnits = ["octet(s)", "ko", "Mo", "Go", "To", "Po"]
        
        # Version 3  - La plus "matheuse" et la plus ouverte aussi
        #  necessite le module math

        # on effectue un log base 1024 = log 2 / 10
        #   attention logn(0) n'existe pas !!!
        index = 0 if size == 0 else int(math.log(size,2) / 10) 
        if index >= len(sizeUnits) : index = len(sizeUnits) - 1 # Indice max
        return str(round(size/2**(10*index),2)) + " " + sizeUnits[index]
        
        """
        # Version 2 - La plus élégante
        max = len(sizeUnits) - 1    # Après on ne sait plus nommer

        # Log base 1024 ...
        while index < max and size > 1024:
            size/=1024
            index+=1
        return str(round(size,2)) + " " + sizeUnits[index]
        """

        """
        # Version 1 - Plutôt bourine (et surtout très limitée ...)

        # en octets
        if size < 1024:
            return str(round(size,2)) + " octet(s)"
        
        # en k
        size/=(2**10)
        if size < 1024:
            return str(round(size,2)) + " ko"

        # en Mo
        size/=(2**10)
        if size < 1024:
            return str(round(size,2)) + " Mo"

        # en Go
        size/=(2**10)
        if size < 1024:
            return str(round(size,2)) + " Go"

        # On s'arrête au To
        size/=(2**10)
        return str(round(size,2)) + " To"
        """

    #
    # Méthodes générales
    #

    # Le dossier existe-il ?
    def exists(self, folderName):
        if 0 == len(folderName):
            folderName = self.name_

        # On vérifie ...
        return os.path.isdir(folderName)

    #
    # Méthodes internes
    #

    # Génération d'un motif aléatoire
    #   retourne une chaine aléatoire "lisible"
    def _newPattern(self):
        
        # Taille du motif
        patternSize = random.randint(PATTERN_MIN_LEN, self.maxPatternSize_)
        
        # Génération de la chaine
        out = ""
        maxIndex = len(PATTERN_BASE_STRING) - 1
        for _ in range(patternSize):
            # Valeur aléatoire
            out+=PATTERN_BASE_STRING[random.randint(0, maxIndex)]

        # Terminé
        return out

    # Génération d'un nom de fichier (pour le dossier courant)
    #   Retourne un nom unique de fichier (le nom court est retourné)
    def _newFileName(self):
        now = datetime.datetime.now()

        name = now.strftime("%Y%m%d-%H%M%S-%f")
        fullName = os.path.join(self.name_, name)

        # Tant qu'il existe (avec le même nom)
        count = 0
        while True == self._fileExists(fullName):
            # On génère un nouveau nom
            count+=1
            name = name + "-" + str(count)
            fullName = os.path.join(self.name_, name )
        
        return name # On retourne le nom court

    ## Renomage d'un fichier
    #   Retourne le "nouveau" nom ou "" en cas d'erreur
    def _renameFile(self, file):
        if self._fileExists(file):
            

            # Nouveau nom "complet"
            res = os.path.split(file)
            name = os.path.join(res[0], self._newFileName())

            try:
                os.rename(file, name)
            except:
                # une erreur
                return file

            return name

        # sinon on retourne le nom de base
        return file

    # Le fichier existe t'il ?
    def _fileExists(self, fileName):
        # Le nom est-il renseigné ?
        if len(fileName) == 0:
            return False

        # On va essayer d'ouvrir le fichier en lecture
        try:
            file = open(fileName, 'r')

            # Le fichier existe, il est donc ouvert
            file.close()
            return True
        except IOError: 
            # print("Le fichier ", self.fileName_, " n'existe pas")
            return False
        except:
            # print("Erreur lors de l'ouverture du fichier", self.fileName_)
            return False
        
        # oui
        return True

    # Rempliisage d'un fichier
    #    retourne le tuple (nom du fichier, taille en octets, taille du motif aléatoire)
    def _pattern2File(self, fname, fileSize = 0, maxFileSize = 0):
        currentSize = 0
        if True == self.valid_:

            # Creation ?
            if 0 == len(fname):
                # Si la taille est nulle => on choisit aléatoirement
                if 0 == fileSize:
                    # 1 => ko, 2 = Mo
                    unit = 1 + random.randint(1, 1024) % 2
                    fileSize = 2 ** (unit * 10) * random.randint(FILESIZE_MIN, FILESIZE_MAX)

                    # On remplit (mais on ne déborde pas !)
                    if maxFileSize >0 and fileSize > maxFileSize:
                        fileSize = maxFileSize

                    # Génération du nom
                    name = self._newFileName()
                    os.path.join(self.params_.folder_, name)

            else:
                # Remplissage
                if False == self._fileExists(fname):
                    # Le fichier n'existe pas
                    return fname, 0, 0

                # On conserve la taille
                fileSize = os.path.getsize(fname)
                name = fname

            # Le motif
            pattern = self._newPattern()
            pSize = len(pattern)

            # Taille du buffer
            buffSize = pSize if pSize < fileSize else fileSize

            try:
                # Ouverture / création du fihcier
                file = open(fname, 'w')
            except:
                return name, 0

            try:
                # Remplissage du fichier
                while currentSize < fileSize:
                    # Ecriture du buffer
                    file.write(pattern)
                    currentSize+=buffSize

                    # Le dernier paquet doit-il être tronqué ?
                    if (currentSize + buffSize) > fileSize:
                        buffSize = fileSize - currentSize
                        pattern = pattern[:buffSize]

                # Terminé
                file.close()
            except:
                file.close()
                return name, 0, 0
        else:
            name = ""

        return name, currentSize, pSize
# EOF