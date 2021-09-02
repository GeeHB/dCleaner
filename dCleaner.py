#!/bin/python3

# coding=UTF-8
#
#   File     :   dCleaner.py
#
#   Auteur      :   JHB
#
#   Description :   Point d'entrée du programme
#
#   Remarque    : 
#
#   Dépendances :  + Nécessite python-psutil (apt-get install / dnf install)
#
#   Version     :   0.2.1
#
#   Date        :   31 aout 2021
#

import parameters
from paddingFolder import paddingFolder

# Classe dCleaner
#   Actions sur le dossier de remplissage
#
class dCleaner:
    # Données membre
    #
    color_  = None      # Gestion des sorties en mode terminal
    folder_ = None      # Mon dossier de remplissage
    fillRate_ = 0       # Taux de remplissage de la partition
    renewRate_ = 0      # Taux de rafraichissement de la zone "libre" de la partition

    # Construction
    def __init__(self, folderName, color, fillRate = parameters.DEF_PARTITION_FILL_RATE, renewRate = parameters.DEF_PADDING_RATE):
        # Initialisation des données membres
        if 0 == len(folderName):
            raise ValueError("Le nom doit être renseigné")

        # Création de l'objet pour la gestion du dossier
        self.folder_ = paddingFolder(folderName, self.color_)
        done, message = self.folder_.init()

        if False == done:
            # Erreur d'initialisation du dossier
            raise ValueError(message)

        self.color_ = color
        self.fillRate_ = fillRate
        self.renewRate_ = renewRate

    # Affichage des paramètres internes de l'objet
    def __repr__(self):
        
        res = self.folder_.partitionUsage()
    
        # Quelques informations ...
        #

        out = "\nParamètres : " 
        out += "\n\t- Taille de la partition : " + self.folder_.displaySize(res[0])
        out += "\n\t- Taux de remplissage max : " + str(self.fillRate_) + "%"
        out += "\n\t- Taux de renouvellement de la partition : " + str(self.renewRate_) + "%"        
        out += "\n\t- Attente entre 2 fichiers : " + str(self.folder_.elapseFiles()) + "s"
        out += "\n\t- Attente entre 2 traitements : " + str(self.folder_.elapseTasks()) + "s"

        out += "\n\nDossier : " 
        out += "\n\t- Nom : " + self.folder_.name()
        out += "\n\t- Contenu : " + self.folder_.displaySize(self.folder_.size())
        out += "\n\t- Remplissage de la partition : " + self.folder_.displaySize(res[1]) +  " = " + str(round(100*res[1]/res[0],2)) + "%"

        return out

    # Remplissage iniitial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def fillPartition(self):

        res = self.folder_.partitionUsage()
        maxFill = res[0] * parameters.DEF_PARTITION_FILL_RATE / 100

        if res[1] < maxFill:
            # On fait en sorte de coller immédiatement au taux de remplissage
            fillSize = maxFill - res[1]
            #print("Remplissage initial de", self.folder_.displaySize(fillSize))
            self.folder_.newFiles(fillSize)
            return True
        
        # La partition est déja "pleine"
        return False
        
    # Nettoyage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def freePartition(self):
        
        # Mode "initial" : on fait en sorte de coller immédiatement au taux de remplissage
        res = self.folder_.partitionUsage()
        maxFill = res[0] * parameters.DEF_PARTITION_FILL_RATE / 100
    
        if res[1] > maxFill:
            print(params.color_.colored("La partition est déja trop remplie", params.colors_.textColor.JAUNE))

            # en retirant les fichiers déja générés
            paddingSize = self.folder_.size()
            if (res[1] - paddingSize) > maxFill:
                print(params.color_.colored("Vidage du dossier de remplissage"))
                self.folder_.empty()
            else:
                # Retrait du "minimum"
                removeSize = res[1] - maxFill

                print("Suppression des fichiers de remplissage à hauteur de", self.folder_.displaySize(removeSize))
                self.folder_.deleteFiles(size=removeSize)
            
            return True

        # Rien n'a été fait
        return False

    # Rafraichissement - remplissage et nettoyage ponctuel
    def cleanPartition(self):
        
        # Taille en octets du volume à renouveller
        res = self.folder_.partitionUsage()
        
        # Valeur max. théorique
        renewSize = res[0] * (100 - self.fillRate_) / 100 * self.renewRate_ / 100 
        
        # on recadre avec l'espace effectivement dispo
        renewSize = self.folder_.minMax(0, renewSize, res[2] * self.renewRate_ / 100)        
        
        # On remplit 
        self.folder_.newFiles(renewSize)
        
        # On supprime
        self.folder_.deleteFiles(size = renewSize)
        
 
#
# Corps du programme
#
if '__main__' == __name__:
    
    # Ma ligne de commandes
    params = parameters.options()
    if False == params.parse():
        exit(1)

    try:    
        cleaner = dCleaner(params)

        print(cleaner)

        print("\nTraitements initiaux :")
        if False == cleaner.fillPartition():
            # Il faut plutôt libérer de la place
            cleaner.freePartition()

        # Maintenant traitement de "fond"
        print("\nTâches de fond :")
        cleaner.cleanPartition()

    except ValueError as e:
        print(params.color_.colored("Erreur de paramètre(s) : " + str(e), params.colors_.textColor.ROUGE))

# EOF