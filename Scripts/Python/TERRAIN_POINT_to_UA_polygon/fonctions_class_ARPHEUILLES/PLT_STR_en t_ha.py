from qgis.core import QgsField,QgsVectorLayer
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())


def build_PLT_STR(layer, target_col="PLT_STR_T_HA"):

    # Vérifier que la colonne cible existe
    if target_col not in [f.name() for f in layer.fields()]:
        layer.dataProvider().addAttributes([QgsField(target_col, QVariant.String)])
        layer.updateFields()

    layer.startEditing()
    target_idx = layer.fields().indexFromName(target_col)

    for feat in layer.getFeatures():

        pct_npb = (feat["%_PB"])
        pct_nbm = (feat["%BM"])
        pct_ngb = (feat["%GBTGB"])

        if pct_npb is None or str(pct_npb).strip().upper() in ["", "NULL", "NONE"]:
            continue
        if pct_nbm is None or str(pct_nbm).strip().upper() in ["", "NULL", "NONE"]:
            continue
        if pct_ngb is None or str(pct_ngb).strip().upper() in ["", "NULL", "NONE"]:
            continue
        

        # Conversion pct_val en int + comparaisont
        npb = int(float(str(pct_npb).replace("%", "").replace(",",".").strip()))
        nbm = int(float(str(pct_nbm).replace("%", "").replace(",",".").strip()))
        ngb = int(float(str(pct_ngb).replace("%", "").replace(",",".").strip()))

        STR_pair = [("GB", ngb), ("BM", nbm), ("PB", npb)]

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

    print("PLT_STR basé sur N/ha Terminé")       

build_PLT_STR(layer, target_col="PLT_STR_T_HA")