# coding=UTF-8
#
#   Fichier     :   basicFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets basicFile et basicFolder
#
#                   basicFile : Gestion d'un fichier
#
#                   basicFolder modélise un dossier lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
import os, random, datetime, math, hashlib
from parameters import options as p, FILESIZE_MAX, FILESIZE_MIN, PATTERN_MIN_LEN, PATTERN_MAX_LEN, PATTERN_BASE_STRING
from sharedTools.colorizer import textColor

#
# Classe basicFile - un fichier (à créer, salir ou supprimer)
#
class basicFile:
    
    # Constructeur
    def __init__(self, fName = None, iterate = 1):
        self.name_ = fName
        self.iterate_ = iterate
        self.pattern_ = ""
        self.error_ = ""

    # Nom du fichier
    @property
    def name(self) -> str:
        return self.name_
    
    @name.setter
    def name(self, value):
        self.name_ = value

    # Nom court
    def shortName(self):
        if len(self.name_) == 0:
            return ""
        res = os.path.split(self.name_)
        return res[1]
    
    #
    # Gestion des erreurs
    #
    @property
    def error(self) -> str:
        message =self.error_
        if len(message):
            # Effacement du message aprèsz consultation
            self.error_ = ""
        return message
    
    @error.setter
    def error(self, value):
        self.error_ = value

    # Une erreur ?
    def noError(self):
        return 0 == len(self.error_)

    #
    # Gestion des fichiers
    #

    # Création d'un nouveau fichier
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def create(self, fileSize = 0, maxFileSize = 0):
        if self.exists():
            if len(self.rename(True)) > 0:
                yield from self._createFile(fileSize, maxFileSize, True)  

    # Remplissage d'un fichier existant
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def fill(self):
        if self.exists():
            if len(self.rename()) > 0:
                for _ in range(self.iterate_):
                    yield from self._createFile()
    # Renomage
    #   Retourne le nouveau nom (ou l'ancien en cas d'erreur)
    def rename(self, force = False):
        if (not force and self.exists()) or force:
            # Nouveau nom "complet"
            name = self.genName()
            try:
                os.rename(self.name_, name)
                self.name_ = name
            except:
                # une erreur
                return self.name_

            return name

        # sinon on retourne le nom de base
        return self.name_

    # Suppression
    #   clear : Doit-on effacer le contenu ?
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def delete(self, clear = True):
        # Le fichier doit exister
        if self.exists():
            
            # Remplacement du contenu ?
            if clear:
                # Nouveau nom
                if len(self.rename()) > 0:
                    # Nouveau contenu (on itère l'effacement)
                    for _ in range(self.iterate_):
                        yield from self._createFile()
            try:
                # (puis) effacement
                if len(self.name_)>0:
                    os.remove(self.name_)
            except:
                self.error_ = f"Erreur lors de la tentative de suppression de {self.name_}"

    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        return None if len(self.name_) == 0 or not self.exists() else os.path.getsize(self.name_)

    # Le fichier existe t'il ?
    def exists(self, fileName = None):
        # Le nom est-il renseigné ?
        if len(self.name_) == 0 and len(fileName) == 0:
            return False

        # On va essayer d'ouvrir le fichier en lecture
        try:
            file = open(fileName if fileName is not None else self.name_, 'r')
            file.close()
            return True
        except:
            return False
            
    # Génération d'un nom de fichier pour un fichier existant ou un nouveau fichier
    #   Retourne le nouveau nom complet ou "" en cas d'anomalie
    def genName(self, parentFolder = None, folder = False):
        # Dossier parent
        if parentFolder is None:
            # Utilisation du nom courant
            if len(self.name_) == 0:
                return ""
            folder, _ = os.path.split(self.name_)
        else:
            folder = parentFolder
        
        # Tant qu'il existe (avec le même nom)
        generate = True
        while True == generate:
            fName = os.path.join(folder, self._genName())
        
            # Si le fichier ou le dossier existe on génère un nouveau nom
            generate = os.path.isdir(fName) if folder else self.exists(fName)

        # Retour du nom complet
        return fName

    #
    # Méthodes internes
    #

    # Génération d'un nouveau nom (fichier ou dossier)
    #   Retourne le nouveau nom
    def _genName(self):
        hash = hashlib.blake2b(digest_size=20)
        hash.update(str.encode(now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")))
        return hash.hexdigest()

    # Génération d'un motif aléatoire
    def _genPattern(self):
        self.pattern_ = ""
        for _ in range(random.randint(PATTERN_MIN_LEN, PATTERN_MAX_LEN)):
            self.pattern_+=PATTERN_BASE_STRING[random.randint(0, len(PATTERN_BASE_STRING) - 1)]

    # Création d'un fichier à la taille demandée
    #  Si le fichier existe son contenu sera remplacé
    def _createFile(self, fileSize = 0, maxFileSize = 0, isNew = False):
        currentSize = 0
        
        # Création ?
        if isNew:
            # Si la taille est nulle => on choisit aléatoirement
            if 0 == fileSize:
                # 1 => ko, 2 = Mo
                unit = 1 + random.randint(1, 1024) % 2
                fileSize = 2 ** (unit * 10) * random.randint(FILESIZE_MIN, FILESIZE_MAX)

                # On remplit (mais on ne déborde pas !)
                if maxFileSize >0 and fileSize > maxFileSize:
                    fileSize = maxFileSize
        else:
            # Remplissage
            if False == self.exists():
                self.error_ = f"Erreur, le fichier '{self.name_}' n'existe pas"
                return

            # On conserve la taille
            fileSize = self.size()

        # Nouveau motif
        self._genPattern()
        pSize = len(self.pattern_)

        # Taille du buffer
        buffSize = pSize if pSize < fileSize else fileSize

        # Ouverture / création du fichier            
        try:
            file = open(self.name_, 'w')
        except:
            self.error_ = f"Impossible d'ouvrir {self.name_}"
            return

        try:
            # Remplissage du fichier
            while currentSize < fileSize:
                # Ecriture du buffer
                file.write(pattern)
                currentSize+=buffSize

                # On retourne la taille du paquet écrit
                yield buffSize

                # Le dernier paquet doit-il être tronqué ?
                if (currentSize + buffSize) > fileSize:
                    buffSize = fileSize - currentSize
                    pattern = pattern[:buffSize]
        except:
            self.error_ = f"Erreur lors de l'ecriture dans {self.name_}"
        finally:
            file.close()

#
# Classe basicFolder - un dossier de remplissage ou à vider ...
#
class basicFolder:

    # Données membres
    valid_ = False                      # L'objet est-il correctement initialisé ?
    name_ = ""                          # Nom complet du dossier
    params_ = None
    maxPatternSize_ = PATTERN_MAX_LEN   # Taille maximale du motif aléatoire
    sizes_ = None                       # Taille et # fichiers contenus

    restricted_ = []                    # Liste des dossiers que l'on ne peut supprimer

    # Constructeur
    def __init__(self, options, pMaxSize = 0):
        # Initialisation des données membres
        self._valid = False
        self.name_ = ""
        self.params_ = options
        self.maxPatternSize_ = pMaxSize if (pMaxSize > PATTERN_MIN_LEN and pMaxSize < PATTERN_MAX_LEN) else PATTERN_MAX_LEN
        sizes_ = None
        
        # Dossiers protégés
        self.restricted_.append(p.homeFolder()) 
        trashes = p.trashFolders()
        for trash in trashes:
            self.restricted_.append(trash)

    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self, name = None):

        # Initialisation du générateur aléatoire
        random.seed()

        if name is not None and False == self.setName(name):
            return False, f"Le dossier '{name}' n'existe pas"
        
        # Ok - pas  de message
        return True , ""
    
    # Nom du dossier courant
    def name(self):
        return self.name_
    
    def setName(self, name):
        # Le dossier existe t'il ?
        if False == os.path.isdir(name):
            self.name_ = ""
            self.valid_ = False
            return False
        
        # Ok
        self.name_ = name
        self.valid_ = True
        return True

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
                #except ValueError as e:
                    if self.params_.verbose_:
                        print(self.params_.color_.colored(f"Erreur lors de la tentative de suppression de {name}", textColor.ROUGE))
                    pass 

        # Rien n'a été fait
        return "", 0
    
    # Vidage d'un dossier
    #
    #       folder : nom complet du dossier à vider ("" => dossier courant)
    #       recurse : suppression recursive des sous-dossiers ?
    #       remove : Suppression du dossier (-1 : pas de suppression; 0 : Suppression du dossier et de tous les descendants; n : suppression à partir de la profondeur n)
    #   
    #   Generateur - "Retourne" {Fichier?, nom du fichier/dossier supprimé, effectué ?}
    #
    def empty(self, folder = None, recurse = False, remove = -1):
        folderName = self.name_ if folder is None else folder
        # Analyse récursive du dossier
        for entry in os.scandir(folderName):
            fullName = os.path.join(folderName, entry.name) 
            if entry.is_file():
                # Un fichier
                ret = self.deleteFile(fullName)
                yield True, fullName, ret[1] > 0
            elif entry.is_dir():
                # Un sous dossier => appel récursif
                if recurse:
                    yield from self.empty(fullName, True, remove - 1 if remove > 0 else remove)
        
        # Suppression du dossier courant?
        if 0 == remove:
            yield False, folderName, self.rmdir(folderName)

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
                folder = self.name_ if len(self.name_) else self.params_.folder_
            
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
    
    # Suppression du dossier
    #   retourne un booléen : fait ?
    def rmdir(self, folder):
        if len(folder) == 0:
            return
        
        # Puis-je le supprimer ?
        if folder in self.restricted_:
            # Non, le dossier est dans la liste ....
            return False
        
        # Récupération du dossier parent
        res = os.path.split(folder)
        if len(res[0]) == 0 or len(res[1]) == 0 :
            # Le chemin n'est pas possible => pas de dossier parent
            return False

        # Nouveau nom
        nFolder = self._newFolderName(res[0])
        if 0 == len(nFolder):
            return False
        
        # Renommage demandé mais pas obligatoire ...
        try:
            os.rename(folder, nFolder)
        except:
            # Impossible de renommer
            nFolder = folder    # Peut-être que l'on pourra malgré tout supprimer le fichier
        
        # Suppression
        try:
            os.rmdir(nFolder)
        except:
            return False
        
        return True
        
    # Représentation d'une taille (en octets)
    #   Retourne une chaine de caractères
    def size2String(self, size):
        
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
        # Tant qu'il existe (avec le même nom)
        generate = True
        while True == generate:
            # On génère un nouveau nom
            now = datetime.datetime.now()
            #name = hashlib.sha256(str.encode(now.strftime("%Y%m%d-%H%M%S-%f"))).hexdigest()
            hash = hashlib.blake2b(digest_size=20)
            hash.update(str.encode(now.strftime("%Y%m%d-%H%M%S-%f")))
            name = hash.hexdigest()
            fullName = os.path.join(self.name_, name)
        
            # Si le fichier existe on génère un nouveau nom
            generate = self._fileExists(fullName)
        return name # On retourne le nom court
        
    # Génération d'un nom de dossier
    #   Retourne le chemin complet
    def _newFolderName(self, parent):
        now = datetime.datetime.now()
        name = now.strftime("%Y%m%d-%H%M%S-%f")
        fullName = os.path.join(parent, name)

        # Tant qu'il existe (avec le même nom)
        count = 0
        while True == self.exists(fullName):
            # On génère un nouveau nom
            count+=1
            name = name + "-" + str(count)
            fullName = os.path.join(parent, name)
        
        return fullName # On retourne le chemin complet

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

    # Remplissage d'un fichier
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
                    fname = os.path.join(self.params_.folder_, name)

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
                # Ouverture / création du fichier
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
            except:
                return name, 0, 0
            finally:
                file.close()
        else:
            name = ""

        return name, currentSize, pSize
# EOF