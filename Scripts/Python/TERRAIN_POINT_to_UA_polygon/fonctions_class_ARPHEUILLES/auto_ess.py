from qgis.core import QgsField,QgsVectorLayer
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

def classify_PLT_ESS():
    provider = layer.dataProvider()
    fields = layer.fields()

    layer.startEditing()

    # Ajout des champs si absents
    if "PLT_ESS" not in [f.name() for f in fields]:
        provider.addAttributes([QgsField("PLT_ESS", QVariant.String)])

    target_col = "PLT_ESS"
    target_idx = layer.fields().indexFromName(target_col)



    layer.updateFields()

    for feat in layer.getFeatures():
        gtot = float(feat["Gtot_BABO"]) if feat["Gtot_BABO"] not in (None, "") else 0


        alt = (float(feat["GBO_ALT"] or 0) + float(feat["GBA_ALT"] or 0))*100/gtot if gtot else 0
        che = (float(feat["GBO_CHE"] or 0) + float(feat["GBA_CHE"]or 0))*100/gtot if gtot else 0
        chp = (float(feat["GBO_CHP"]or 0) + float(feat["GBA_CHP"] or 0))*100/gtot if gtot else 0
        chs = (float(feat["GBO_CHS"] or 0) + float(feat["GBA_CHS"]or 0))*100/gtot if gtot else 0
        cor = (float(feat["GBO_COR"] or 0)) *100/gtot if gtot else 0
        erc = (float(feat["GBO_ERC"] or 0) + float(feat["GBA_ERC"]or 0))*100/gtot if gtot else 0
        fre = (float(feat["GBO_ERC_1"] or 0) + float(feat["GBA_FRE"]or 0))*100/gtot if gtot else 0
        het = (float(feat["GBO_HET"] or 0) + float(feat["GBA_HET"]or 0))*100/gtot if gtot else 0
        tre = (float(feat["GBO_TRE"]or 0)) *100/gtot if gtot else 0

        plt_ess = feat["PLT_ESS"]

        ess_pair = [
            ("ALT", alt),
            ("CHE", che),
            ("CHP", chp),
            ("CHS", chs),
            ("COR", cor),
            ("ERC", erc),
            ("FRE", fre),
            ("HET",het),
            ("TRE", tre)
        ]

        ess_list = []

        ess_pairs_sorted = sorted(ess_pair, key=lambda x: x[1], reverse=True)

        for ess, pct_val in ess_pairs_sorted :

            if pct_val is None or pct_val == 0:
                continue
            #à noter si moins de 10% pas essence
            
            # avec = 10 à 30% de G
            if pct_val is not None and pct_val <10 :
                ess_list.append("")
            elif pct_val is not None and pct_val < 30 :
                ess_list.append(f"({ess})")
            else:
                ess_list.append(str(ess))

        
        # Concaténer uniquement si au moins une essence existe
        if ess_list:
            plt_ess_final = "-".join(ess_list)

        else:
            feat[target_col] = None


        layer.changeAttributeValue(feat.id(), target_idx, plt_ess_final)

    layer.commitChanges()

    print("Terminé")

classify_PLT_ESS()


