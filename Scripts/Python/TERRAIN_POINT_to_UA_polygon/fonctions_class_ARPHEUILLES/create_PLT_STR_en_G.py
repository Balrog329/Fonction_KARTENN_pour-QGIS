from qgis.core import QgsField,QgsVectorLayer
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())


def build_PLT_STR(layer, target_col="PLT_STR"):

    # Vérifier que la colonne cible existe
    if target_col not in [f.name() for f in layer.fields()]:
        layer.dataProvider().addAttributes([QgsField(target_col, QVariant.String)])
        layer.updateFields()

    layer.startEditing()
    target_idx = layer.fields().indexFromName(target_col)

    for feat in layer.getFeatures():
        gtot = float(feat["Gtot_BABO"]) if feat["Gtot_BABO"] not in (None, "") else 0

        gpb = (float(feat["G_PB"] or 0)) *100/gtot if gtot else 0
        gbm = (float(feat["G_BM"] or 0)) *100/gtot if gtot else 0
        ggb = (float(feat["G_GB"] or 0) + float(feat["G_TGB"] or 0)) *100/gtot if gtot else 0

        STR_pair = [("GB", ggb), ("BM", gbm), ("PB", gpb)]

        inter = []
        strong = []


        for stru, pct_val in STR_pair :

            if pct_val is None or pct_val == 0: #cas des "NULL"
                continue

            if pct_val is not None and pct_val <10 : #on en tient pas compte de l'essence sous ce seuil
                continue
            elif pct_val < 30: # limite du "avec"
                inter.append(stru)
            else:
                strong.append(stru)
        str_list = strong[:]
        if inter:
            str_list.append("(" + "-".join(inter) + ")")

        plt_str_final = "-".join(str_list) if str_list else None

        layer.changeAttributeValue(feat.id(), target_idx, plt_str_final)

    layer.commitChanges()

    print("PLT_STR basé sur G Terminé")       

build_PLT_STR(layer, target_col="PLT_STR")
    

