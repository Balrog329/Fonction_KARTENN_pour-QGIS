from qgis.core import QgsField,QgsVectorLayer
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())


def build_PLT_TSE(layer, pct_cols1=["Ess_bc_bd%"], pct_cols2=["Ess_bc_bb"],
                  dens_col="Tai_den", exp_col="Tai_expl", target_col="PLT_TSE"):
    
    # Vérifier que la colonne cible existe, sinon la créer
    if target_col not in [f.name() for f in layer.fields()]:
        layer.dataProvider().addAttributes([QgsField(target_col, QVariant.String)])
        layer.updateFields()

    
    layer.startEditing()

    target_idx = layer.fields().indexFromName(target_col)

    for feat in layer.getFeatures():

        dominant = None


        for pct_col in pct_cols1:
            if pct_col in feat.fields().names():
            
                pct = feat[pct_col]

                if pct is None or str(pct).strip().upper() in ["", "NULL", "NONE"]:
                    continue

        for pct_col2 in pct_cols2:
            if pct_col2 in feat.fields().names():
            
                pct2 = feat[pct_col2]

                if pct2 is None or str(pct2).strip().upper() in ["", "NULL", "NONE"]:
                    continue

                # Conversion pct_val en int + comparaisont
                pct_val = int(str(pct).replace("%", "").strip())
                pct_val2 = int(str(pct2).replace("%", "").strip())

                if pct_val is not None or pct_val2 is not None :
                    if pct_val > pct_val2 :
                        dominant = str("BD")
                    elif pct_val2 > pct_val :

                        dominant = str("BB")

            print("Feature", feat.id(), pct, pct2)

        #récupération densité et exploitabilité
        dens = str(feat[dens_col]) if feat[dens_col] is not None else ""
        expl = str(feat[exp_col]) if feat[exp_col] is not None else ""

        
        if dens == "pd":
            densi = "3"
        elif dens == "md":
            densi = "2"
        elif dens == "d":
            densi = "1"
        else : densi =""
        
        if expl == "ne":
            exploi = "c"
        elif expl =="ie":
            exploi = "b"
        elif expl == "e":
            exploi = "a"
        else : exploi = ""
        



        

        if dominant : 
            plt_tse = f"{dominant}-T{densi}{exploi}"
        else : plt_tse = None

        layer.changeAttributeValue(feat.id(), target_idx, plt_tse)

    layer.commitChanges()

    print(f"Colonne {target_col} mise à jour.")

build_PLT_TSE(layer, pct_cols1=["Ess_bc_bd%"], pct_cols2=["Ess_bc_bb"],dens_col="Tai_den", exp_col="Tai_expl", target_col="PLT_TSE")