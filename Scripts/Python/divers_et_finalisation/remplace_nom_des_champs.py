from qgis.core import QgsFields
from PyQt5.QtCore import QVariant
from qgis.utils import iface

#Pour remplacer une partie d'un nom de champs dans tout les champs : 

#select votre couche dans la panneau des couches 




remplace = "true" # <==== taper a la place du "" et entre "" ce que vous voulez remplacer
par = "" # <==== taper ici ce que vous voulez mettre à la place

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

layer.startEditing()



fields = layer.fields()

new_fields = QgsFields()

for field in layer.fields():
    old_name = field.name()
    new_name = old_name.replace(remplace, par)
    if new_name != old_name:  # seulement si changement
        idx = layer.fields().indexFromName(old_name)
        layer.renameAttribute(idx, new_name)

layer.updateFields()

print ("Traitement terminé")
