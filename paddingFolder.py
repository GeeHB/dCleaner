# coding=UTF-8
#
#   Fichier     :   paddingFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet paddingFolder
#                   Cet objet modélise le dossier de "remplissage" dans lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
#   Version     :   0.1.5
#
#   Date        :   20 février 2020
#

import os, random, datetime, math, shutil, time
from colorizer import colorizer, backColor, textColor, textAttribute    # Pour la coloration des sorties terminal

# Motif aléatoire
#

# Caractères utilisés pour l'encodage
BASE_STRING = "ABCDEFGKHIJLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/!=@&_-:;,?<>$"

# Taille d'un motif aléatoire
MIN_PATTERN_LEN = 33
MAX_PATTERN_LEN = 5121

# Taille d'un fichier (en k-octets)
MIN_FILESIZE = 1           # 1ko
MAX_FILESIZE = 54272       # 53Mo

# Durées d'attente en secondes
MIN_ELPASE_FILES = 1    # Entre la gestion de deux fichiers
MIN_ELAPSE_TASKS = 900  # Entre 2 tâches

# Classe paddingFolder - un dossier de remplissage
#
class paddingFolder:

    # Données membres
    color_ = None                       # Colorisation du texte
    valid_ = False                      # L'objet est-il correctement initialisé ?
    currentFolder_ = ""                 # Dossier dans lequel seront générés les fichiers
    maxPatternSize_ = MAX_PATTERN_LEN   # Taille maximale du motif aléatoire
    elapseFiles_ = 0                    # Attente entre le traitement de 2 fichiers
    elapseTasks_ = 0                    # Attente entre deux traitements

    files_ = 0  # Nombre de fichiers générés

    # Constructeur
    def __init__(self, folder, color, pMaxSize = 0, elapseFiles = MIN_ELPASE_FILES, elapseTasks = MIN_ELAPSE_TASKS):
        # Initialisation des données membres
        self.color_ = color
        self.currentFolder_ = folder
        self.maxPatternSize_ = pMaxSize if (pMaxSize > MIN_PATTERN_LEN and pMaxSize < MAX_PATTERN_LEN) else MAX_PATTERN_LEN
        self._valid = False
        self.elapseFiles_ = elapseFiles
        self.elapseTasks_ = elapseTasks

    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self):

        # Initialisation du générateur aléatoire
        random.seed()

        # Ouverture / création du dossier de travail
        if 0 == len(self.currentFolder_):
            return False, "Erreur de paramètres"

        #print("Ouverture du dossier", self.currentFolder_)

        # Le dossier existe t'il ?
        if False == os.path.isdir(self.currentFolder_):
            print("Le dossier", self.currentFolder_, "n'existe pas")

            # On essaye de le créer
            try:
                os.makedirs(self.currentFolder_)
            except:   
                return False, "Impossible de créer le dossier " + self.currentFolder_
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
    # Nom du dossier courant
    def name(self):
        return self.currentFolder_

    # Temps d'attente
    def elapseFiles(self):
        return self.elapseFiles_

    def elapseTasks(self):
        return self.elapseTasks_
    

    # Usage du disque (de la partition sur laquelle le dossier courant est situé)
    #   Retourne le tuple (total, used, free)
    def partitionUsage(self):
        if True == self.valid_:
            total, used, free = shutil.disk_usage(self.currentFolder_)
            return total, used, free
        else:
            return 0,0,0

    # Contenu du dossier
    #   retourne le contenu du dossier
    def content(self):
        return 0

    # Génération d'un fichier
    #   retourne le tuple (nom du fichier crée, taille en octets, taille du motif aléatoire)
    def newFile(self, fileSize = 0):
        currentSize = 0
        if True == self.valid_:

            # Si la taille est nulle => on choisit aléatoirement
            if 0 == fileSize:
                fileSize = 1024 * random.randint(MIN_FILESIZE, MAX_FILESIZE)

            # Un nouveau fichier ...
            name = self._newFileName()

            # Le motif
            pattern = self._newPattern()
            pSize = len(pattern)

            # Taille du buffer
            buffSize = pSize if pSize < fileSize else fileSize

            try:
                # Ouverture du fihcier
                file = open(os.path.join(self.currentFolder_ ,name), 'w')
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

    # Remplissage avec un taille totale à atteindre ...
    #   Retourne un booléen indiquant si l'opération a pu être effectuée
    def newFiles(self, expectedFillSize):
        if True == self.valid_ and expectedFillSize > 0:
            print("Demande de remplissage de", self.displaySize(expectedFillSize))

            # Rien n'a été fait !!!
            still = expectedFillSize
            totalSize = 0
            files = 0
            cont = True
            
            while totalSize < expectedFillSize and cont:
                res = self.newFile()

                if 0 == res[1]:
                    # Erreur ...
                    cont = False
                else:
                    print("  + " + res[0] + " - " + self.displaySize(res[1]) + " / " + self.displaySize(still))
                    totalSize+=res[1] # Ajout de la taille du fichier
                    still-=res[1]
                    files+=1

                    # On attend ...
                    time.sleep(self.elapseFiles_)

            # Terminé
            print("Remplissage de", self.displaySize(totalSize), " -", str(files),"fichiers crées")
            return True
        
        # Erreur
        return False

    # Suppression d'un fichier (le nom doit être complet)
    #   retourne le tuple (nom du fichier, nombre d'octets libérés) ou ("" , 0) en cas d'erreur
    def deleteFile(self, name = ""):
        if True == self.valid_:
            # Pas de nom ?
            if 0 == len(name):
                # On supprime le premier qui vient ...
                name = ""
                for file in os.listdir(self.currentFolder_):
                    fName = os.path.join(self.currentFolder_, file)
                    
                    # Un fichier ?
                    if self._fileExists(fName):
                        name = fName
                        break

            # Le fichier doit exister
            if self._fileExists(name):
                try:
                    size = os.path.getsize(name)
                    os.remove(name)
                    #print("Suppression de", name, " - ", self.displaySize(size))
                    
                    # On retourne le nom court
                    values = os.path.split(name)
                    return values[1], size
                except:
                    #print("Erreur lors de la tentative de suppression de", name)
                    pass 

        # Rien n'a été fait
        return "", 0

    # Suppression d'un ou plusieurs fichiers sur un critère de nombre ou de taille à libérer
    #   retourne True lorsque l'opération s'est déroulée correctement
    def deleteFiles(self, count = 0, size = 0):
        
        tSize = 0
        tFiles = 0
        
        if True == self.valid_:
            # Il y a quelques choses à faire ....
            if not 0 == count or not 0 == size:
                
                if not 0 == size :
                    print("Demande de suppression à hauteur de", self.displaySize(size))
                else:
                    print("Demande de suppression de " + str(count) + " fichiers")

                # On va parser le dossier ...
                try:
                    # Analyse récursive du dossier
                    for (curPath, dirs, files) in os.walk(self.currentFolder_):
                        if curPath == self.currentFolder_:
                            dirs[:]=[] # On arrête de parser
                    
                        # Les fichiers "fils"
                        for file in files:
                            fullName = os.path.join(curPath, file) 
                            res = self.deleteFile(fullName)

                            # Suppression effectuée ?
                            if res[1] > 0:
                                tFiles+=1       # Un fichier de + (de supprimé ...)
                                tSize+=res[1]   # La taille en octets

                                if 0 == size:
                                    print("  -v" + res[0] + " - " + str(tFiles) + " / " + str(count))
                                else:
                                    print("  - " + res[0] + " - " + self.displaySize(res[1]) + " / " + self.displaySize(size - tSize))

                                # Quota atteint
                                if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                                    break

                            # On attend ...
                            time.sleep(self.elapseFiles_)
                            
                            # On continue

                except:
                    # Une erreur => on arrête de suite ...
                    return False

        # Fin des traitements
        print("Suppression de", self.displaySize(tSize), " -", str(tFiles),"fichiers supprimés")
        return True

    # Vidage du dossier
    def empty(self):
        if False == self.valid_:
            return 0, "Objet non initialisé"

        count = 0

        # Vidage du dossier
        try:
            # Analyse récursive du dossier
            for (curPath, dirs, files) in os.walk(self.currentFolder_):
                if curPath == self.currentFolder_:
                    dirs[:]=[] # On arrête de parser
            
                # Les fichiers "fils"
                for file in files:
                    fullName = os.path.join(curPath, file) 
                    count+=1

                    self.deleteFile(fullName)
        except:
            return 0, "Erreur lors du vidage de "+self.currentFolder_
        
        # Dossier vide
        return count, ""

    # Taille en octet du dossier
    #   Retourn eun entier
    def size(self, folder = ""):   
        if False == self.valid_ :
            # Pas ouvert
            return 0

        total = 0
        try:
            # Par défaut, moi !
            if 0 == len(folder):
                folder = self.currentFolder_
            
            # On regarde tous les éléments du dossier
            for entry in os.scandir(folder):
                if entry.is_file():
                    # Un fichier
                    total += entry.stat().st_size
                elif entry.is_dir():
                    # Un sous dossier => appel récursif
                    total += self.size(entry.path)
        except NotADirectoryError:
            # ?
            return os.path.getsize(folder)
        except PermissionError:
            # Je n'ai pas les droits ...
            return 0
        return total

    # Representation d'une taille (en octets)
    #   Retourne une chaine de caractères
    def displaySize(self, size):
        
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
    # On s'assure qu'une valeur se trouve dans un intervalle donné
    #   retourne la valeur ou sa version corrigée
    def minMax(self, source, min, max):
        if source < min :
            source = min
        else:
            if source > max:
                source = max
        return source

    #
    # Méthodes internes
    #

    # Génération d'un motif aléatoire
    #   retourne une chaine aléatoire "lisible"
    def _newPattern(self):
        
        # Taille du motif
        patternSize = random.randint(MIN_PATTERN_LEN, self.maxPatternSize_)
        
        # Génération de la chaine
        out = ""
        maxIndex = len(BASE_STRING) - 1
        for _ in range(patternSize):
            # Valeur aléatoire
            out+=BASE_STRING[random.randint(0, maxIndex)]

        # Terminé
        return out

    # Génération d'un nom de fichier
    #   Retourne un nom unique de fichier  (le nom court est retourné)
    def _newFileName(self):
        now = datetime.datetime.now()

        name = now.strftime("%Y%m%d-%H%M%S")
        fullName = os.path.join(self.currentFolder_, name)

        # Tant qu'il existe
        count = 0
        while True == self._fileExists(fullName):
            # On génère un nouveau nom
            count+=1
            name = name + "-" + str(count)
            fullName = os.path.join(self.currentFolder_, name )
        
        return name # On retourne le nom court

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
        #except IOError as e: 
        except IOError: 
            # print("Le fichier ", self.fileName_, " n'existe pas")
            return False
        except:
            # print("Erreur lors de l'ouverture du fichier", self.fileName_)
            return False
        
        # oui
        return True

# EOF