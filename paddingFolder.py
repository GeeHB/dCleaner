# coding=UTF-8
#
#   File     :   paddingFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet paddingFolder
#                   Cet objet modélise le dossier de "remplissage" dans lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
#   Version     :   0.4.1
#
#   Date        :   29 déc. 2022
#

import os, random, datetime, math, shutil, time
import parameters
from sharedTools.colorizer import textColor

# Classe paddingFolder - un dossier de remplissage
#
class paddingFolder:

    # Données membres
    valid_ = False                      # L'objet est-il correctement initialisé ?
    params_ = None
    maxPatternSize_ = parameters.PATTERN_MAX_LEN   # Taille maximale du motif aléatoire
    elapseFiles_ = 0                    # Attente entre le traitement de 2 fichiers
    elapseTasks_ = 0                    # Attente entre deux traitements
    sizes_ = None                       # Taille (#octets et fichiers) du dossier

    files_ = 0  # Nombre de fichiers générés

    # Constructeur
    def __init__(self, options, pMaxSize = 0, elapseFiles = parameters.MIN_ELPASE_FILES, elapseTasks = parameters.MIN_ELAPSE_TASKS):
        # Initialisation des données membres
        self.params_ = options
        self.maxPatternSize_ = pMaxSize if (pMaxSize > parameters.PATTERN_MIN_LEN and pMaxSize < parameters.PATTERN_MAX_LEN) else parameters.PATTERN_MAX_LEN
        self._valid = False
        self.elapseFiles_ = elapseFiles
        self.elapseTasks_ = elapseTasks

    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self):

        # Initialisation du générateur aléatoire
        random.seed()

        # Ouverture / création du dossier de travail
        if 0 == len(self.params_.folder_):
            return False, "Erreur de paramètres"

        #print("Ouverture du dossier", self.params_.folder_)

        # Le dossier existe t'il ?
        if False == os.path.isdir(self.params_.folder_):
            if self.params_.verbose_:
                print("Le dossier '" +  self.params_.folder_ + "' n'existe pas")

            # On essaye de le créer
            try:
                os.makedirs(self.params_.folder_)

                if self.params_.verbose_:
                    print("Dossier crée avec succès")

            except:   
                return False, "Impossible de créer le dossier '" + self.params_.folder_ + "'"
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
    # Nom du dossier courant
    def name(self):
        return self.params_.folder_

    # Temps d'attente
    def elapseFiles(self):
        return self.elapseFiles_

    def elapseTasks(self):
        return self.elapseTasks_

    def wait(self, duration):
        time.sleep(duration)
    
    # Usage du disque (de la partition sur laquelle le dossier courant est situé)
    #   Retourne le tuple (total, used, free)
    def partitionUsage(self):
        if True == self.valid_:
            total, used, free = shutil.disk_usage(self.params_.folder_)
            return total, used, free
        else:
            return 0,0,0

    # Contenu du dossier
    #   retourne le contenu du dossier
    def content(self):
        return 0

    # Génération d'un fichier
    #   retourne le tuple (nom du fichier crée, taille en octets, taille du motif aléatoire)
    def newFile(self, fileSize = 0, maxFileSize = 0):
        currentSize = 0
        if True == self.valid_:

            # Si la taille est nulle => on choisit aléatoirement
            if 0 == fileSize:
                # 1 => ko, 2 = Mo
                unit = 1 + random.randint(1, 1024) % 2
                fileSize = 2 ** (unit * 10) * random.randint(parameters.FILESIZE_MIN, parameters.FILESIZE_MAX)

                # On remplit (mais on ne déborde pas !)
                if maxFileSize >0 and fileSize > maxFileSize:
                    fileSize = maxFileSize

            # Un nouveau fichier ...
            name = self._newFileName()

            # Le motif
            pattern = self._newPattern()
            pSize = len(pattern)

            # Taille du buffer
            buffSize = pSize if pSize < fileSize else fileSize

            try:
                # Ouverture du fihcier
                file = open(os.path.join(self.params_.folder_ ,name), 'w')
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
            if self.params_.verbose_ :
                print("Demande de remplissage de", self.displaySize(expectedFillSize))

            # Rien n'a été fait !!!
            still = expectedFillSize
            totalSize = 0
            files = 0
            cont = True
            
            while totalSize < expectedFillSize and cont:
                res = self.newFile(maxFileSize = still)

                if 0 == res[1]:
                    # Erreur ...
                    cont = False
                else:
                    if self.params_.verbose_:
                        print("  + " + res[0] + " - " + self.displaySize(res[1]) + " / " + self.displaySize(still) + " restants")
                    
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
                for file in os.listdir(self.params_.folder_):
                    fName = os.path.join(self.params_.folder_, file)
                    
                    # Un fichier ?
                    if self._fileExists(fName):
                        name = fName
                        break

            # Le fichier doit exister
            if self._fileExists(name):
                try:
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
        return "", 0

    # Suppression d'un ou plusieurs fichiers sur un critère de nombre ou de taille à libérer
    #   retourne True lorsque l'opération s'est déroulée correctement
    def deleteFiles(self, count = 0, size = 0):
        
        tSize = 0
        tFiles = 0
        
        if True == self.valid_:
            # Il y a quelques choses à faire ....
            if not 0 == count or not 0 == size:
                
                if self.params_.verbose_:
                    if not 0 == size :
                        print("Demande de suppression à hauteur de", self.displaySize(size))
                    else:
                        print("Demande de suppression de " + str(count) + " fichiers")

                
                # Liste des fichiers du dossier
                files = [ f for f in os.listdir(self.params_.folder_) if os.path.isfile(os.path.join(self.params_.folder_,f)) ]

                # On mélange la liste
                random.shuffle(files)
                
                # Suppression des fichiers
                try:
                    # Les fichiers "fils"
                    for file in files:
                        fullName = os.path.join(self.params_.folder_, file) 
                        res = self.deleteFile(fullName)

                        # Suppression effectuée ?
                        if res[1] > 0:
                            tFiles+=1       # Un fichier de + (de supprimé ...)
                            tSize+=res[1]   # La taille en octets

                            if self.params_.verbose_:
                                if 0 == size:
                                    print("  -v" + res[0] + " - " + str(tFiles) + " / " + str(count) + " restant(s)")
                                else:
                                    print("  - " + res[0] + " - " + self.displaySize(res[1]) + " / " + self.displaySize(size - tSize) + " restants")

                            # Quota atteint
                            if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                                break

                        # On attend ...
                        time.sleep(self.elapseFiles_)

                except :
                    # Une erreur => on arrête de suite ...
                    return False

        # Fin des traitements
        print("Suppression de", self.displaySize(tSize), " -", str(tFiles),"fichiers supprimés")
        return True

    # Vidage du dossier
    #   
    #   Retourne Le tuple (# supprimé, message d'erreur / "")
    #
    def empty(self):
        if False == self.valid_:
            return 0, "Objet non initialisé"

        count = 0

        # Vidage du dossier
        try:
            # Analyse récursive du dossier
            for (curPath, dirs, files) in os.walk(self.params_.folder_):
                if curPath == self.params_.folder_:
                    dirs[:]=[] # On arrête de parser
            
                # Les fichiers "fils"
                for file in files:
                    fullName = os.path.join(curPath, file) 
                    count+=1

                    self.deleteFile(fullName)
        except:
            return 0, "Erreur lors du vidage de "+self.params_.folder_
        
        # Dossier vidé
        return count, ""

    # Taille du dossier
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
        
    # Representation d'une taille (en octets)
    #   Retourne une chaine de caractères
    def displaySize(self, size):
        
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
    # Méthodes internes
    #

    # Génération d'un motif aléatoire
    #   retourne une chaine aléatoire "lisible"
    def _newPattern(self):
        
        # Taille du motif
        patternSize = random.randint(parameters.PATTERN_MIN_LEN, self.maxPatternSize_)
        
        # Génération de la chaine
        out = ""
        maxIndex = len(parameters.PATTERN_BASE_STRING) - 1
        for _ in range(patternSize):
            # Valeur aléatoire
            out+=parameters.PATTERN_BASE_STRING[random.randint(0, maxIndex)]

        # Terminé
        return out

    # Génération d'un nom de fichier
    #   Retourne un nom unique de fichier (le nom court est retourné)
    def _newFileName(self):
        now = datetime.datetime.now()

        name = now.strftime("%Y%m%d-%H%M%S-%f")
        fullName = os.path.join(self.params_.folder_, name)

        # Tant qu'il existe
        count = 0
        while True == self._fileExists(fullName):
            # On génère un nouveau nom
            count+=1
            name = name + "-" + str(count)
            fullName = os.path.join(self.params_.folder_, name )
        
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
        except IOError: 
            # print("Le fichier ", self.fileName_, " n'existe pas")
            return False
        except:
            # print("Erreur lors de l'ouverture du fichier", self.fileName_)
            return False
        
        # oui
        return True

# EOF