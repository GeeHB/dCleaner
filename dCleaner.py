# coding=UTF-8
#
#   Fichier     :   dCleaner.py
#
#   Auteur      :   JHB
#
#   Description :   Point d'entrée du programme
#
#   Remarque    : 
#
#   Version     :   0.1.2
#
#   Date        :   6 février 2020
#

#import os, random, datetime
from paddingFolder import paddingFolder

#
# Valeurs par défaut
#
DEF_PARTITION_FILL_RATE = 75    # Pourcentage de remplissage max. de la partition
DEF_PADDING_RATE = 30           # Dans le % restant, quelle est le taux de renouvellement (ie ce pourcentage sera nettoyé à chaque lancement)

# Classe dCleaner
#   Actions sur le dossier de remplissage
#
class dCleaner:
    # Données membre
    #
    folder_ = None      # Mon dossier de remplissage
    fillRate_ = 0       # Taux de remplissage de la partition
    renewRate_ = 0      # Taux de rafraichissement de la zone "libre" de la partition

    # Construction
    def __init__(self, folderName, fillRate = DEF_PARTITION_FILL_RATE, renewRate = DEF_PADDING_RATE):
        # Initialisation des données membres
        if 0 == len(folderName):
            raise ValueError("Le nom doit être renseigné")

        # Création de l'objet pour la gestion du dossier
        self.folder_ = paddingFolder(folderName)
        done, message = self.folder_.init()

        if False == done:
            # Erreur d'initialisation du dossier
            raise ValueError(message)

        self.fillRate_ = fillRate
        self.renewRate_ = renewRate

    # Affichage des paramètres internes de l'objet
    def __repr__(self):
        
        res = self.folder_.partitionUsage()
    
        # Quelques informations ...
        out = "Dossier : " 
        out += "\n\t- Nom : " + self.folder_.name()
        out += "\n\t- Contenu : " + self.folder_.displaySize(self.folder_.size())
        out += "\n\t- Remplissage de la partition : " + self.folder_.displaySize(res[1]) +  " = " + str(round(100*res[1]/res[0],2)) + "%"

        out += "\nParamètres : " 
        out += "\n\t- Taille de la partition : " + self.folder_.displaySize(res[0])
        out += "\n\t- Taux de remplissage max : " + str(self.fillRate_) + "%"
        out += "\n\t- Taux de renouvellement de la partition : " + str(self.renewRate_) + "%"

        return out

    # Remplissage iniitial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def fillPartition(self):

        res = self.folder_.partitionUsage()
        maxFill = res[0] * DEF_PARTITION_FILL_RATE / 100

        if res[1] < maxFill:
            # On fait en sorte de coller immédiatement au taux de remplissage
            fillSize = maxFill - res[1]
            print("Remplissage initial de", self.folder_.displaySize(fillSize))
            self.folder_.newFiles(fillSize)
            return True
        
        # La partition est déja "pleine"
        return False
        
    # Nettoyage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def freePartition(self):
        
        # Mode "initial" : on fait en sorte de coller immédiatement au taux de remplissage
        res = self.folder_.partitionUsage()
        maxFill = res[0] * DEF_PARTITION_FILL_RATE / 100
    
        if res[1] > maxFill:
            print("La partition est déja trop remplie")

            # en retirant les fichiers déja générés
            paddingSize = self.folder_.size()
            if (res[1] - paddingSize) > maxFill:
                print("Vidage du dossier de remplissage")
                self.folder_.empty()
            else:
                # Retrait du "minimum"
                removeSize = res[1] - maxFill

                print("Suppression des fichiers de remplissage pour ", self.folder_.displaySize(removeSize))
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
        
        # on recadre avec l'espce effectivement dispo
        renewSize = self.folder_.minMax(0, renewSize, res[2] * self.renewRate_ / 100)        
        
        # On supprime
        self.folder_.deleteFiles(size = renewSize)
        
        # On remplit 
        self.folder_.newFiles(renewSize)
        
 
#
# Corps du programme
#

try:
    cleaner = dCleaner("/home/jhb/padding")

    print(cleaner)

    # Lancement => traitements initiaux
    if False == cleaner.fillPartition():
        # Il faut plutôt libérer de la place
        cleaner.freePartition()

    # Maintenant traitement de "fond"
    cleaner.cleanPartition()

except ValueError as e:
    print("Erreur ",e)

"""
if True == done:
    

    res = folder.partitionUsage()
    
   

    # Maintenant que le disque a le taux de remplissage souhaité, on nettoye ce qui reste
    renewSize = folder.minMax(0, renewSize, res[2] * DEF_PADDING_RATE / 100)
else:
    # Une erreur quelconque
    print(msg)
"""
# EOF