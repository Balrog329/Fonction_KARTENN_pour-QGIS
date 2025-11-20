from qgis.core import QgsVectorLayer, QgsField, QgsFeature, edit
from qgis.utils import iface
from PyQt5.QtCore import QVariant

#La fonction SUPP 0 : 
#Supprime les 0 dans la couche SSPF avant les numéro de sous parcelles 
#et met a jour le champ PARFOR.


#crédit : Alexandre Le Bars

# ! utilisation hors de la console QGIS uniquement possible avec
#Kartenn !

# ! Pour commencer, selectionner votre couche 
# SSPF_polygon dans le panneau de couche !

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

def kill_0(layer,parfor_coll=["PARFOR","N_PARFOR"]):
    layer.startEditing()
    field = [f.name() for f in layer.fields()]
    target_field = [f for f in parfor_coll if f in field]

    for feat in layer.getFeatures() :
        for field in target_field:
            values = feat[field]
            new_value = values.replace("0","")
            layer.changeAttributeValue(feat.id(), layer.fields().indexFromName(field), new_value)
    print("traitement termniné les 0 ont été supprimés")
    layer.commitChanges()
    print(f"Colonne {parfor_coll} mise à jour.")
kill_0(layer,parfor_coll=["PARFOR","N_PARFOR"])
