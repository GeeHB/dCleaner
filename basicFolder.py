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
from parameters import WINDOWS_TRASH, FILESIZE_MAX, FILESIZE_MIN, PATTERN_MIN_LEN, PATTERN_MAX_LEN, PATTERN_BASE_STRING

#
# Objet du système de fichier (dossier ou fichier) à supprimer / vider
#
class FSObject(object):
    
    # Est-ce un fichier ?
    def isFile(self):
        return False
    
    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        pass

    # Représentation d'une taille (en octets)
    #   Conversion int -> str
    #
    #   size : Taille en octets à convertir
    #
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

#
# Classe basicFile - un fichier (à créer, salir ou supprimer)
#
class basicFile(FSObject):
    
    # Constructeur
    def __init__(self, path = None, fName = None, iterate = 1, FQDN = None):
        
        # Initialisation des données membres
        self.iterate_ = iterate
        self.pattern_ = ""
        self.error_ = ""

        # Un nom complet (ie. le fichier existe !!!)
        if FQDN is not None :
            self.name = FQDN
        else:
            # Nom du fichier
            if path is not None and basicFolder.existsFolder(path):
                # Le dossier est valide
                if fName is not None and len(fName)>0 :
                    # Le nom est "correct"
                    self.name = os.path.join(path, fName)
                else:
                    # Génération d'un nom nouveau
                    name = basicFile.genName(path, False)
                    if name is None:
                        self.error = "Impossible de générer un nom de fichier pour le dossier  {path}"
                    else:
                        self.name = name
            else:
                # pas de nom (pour l'instant)
                self.name = ""

    # Est-ce un fichier ?
    def isFile(self):
        return True
    
    # Initialisation du générateur aléatoire
    @staticmethod
    def init():
        random.seed()

    # Nom du fichier
    @property
    def name(self):
        return self.name_ if self.name_ is not None else ""
    
    @name.setter
    def name(self, value):
        self.name_ = value

    # Nom court
    def shortName(self):
        if len(self.name_) == 0:
            return ""
        _, sName = os.path.split(self.name_)
        return sName
    
    # Nom du dossier
    def folder(self):
        if 0 == len(self.name):
            return None

        f, _ = os.path.split(self.name)
        return f
    
    #
    # Gestion des erreurs
    #
    @property
    def error(self):
        message =self.error_
        if len(message):
            # Effacement du message après consultation
            self.error_ = ""
        return message
    
    @error.setter
    def error(self, value):
        self.error_ = value

    # La dernière opération s'est correctement déroulée ?
    def success(self):
        return 0 == len(self.error_)

    #
    # Gestion du fichier
    #

    # Création d'un nouveau fichier
    #
    #   Generator qui énumère les blocks d'octets crées
    #
    #   fileSize : Taille en octets du fichier (ou 0 si taille aléatoire)
    #   maxFileSize : Taille max. n octets d'un fichier
    #
    def create(self, fileSize = 0, maxFileSize = 0):
        if len(self.name):
            # Si le fichier existe, je le supprime ...
            if self.exists():
                self.delete()
        else:
            # Pas de nom
            self.error = f"Impossible de créer le fichier. Il n'a pas de nom"
                
        if self.success():
            # Creation à la "bonne taille"
            for _ in range(self.iterate_):
                for fragment in self._create(fileSize, maxFileSize, True):
                    yield fragment

    # Remplissage d'un fichier existant
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    #   rename : Doit-on renomer le fichier (avec un nom aléatoire) ?
    #
    def fill(self, rename = False):
        if self.exists():
            for _ in range(self.iterate_):
                for fragment in self._create():
                    yield fragment

            if False == self.success():
                return

            # Nouveau nom
            if rename and len(self.rename()) == 0:
                self.error = f"Impossible de renommer {self.name_}"
            
    # Renomage
    #
    #   Retourne le nouveau nom (ou None en cas d'erreur)
    def rename(self):
        #if (not force and self.exists()) or force:
        if self.exists():
            folder, _ = os.path.split(self.name)
            
            # Nouveau nom "complet"
            name = self.genName(folder)
            try:
                os.rename(self.name_, name)
                self.name_ = name
            except OSError:
                # une erreur
                return None

            return name

        # sinon on retourne le nom de base
        return self.name_

    # Suppression
    #
    #   replace : Doit-on remplacer le contenu ?
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def delete(self, replace = True):
        # Le fichier doit exister
        if self.exists():   
            # Remplacement du contenu ?
            if replace:
                # Nouveau nom
                nName = self.rename() 
                if nName is None or len(nName) == 0:
                    self.error = f"Impossible de renommer {self.name_}"     
                    
                # Nouveau contenu (on itère l'effacement)
                for _ in range(self.iterate_):
                    for fragment in self._create():
                        yield fragment

                if False == self.success():
                    return
            
            # Dans tous les cas, effacement
            try:
                if len(self.name_)>0:
                    os.remove(self.name_)
            except OSError:
                self.error = f"Erreur lors de la tentative de suppression de {self.name_}"

    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        return None if len(self.name_) == 0 or not self.exists() else os.path.getsize(self.name_)

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
    
    def exists(self):
        return False if len(self.name) == 0 else basicFile.existsFile(self.name)
            
    # Génération d'un nom de fichier pour un fichier existant ou un nouveau fichier
    #
    #   parentFolder : dossier parent (qui contiendra le nouvel élément)
    #   folder : S'agit'il d'un dossier ?
    #
    #   Retourne le nouveau nom complet ou None en cas d'anomalie
    @staticmethod
    def genName(parentFolder, folder = False):
        # Dossier parent
        if parentFolder is None:
            return None
            
        # Tant qu'il existe (avec le même nom)
        generate = True
        while True == generate:
            fName = os.path.join(parentFolder, basicFile._genName())
        
            # Si le fichier ou le dossier existe on génère un nouveau nom
            #generate = os.path.isdir(fName) if folder else self.exists(fName)
            generate = basicFolder.existsFolder(fName) if folder else basicFile.existsFile(fName)

        # Retour du nom complet
        return fName

    #
    # Méthodes internes
    #

    # Génération d'un nouveau nom (fichier ou dossier)
    #   Retourne le nouveau nom
    @staticmethod
    def _genName():
        now = datetime.datetime.now()
        hash = hashlib.blake2b(digest_size=20)
        hash.update(str.encode(now.strftime("%Y%m%d-%H%M%S-%f")))
        return hash.hexdigest()

    # Génération d'un motif aléatoire
    def _genPattern(self, maxPatternSize = PATTERN_MAX_LEN):
        self.pattern_ = ""
        iSize = int(maxPatternSize)
        maxSize = PATTERN_MAX_LEN if iSize > PATTERN_MAX_LEN else (iSize if iSize > PATTERN_MIN_LEN else PATTERN_MIN_LEN)
        for _ in range(random.randint(PATTERN_MIN_LEN, maxSize)):
            self.pattern_+=PATTERN_BASE_STRING[random.randint(0, len(PATTERN_BASE_STRING) - 1)]

    # Création d'un fichier à la taille demandée
    #  Si le fichier existe son contenu sera remplacé
    #
    #   fileSize : Taille en octets du fichier (ou 0 si taille aléatoire)
    #   maxFileSize : Taille max. n octets d'un fichier
    #   isNew : Est-ce une création de fichier ?
    #
    def _create(self, fileSize = 0, maxFileSize = 0, isNew = False):
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
            # On conserve la taille
            fileSize = self.size()

        # Nouveau motif
        self._genPattern(fileSize)
        pSize = len(self.pattern_)

        # Taille du buffer
        buffSize = pSize if pSize < fileSize else fileSize

        # Ouverture / création du fichier            
        currentSize = 0
        try:
            file = open(self.name_, 'w')
        except OSError:
            self.error = f"Impossible d'ouvrir {self.name_}"
            return

        try:
            # Remplissage du fichier
            while currentSize < fileSize:
                # Le dernier paquet (qui peut aussi être le premier) doit-il être tronqué ?
                if (currentSize + buffSize) > fileSize:
                    buffSize = fileSize - currentSize
                    self.pattern_ = self.pattern_[:buffSize]

                # Ecriture du buffer
                file.write(self.pattern_)
                currentSize+=buffSize

                # On retourne la taille du paquet écrit
                yield buffSize
        except OSError:
            self.error = f"Erreur lors de l'ecriture dans {self.name_}"
        finally:
            file.close()

#
# Classe basicFolder - un dossier de remplissage ou à vider ...
#
class basicFolder(FSObject):

    # Nom du fichier
    @property
    def name(self):
        return self.name_ if self.name_ is not None else ""
    
    @name.setter
    def name(self, value):
        # Poubelle Windows => non géré ...
        if value != WINDOWS_TRASH:
            # Le dossier existe t'il ?
            if value is None or value == "" or False == os.path.isdir(value):
                self.name_ = ""
                self.valid_ = False
                return
        else:
            self.name_ = WINDOWS_TRASH
            self.valid_ = False
            return
            
        # Ok
        self.name_ = value
        self.valid_ = True

    # Les données internes sont-elles valides ?
    @property
    def valid(self):
        return self.valid_
    
    @valid.setter
    def valid(self, value):
        self.valid_ = value

    # Constructeur
    def __init__(self, opts, pMaxSize = 0):
        # Initialisation des données membres
        self.name = ""
        self.valid = False
        self.params_ = opts
        self.maxPatternSize_ = pMaxSize if (pMaxSize > PATTERN_MIN_LEN and pMaxSize < PATTERN_MAX_LEN) else PATTERN_MAX_LEN
        self.sizes_ = None
        self.restricted_ = []                    # Liste des dossiers que l'on ne peut supprimer
        
        # Dossiers protégés
        self.restricted_.append(opts.homeFolder()) 
        trashes = opts.trashFolders()
        for trash in trashes:
            self.restricted_.append(trash)

    # Initalisation
    #
    #   name : nom du dossier (ou None si dossier 'vierge')
    #
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self, name = None):

        # Initialisation du générateur aléatoire
        random.seed()

        if name is not None and False == basicFolder.existsFolder(name):
            return False, f"Le dossier '{name}' n'existe pas"
        
        # Ok - pas  de message
        self.name = name
        return True , ""
    
    # Création du dossier
    #
    #   name : nom du dossier à créer
    #
    #   retourne le booléen : crée ?
    def create(self, name):
        if name is None or len(name) == 0 :
            return False
        
        # On essaye de le créer
        try:
            os.makedirs(name)
            return True
        except OSError:   
            return False
    
    # Parcours récursif d'un dossier en vue de le vider
    #
    #       folder : Nom complet du dossier de départ ("" => dossier courant)
    #       recurse : Parcours recursif des sous-dossiers ?
    #       remove : Suppression du dossier (-1 : pas de suppression; 0 : Suppression du dossier et de tous les descendants; n : suppression à partir de la profondeur n)
    #   
    #   Generateur - "Retourne" {Fichier?, nom du fichier/dossier}
    #
    def browse(self, folder = None, recurse = False, remove = -1):
        folderName = self.name_ if folder is None else folder
        # Analyse récursive du dossier
        for entry in os.scandir(folderName):
            fullName = os.path.join(folderName, entry.name) 
            if entry.is_file():
                # Un fichier
                yield True, fullName
            elif entry.is_dir():
                # Un sous dossier => appel récursif
                if recurse:
                    yield from self.browse(fullName, True, remove - 1 if remove > 0 else remove)
        
        # Suppression du dossier courant?
        if 0 == remove:
            yield False, folderName
    
    # Taille du dossier (et de tout ce qu'il contient)
    #
    #   folder : nom du dossier à analyser ou none pour le dossier courant
    #
    #   Retourne le tuple (taille en octets, nombre de fichiers)
    def sizes(self, folder = "", recurse = False):
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
                    if recurse:
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
    #   
    #   folder : nom du dossier à supprimer
    #
    #   retourne un booléen : fait ?
    def rmdir(self, folder):
        if folder is None or len(folder) == 0:
            return False
        
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
        nFolder = basicFile.genName(res[0], True)
        if nFolder is not None:    
            # Renommage demandé mais pas obligatoire ...
            try:
                os.rename(folder, nFolder)
            except OSError:
                # Impossible de renommer
                nFolder = folder    # Peut-être que l'on pourra malgré tout supprimer le fichier
        else:
            nFolder = folder
            
        # Suppression
        try:
            os.rmdir(nFolder)
        except OSError:
            return False
        
        return True

    # Le dossier existe-il ?
    @staticmethod
    def existsFolder(folderName):
        # On vérifie ...
        return os.path.isdir(folderName)
    
    def exists(self, folderName = None):
        # On vérifie ...
        return self.existsFolder(folderName if (folderName is not None and len(folderName)) != 0 else self.name_)
    
# EOF