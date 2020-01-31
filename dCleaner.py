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
#   Version     :   0.1.1
#
#   Date        :   29 janvier 2020
#

import os, random, datetime
from paddingFolder import paddingFolder


#
# Corps du programme
#
folder = paddingFolder("/home/jhb/padding")
done, msg = folder.init()
if True == done:
    #print(folder.newFile(20480))
    #print(folder.empty())
    print(folder.partitionUsage())
    #print(folder.displaySize(123456789123410))
else:
    print(msg)


# EOF