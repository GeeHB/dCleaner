#!/bin/python3

# coding=UTF-8
#
#   Fichie      : dCleaner.py
#
#   Auteur      : JHB
#
#   Description : Outil de nettoyage de la partition utilisateur
#
#   Remarques   : Point d'entrée du programme
#
#   Dépendances : Nécessite psutil
#
from parameters import options, APP_NAME, WINDOWS_TRASH, TIME_PREFIX, FOLDERS_TRASH, FOLDERS_TRASH_BIS
import os,sys
from datetime import datetime
from basicFolder import basicFolder
from winTrashFolder import winTrashFolder
from paddingFolder import paddingFolder
from basicFolder import FSObject, basicFile
from sharedTools.colorizer import textAttribute, textColor

# Classe dCleaner
#   Actions sur le dossier de remplissage
#
class dCleaner:
    # Données membre
    #
    options_ = None

    # Construction
    def __init__(self, options):
        # Initialisation des données membres
        if None == options or None == options.folder_:
            raise ValueError("Pas de paramètre ou paramètres incorrects")

        self.options_ = options

        # Le dossier est-il correct ?
        if self.options_.folder_ == "\\" or (os.path.exists(self.options_.folder_) and not os.path.isdir(self.options_.folder_)):
            message = f"'{self.options_.folder_}' ne correspond pas à un dossier correct"
            raise ValueError(message)

        # Création de l'objet pour la gestion du dossier
        self.paddingFolder_ = paddingFolder(self.options_)
        done, message = self.paddingFolder_.init()

        if False == done:
            # Erreur d'initialisation du dossier
            raise ValueError(message)

    # Affichage des paramètres internes de l'objet
    def __repr__(self):
        
        # Quelques informations ...
        #
        res = self.paddingFolder_.partitionUsage()

        mode = ""
        if self.options_.clear_:
            mode = "libération"
        else: 
            if False == self.options_.noPadding_:
                mode = "ajustement" if self.options_.adjust_ else "remplissage / nettoyage"
        
        if len(self.options_.clean_) > 0:
            if len(mode) > 0 : 
                mode = mode + " & "
            mode = mode + "vidage de dossier"
    
        if self.options_.verbose_:
            out = "Paramètres : " 
            out += f"\n\t- Mode : {self.options_.color_.colored(mode, formatAttr=[textAttribute.GRAS])}"
            
            out += "\n\t- Taux de remplissage max : " + self.options_.color_.colored(f"{self.options_.fillRate_}%", formatAttr=[textAttribute.GRAS])
            out += "\n\t- Taux de renouvellement de la partition : " + self.options_.color_.colored(f"{self.options_.renewRate_}%", formatAttr=[textAttribute.GRAS])
            out += f"\n\t- Attente entre 2 fichiers : {self.options_.waitFiles_}s"
            out += f"\n\t- Attente entre 2 itérations : {self.options_.waitTasks_}s"
            
            if False == self.options_.adjust_ :
                out += f"\n\t- Itération(s) de nettoyage : {self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])}"
            
            out += "\n\nPartition : "
            out += f"\n\t- Taille : {FSObject.size2String(res[0])}"
            out += "\n\t- Remplie à " + self.options_.color_.colored(f"{round(res[1] / res[0] * 100 , 2)}%", formatAttr=[textAttribute.GRAS]) + " - " + FSObject.size2String(res[1])
            
            if False == self.options_.noPadding_:
                out += "\n\nRemplissage : " 
                out += f"\n\t- Nom : {self.options_.color_.colored(self.paddingFolder_.name, formatAttr=[textAttribute.GRAS])}"
                out += f"\n\t- Contenu : {FSObject.size2String(self.paddingFolder_.size())}\n"

            if len(self.options_.clean_) > 0 :
                out += "\n\nVider : " 
                out += f"\n\t - {len(self.options_.clean_)} dossiers(s) à vider :"
                for FSO in self.options_.clean_:
                    out += f"\n\t\t- {self.options_.color_.colored(FSO.name, formatAttr=[textAttribute.GRAS])}"
                out += f"\n\t- Récursivité : {self.options_.color_.colored('oui' if self.options_.recurse_ else 'non', formatAttr=[textAttribute.GRAS])}\n"
                if self.options_.recurse_:
                    out += f"\n\t- Profondeur : {self.options_.cleanDepth_}\n"
        else :
            out = f"Partition : {FSObject.size2String(res[0])} - remplie à {round(res[1] / res[0] * 100 ,0)}%"
            out += "\nRemplissage : " + self.options_.color_.colored(self.paddingFolder_.name, formatAttr=[textAttribute.GRAS])
            out += "\nMode : " + mode
            out += "\nTaux de remplissage max : " + self.options_.color_.colored(f"{self.options_.fillRate_}%", formatAttr=[textAttribute.GRAS])
            out += "\nTaux de renouvellement de la partition : " + self.options_.color_.colored(f"{self.options_.renewRate_}%", formatAttr=[textAttribute.GRAS])                    
            
            if self.options_.clean_ is not None and len(self.options_.clean_) > 0:
                out += "\nVider : " + self.options_.color_.colored(f"{len(self.options_.clean_)} dossiers(s) - Profondeur : {self.options_.cleanDepth_}", formatAttr=[textAttribute.GRAS])
            
                if self.options_.recurse_:
                        out += "\n\Récursivité : oui"

            if False == self.options_.adjust_ :
                out += f"\nItération(s) de nettoyage : {self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])}"            
        return out

    # Nettoyage (vidage) de dossiers ou fichiers
    #
    #   fList : liste des dossiers ou fichiers à supprimer (dossier de remplissage / 'padding' si non précisé)
    #
    #   Retourne Le tuple (# supprimé, #dossiers supprimés, message d'erreur / "")
    #
    def cleanFolders(self, fList = None):
        if fList is None or 0 == len(fList):
            ret = self.paddingFolder_.clean()
            return ret[0], 0, ret[1]
        else:
            return self.paddingFolder_.cleanFolders(fList)
    
    # Remplissage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    #
    def fillPartition(self):
        res = self.paddingFolder_.partitionUsage()
        maxFill = res[0] * self.options_.fillRate_ / 100

        if res[1] < maxFill:
            # On fait en sorte de coller immédiatement au taux de remplissage
            fillSize = maxFill - res[1]
            self.paddingFolder_.newFiles(fillSize)
            return True
        
        # La partition est déja "pleine"
        return False
        
    # Nettoyage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    #
    def freePartition(self):
        
        # Mode "initial" : on fait en sorte de coller immédiatement au taux de remplissage
        totalSize, currentFillSize, _ = self.paddingFolder_.partitionUsage()
        maxFillSize = totalSize * self.options_.fillRate_ / 100
    
        if currentFillSize > maxFillSize:
            if self.options_.verbose_:
                print(self.options_.color_.colored(f"La partition est déja trop remplie ({FSObject.size2String(currentFillSize)} - {round(currentFillSize / totalSize * 100 ,0)}% )", textColor.JAUNE))

            # ... en retirant les fichiers déja générés
            paddingFillSize = self.paddingFolder_.size()
            
            # Taille de ce que je dois supprimer
            gap = currentFillSize - maxFillSize
            
            if gap > paddingFillSize:
                # Tout le dossier de 'padding' n'y suffira pas ...
                print(self.options_.color_.colored("Le vidage du dossier de remplissage ne sera pas suffisant pour atteindre le taux de remplissage demandé", textColor.JAUNE))
                res = self.paddingFolder_.clean()
                print(self.options_.color_.colored("Dossier de 'padding' vidé", formatAttr=[textAttribute.GRAS]))
                
                if len(res[1]) > 0:
                    print(self.options_.color_.colored(f"Erreur lors du vidage du dossier de remplissage : {res[1]}", textColor.ROUGE), file=sys.stderr)
                    return False
            else:
                # Retrait du "minimum"
                if not self.options_.verbose_:
                    print(params.color_.colored(f"Suppression de {FSObject.size2String(gap)}", datePrefix = True))
                self.paddingFolder_.deleteFiles(size=gap)
            
            return True

        # Rien n'a été fait
        return False

    # Rafraichissement - remplissage et nettoyage ponctuel
    #
    def cleanPartition(self):
        
        # Taille en octets du volume à renouveller
        res = self.paddingFolder_.partitionUsage()
        
        # Valeur max. théorique
        renewSize = int(res[0] * (100 - self.options_.fillRate_) / 100 * self.options_.renewRate_ / 100) 
        
        # on recadre avec l'espace effectivement dispo
        renewSize = int(options.inRange(None, 0, renewSize, res[2] * self.options_.renewRate_ / 100))
        
        if self.options_.verbose_:
            self.indented_print("Remplissage", True)
        self.paddingFolder_.newFiles(renewSize, iterate = True)
        
        if self.options_.verbose_:
            self.indented_print("Suppression", True)
        self.paddingFolder_.deleteFiles(size = renewSize, iterate = True) 
        if  self.options_.verbose_:
            self.indented_print("Terminé", True)   

    # Affichage d'une ligne indentée
    #
    def indented_print(self, line, date = False):
        if date:
            today = datetime.now()
            prefix = today.strftime(TIME_PREFIX)
        else:
            prefix = ""
        print("\t-"+prefix+line)

# Vérification des privilèges
def isRootLikeUser():
    try:
        if os.environ.get("SUDO_UID") or os.getpid() != 0:
            return False
    except OSError:
        # Je n'ai pas le droit
        pass
    
    # Oui ...
    return True

# Liste des dossiers à nettoyer
#
#   params : Valeurs / paramètres issus de la ligne de commande
#
#   retourne un booléen : des éléments à supprimer ?
#
def _listOfFolders(params):
    
    # On s'assure que les dossiers/fichiers existent et on crée les objets en conséquence
    fileOrFolders = []
    for folder in params.clean_:
        currentFSO = objectFromName(folder, params)
        if currentFSO is not None:
            fileOrFolders.append(currentFSO)

    # Mise à jour de la liste (qui devient une liste d'objets de type FSObject)
    params.clean_ = fileOrFolders
    return len(params.clean_) > 0

# Instantiation d'un objet en fonction de son nom
#
#   name : Nom complet de l'objet
#   
#   iterations : Nombre d'itérations
#
#   retourne un objet (basicFile ou basicFolder) en fonction du nom ou None en cas d'erreur
#
def objectFromName(name, params):
    # Un fichier ?
    if basicFile.existsFile(name):
        return basicFile(FQDN = name, iterate = params.iterate_)
    else:
        obj = None  # pas encore crée

        # Un dossier ?
        if WINDOWS_TRASH == name :
            obj = winTrashFolder(opts = params)
        else :
            if basicFolder.existsFolder(name):
                obj = basicFolder(opts = params)
              
        if obj is not None:
            res = obj.init(name)
            if False == res[0]:
                if len(res[1]):
                    print(params.color_.colored(res[1], textColor.ROUGE), file=sys.stderr)
                return None
            
        if obj is None:
            print(params.color_.colored(f"Nettoyage : '{name}' n'existe pas", textColor.ROUGE), file=sys.stderr)

        return obj
    
#
# Corps du programme
#
if '__main__' == __name__:
    
    # Ne peut-être lancé par un compte root ou "sudoisé"
    if isRootLikeUser() :
        print(f"{APP_NAME} doit être lancé par un compte 'non root'")
        exit()
    
    done = False

    # Initialisations
    basicFile.init()

    # Ma ligne de commandes
    params = options()
    if True == params.parse():
        try:    
            done = True
            print(params.version())

            # Des dossiers ou fichiers à nettoyer ?
            if params.clean_ is not None and len(params.clean_) > 0:
                
                # Analyse de la liste ...
                #                
                # Encore des dossiers dans la liste ?
                if False == _listOfFolders(params):
                    print(params.color_.colored("Pas de dossier ou de fichier à nettoyer", textColor.ROUGE), file=sys.stderr)
                        
            # Lancement de l'application avec les paramètres
            cleaner = dCleaner(params)
            print(cleaner)

            if params.clear_:
                print("Nettoyage du dossier de 'padding'")
                res = cleaner.cleanFolders()
                if len(res[2]) > 0  and res[3]:
                    print(params.color_.colored(f"Erreur lors de la suppression : {res[2]}", textColor.ROUGE), file=sys.stderr)
                else:
                    print(f"{FSObject.count2String('fichier', res[0])} supprimé(s)")
            else:
                # Nettoyer un ou plusieurs dossiers (ou fichiers) ?
                if  0 != len(params.clean_):
                    res = cleaner.cleanFolders(params.clean_)

                    if len(res[2]) > 0 :
                        if res[3]:
                            # Une erreur
                            print(params.color_.colored(f"Erreur lors de la suppression : {res[2]}", textColor.ROUGE), file=sys.stderr)
                        else:
                            # Juste un message ...
                            print(res[2])
                    
                # Remplissage de la partition
                if False == params.noPadding_:
                    print("Vérification du dossier de 'padding'")
                    if False == cleaner.fillPartition():
                        # Il faut plutôt libérer de la place
                        cleaner.freePartition()

                    # Doit-on maintenant "salir" le disque ?
                    if False == params.adjust_:
                        
                        for index in range(params.iterate_):
                            if index > 0:
                                if params.verbose_:
                                    cleaner.indented_print("On attend un peu...")
                                cleaner.paddingFolder_.wait(params.waitTasks_)

                            if params.verbose_:
                                print(f"Itération {index+1}/{params.iterate_}")
                            
                            cleaner.cleanPartition()

        except IOError as ioe:
            print(params.color_.colored(f"Erreur de paramètre(s) : {str(ioe)}", textColor.ROUGE), file=sys.stderr)
        except KeyboardInterrupt as kbe:
            print(params.color_.colored("Interruption des traitements", textColor.JAUNE))
        except ValueError as ve:
            print(params.color_.colored(f"Erreur d'initialisation : {str(ve)}", textColor.ROUGE), file=sys.stderr)
        """
        except Exception as e:
            print(params.color_.colored(f"Erreur inconnue - {str(e)}", textColor.ROUGE), file=sys.stderr)
        """
    # La fin, la vraie !
    if done:
        print(params.color_.colored("Fin des traitements", datePrefix = (False == params.verbose_)))

# EOF