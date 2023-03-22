#!/bin/python3

# coding=UTF-8
#
#   File     :   dCleaner.py
#
#   Auteur      :   JHB
#
#   Description :   Point d'entrée du programme
#
#   Remarques    : 
#
#   Dépendances :  Nécessite python-psutil (apt-get install / dnf install)
#
import parameters
import os
from sharedTools import cmdLineParser as parser
from basicFolder import basicFolder
from paddingFolder import paddingFolder
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
            raise ValueError("Pas de paramètres")

        self.options_ = options

        # Le dossier est-il correct ?
        if self.options_.folder_ == "\\" or (os.path.exists(self.options_.folder_) and not os.path.isdir(self.options_.folder_)):
            message = "Le dossier '" + self.options_.folder_ + "' n'est pas correct"
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
    
        if self.options_.verbose_:
            out = "Paramètres : " 
            
            txt = ""
            if self.options_.clear_:
                txt = "libération"
            else: 
                if False == self.options_.noPadding_:
                    txt = "ajustement" if self.options_.adjust_ else "remplissage / nettoyage"
            
            if len(self.options_.clean_) > 0:
                if len(txt) > 0 : 
                    txt = txt + " &"
                txt = txt + " vidage de dossier"
            out += "\n\t- Mode : " + self.options_.color_.colored(txt, formatAttr=[textAttribute.GRAS])
            
            out += "\n\t- Taux de remplissage max : " + self.options_.color_.colored(str(self.options_.fillRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\n\t- Taux de renouvellement de la partition : " + self.options_.color_.colored(str(self.options_.renewRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\n\t- Attente entre 2 fichiers : " + str(self.options_.waitFiles_) + "s"
            out += "\n\t- Attente entre 2 itérations : " + str(self.options_.waitTasks_) + "s"
            
            if False == self.options_.adjust_ :
                out += "\n\t- Itération(s) de nettoyage : " + self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])
            
            out += "\n\nPartition : "
            out += "\n\t- Taille : " + self.paddingFolder_.size2String(res[0])
            out += "\n\t- Remplie à " + self.options_.color_.colored(str(round(res[1] / res[0] * 100 , 2)) + "%", formatAttr=[textAttribute.GRAS]) + " - " + self.paddingFolder_.size2String(res[1])
            
            if False == self.options_.noPadding_:
                out += "\n\nRemplissage : " 
                out += "\n\t- Nom : " + self.options_.color_.colored(self.paddingFolder_.name(), formatAttr=[textAttribute.GRAS])
                out += "\n\t- Contenu : " + self.paddingFolder_.size2String(self.paddingFolder_.size()) + "\n"

            if len(self.options_.clean_) > 0 :
                out += "\n\nVider : " 
                out += "\n\t - " + str(len(self.options_.clean_))  + " dossiers(s) à vider :"
                for dossier in self.options_.clean_:
                    out += "\n\t\t- " + self.options_.color_.colored(dossier, formatAttr=[textAttribute.GRAS])
                out += "\n\t- Profondeur : " + str(self.options_.cleanDepth_) + "\n"
        else :
            out = "Partition : " + self.paddingFolder_.size2String(res[0]) +  " - remplie à " + str(round(res[1] / res[0] * 100 ,0)) + "%"
            out += "\nRemplissage : " + self.options_.color_.colored(self.paddingFolder_.name(), formatAttr=[textAttribute.GRAS])
            out += "\nMode : " + ("nettoyage" if self.options_.clear_ else ("ajustement" if self.options_.adjust_ else "remplissage / nettoyage"))
            out += "\nTaux de remplissage max : " + self.options_.color_.colored(str(self.options_.fillRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\nTaux de renouvellement de la partition : " + self.options_.color_.colored(str(self.options_.renewRate_) + "%", formatAttr=[textAttribute.GRAS])                    
            
            if self.options_.clean_ is not None and len(self.options_.clean_) > 0:
                out += "\nVider : " + self.options_.color_.colored(str(len(self.options_.clean_)) + " dossiers(s) - Profondeur : " + str(self.options_.cleanDepth_), formatAttr=[textAttribute.GRAS])
            
            if False == self.options_.adjust_ :
                out += "\nItération(s) de nettoyage : " + self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])
            
        return out

    # Nettoyage (vidage) d'un dossier (dossier de remplissage / 'padding' si non précisé)
    #   Retourne Le tuple (# supprimé, message d'erreur / "")
    #
    def clearFolder(self, name = ""):
        if 0 == len(name):
            #return self.paddingFolder_.deleteFiles(count = self.paddingFolder_.files())
            return self.paddingFolder_.empty()
        else:
            # Vidage d'un dossier
            folder = basicFolder(self.options_)

            done, message = folder.init(name)
            if False == done:
                # Erreur d'initialisation du dossier
                raise ValueError(message)
            
            # Nettoyage ...
            return folder.empty(recurse = True, remove = self.options_.cleanDepth_)
    
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
                print(self.options_.color_.colored("La partition est déja trop remplie (" + self.paddingFolder_.size2String(currentFillSize) + " - " + str(round(currentFillSize / totalSize * 100 ,0)) + "% )", textColor.JAUNE))

            # ... en retirant les fichiers déja générés
            paddingFillSize = self.paddingFolder_.size()
            
            # Taille de ce que je dois supprimer
            gap = currentFillSize - maxFillSize
            
            if gap > paddingFillSize:
                # Tout le dossier de 'padding' n'y suffira pas ...
                print(self.options_.color_.colored("Le vidage du dossier de remplissage ne sera pas suffisant pour atteindre le taux de remplissage demandé", textColor.JAUNE))
                res = self.paddingFolder_.empty()
                print(self.options_.color_.colored("Dossier de 'padding' vidé", formatAttr=[textAttribute.GRAS]))
                
                if len(res[1]) > 0:
                    print(self.options_.color_.colored("Erreur lors du vidage du dossier de remplissage : " + res[1], textColor.ROUGE))
                    return False
            else:
                # Retrait du "minimum"
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
        renewSize = res[0] * (100 - self.options_.fillRate_) / 100 * self.options_.renewRate_ / 100 
        
        # on recadre avec l'espace effectivement dispo
        renewSize = parser.cmdLineParser.minMax(None, 0, renewSize, res[2] * self.options_.renewRate_ / 100)        
        
        # On remplit 
        self.paddingFolder_.newFiles(renewSize)
        
        # On supprime
        self.paddingFolder_.deleteFiles(size = renewSize)    

# Vérification des privilèges
def isRootLikeUser():
    try:
        if os.environ.get("SUDO_UID") or os.geteuid() != 0:
            return False
    except:
        # Je n'ai pas le droit
        pass
    
    # Oui ...
    return False

# Corps du programme
#
if '__main__' == __name__:
    
    # Ne peut-être lancé par un compte root ou "sudoisé"
    if isRootLikeUser() :
        print(parameters.APP_NAME + " doit être lancé par un compte 'non root'")
        exit()
    
    done = False

    # Ma ligne de commandes
    params = parameters.options()
    if True == params.parse():
        try:    
            done = True
            params.usage(False)

            cleaner = dCleaner(params)
            print(cleaner)

            if params.clear_:
                print("Nettoyage du dossier de 'padding'")
                res = cleaner.clearFolder()
                if len(res[1]) > 0  :
                    print(params.color_.colored("Erreur lors de la suppression : " + res[1], textColor.ROUGE))
                else:
                    print(str(res[0]) + " fichier(s) supprimé(s)")
            else:
                # Remplissage de la partition
                if False == params.noPadding_:
                    print("Vérification du dossier de 'padding'")
                    if False == cleaner.fillPartition():
                        # Il faut plutôt libérer de la place
                        cleaner.freePartition()

                    # doit-on maintenant "salir" le disque ?
                    if False == params.adjust_:
                        
                        for index in range(params.iterate_):
                            if index > 0:
                                # On patiente un peu ...
                                if params.verbose_:
                                    print("On attend un peu...")
                                cleaner.paddingFolder_.wait(params.waitTasks_)

                            if params.verbose_:
                                print("Iteration " + str(index + 1) + " / " + str(params.iterate_))
                            
                            cleaner.cleanPartition()

                # Nettoyer un ou plusieurs dossiers ?
                if len(params.clean_) > 0:
                    for folderName in params.clean_:
                        cleaner.clearFolder(folderName)

        except ValueError as e:
            print(params.color_.colored("Erreur de paramètre(s) : " + str(e), textColor.ROUGE))
        """
        except :
            print(params.color_.colored("Erreur inconnue", textColor.ROUGE))
        """
    # La fin, la vraie !
    if done:
        print(params.color_.colored("Fin des traitements", datePrefix = (False == params.verbose_)))

# EOF