from qgis.core import QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsProject

from qgis.utils import iface
from PyQt5.QtCore import QVariant
import tempfile
import os

#La fonction CREATE_REGE_point : 
#créé la couche REGE_point récupère la régé dans le TERRAIN_point
#crée une nouvelle couche point avec, l'enregistre en gpkg et applique les styles



#crédit : Alexandre Le Bars

# ! utilisation hors de la console QGIS uniquement possible avec
#Kartenn !

# ! Pour commencer, selectionner votre couche 
# TERRAIN_point dans le panneau de couche !

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

def CREATE_REGE_point(layer, REGE_COLL=["Stade_jeun"]):
    # Créer une couche mémoire avec même type de géométrie et CRS
    geom_type = QgsWkbTypes.displayString(layer.wkbType())
    temp_layer = QgsVectorLayer(f"{geom_type}?crs={layer.crs().authid()}", "REGE_point", "memory")
    provider = temp_layer.dataProvider()


    # Ajouter uniquement les champs choisis qui existent dans la couche
    existing = {f.name(): i for i, f in enumerate(layer.fields())}
    kept_fields = [layer.fields()[existing[name]] for name in REGE_COLL if name in existing]
    provider.addAttributes(kept_fields)
    temp_layer.updateFields()

    new_feats = []
    for feat in layer.getFeatures():
        if any(feat[existing[name]] in (None, "", "NULL") for name in REGE_COLL if name in existing):
            continue  # on ne copie pas cette entité
        new_feat = QgsFeature(temp_layer.fields())
        new_feat.setGeometry(feat.geometry())

        attrs = []
        for name in REGE_COLL:
            if name in existing:
                val = feat[existing[name]]
                val = str(val).lower()
                attrs.append(val)
        new_feat.setAttributes(attrs)
        new_feats.append(new_feat)

    provider.addFeatures(new_feats)

    


    if temp_layer.isValid():
        QgsProject.instance().addMapLayer(temp_layer)
        print(f"Copie ajoutée au projet : {temp_layer}")
        # Appliquer un style
        style_path = os.path.join(r"C:\Users\alexl\CDF Dropbox\COCHERY Expertise et Gestion forestiere\SIG\SIG Alexandre\SIG_style\REGE_point.qml")
        if os.path.exists(style_path):
            temp_layer.loadNamedStyle(style_path)
            temp_layer.triggerRepaint()
            print("Style appliqué.")

        else:
            print("Pas de style trouvé, couche ajoutée avec style par défaut.")
    else:
        print("erreur.")
    

CREATE_REGE_point(layer,REGE_COLL =["Stade_jeun"] )
