from qgis.core import QgsField,QgsVectorLayer
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

dmpb = 22.5 # diamètre moyen des PB
dmbm = 32.5 # diamètre moyen des BM

if "G_TGB" in layer.fields().names():
    dmgb = 57.5 # diamètre moyen des GB 
    dmtgb = 75 # diamètre moyen des TGB  
else : 
    dmgb = 62.5 # diamètre moyen si les TGB sont inclus dans les GB
    dmtgb = 0

#Logique de calcul pour le poid d'un bois en fonction de son diamètre moyen
 
ppb = ((dmpb/2/100)**2)*3.141592653589793
print(f"Le poid d'un PB est : {ppb} m²")
pbm = ((dmbm/2/100)**2)*3.141592653589793
print(f"Le poid d'un BM est : {pbm} m²")

if dmtgb == 0 :
    pgb= (((dmgb/2/100)**2)*3.141592653589793) + (((dmtgb/2/100)**2)*3.141592653589793)
    print(f"Le poid d'un GB est : {pgb} m²")

if dmtgb >0 :

    pgb= (((dmgb/2/100)**2)*3.141592653589793)
    print(f"Le poid d'un GB est : {pgb} m²")
    ptgb= ((dmtgb/2/100)**2)*3.141592653589793
    print(f"Le poid d'un TGB est : {ptgb} m²")


def build_PLT_STR(layer, target_col="PLT_STR", str_dens="PLT_STR_NHA", concat_dens="PLT_REP_NHA", plt_dens="PLT_NHA", plt_dm="PLT_DM"):

    # Champs à créer si absents
    fields_to_add = [target_col, str_dens, concat_dens, plt_dens, plt_dm]

    # Vérifier et créer les champs manquants
    existing = [f.name() for f in layer.fields()]
    new_fields = [QgsField(name, QVariant.String) for name in fields_to_add if name not in existing]

    if new_fields:
        layer.dataProvider().addAttributes(new_fields)
        layer.updateFields()

    # Récupérer les index des champs
    idx_PLT_STR = layer.fields().indexFromName(target_col)
    target_str_dens = layer.fields().indexFromName(str_dens)
    target_plt_dens = layer.fields().indexFromName(plt_dens)
    target_concat_dens = layer.fields().indexFromName(concat_dens)
    target_plt_dm = layer.fields().indexFromName(plt_dm)

    layer.startEditing()


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

        layer.changeAttributeValue(feat.id(), idx_PLT_STR, plt_str_final)



        #===Calcul des densités par catégories===


        dpb = (float(feat["G_PB"] or 0)) / ppb if ppb else 0
        dbm = (float(feat["G_BM"] or 0)) / pbm if pbm else 0
        dgb = (float(feat["G_GB"] or 0)) / pgb if pgb else 0

        dtgb = 0
        if dmtgb > 0:
            dtgb = (float(feat["G_TGB"] or 0)) / ptgb if ptgb else 0

        # Calcul de la densité globale
        Nha = dpb + dbm + dgb + dtgb

        # Calcul des pourcentages (évite division par zéro)
        pct_pbnha = int(round(dpb *100/ Nha if Nha else 0))
        pct_bmnha = int(round(dbm *100/ Nha if Nha else 0))
        pct_gbnha = int(round(dgb *100/ Nha if Nha else 0))
        pct_tgbnha = int(round(dtgb *100/ Nha if (Nha and dtgb > 0) else 0))

        # Concaténation finale
        concat_dens_final = (
            f"PB:{pct_pbnha}%-BM:{pct_bmnha}%-GB:{pct_gbnha}%"
            + (f"-TGB:{pct_tgbnha:.2f}%" if pct_tgbnha > 0 else ""))

        # Mise à jour du champ

        layer.changeAttributeValue(feat.id(), target_concat_dens, concat_dens_final)


    #===calcul du PLT_STR selon NHA===


        pct_tgb_gb_nha = (pct_gbnha if pct_gbnha else 0)+ ((pct_tgbnha if pct_tgbnha else 0))


        NSTR_pair = [("GB", pct_tgb_gb_nha), ("BM", pct_bmnha), ("PB", pct_pbnha)]

        Ninter = []
        Nstrong = []


        for Nstru, Npct_val in NSTR_pair :

            if Npct_val is None or Npct_val == 0: #cas des "NULL"
                continue

            if Npct_val is not None and Npct_val <10 : #on en tient pas compte de l'essence sous ce seuil
                continue
            elif Npct_val < 30: # limite du "avec"
                Ninter.append(Nstru)
            else:
                Nstrong.append(Nstru)
        Nstr_list = Nstrong[:]
        if Ninter:
            Nstr_list.append("(" + "-".join(Ninter) + ")")

        Nplt_str_final = "-".join(Nstr_list) if Nstr_list else None

        layer.changeAttributeValue(feat.id(), target_str_dens, Nplt_str_final)

    #===Calcul de N/ha par point===


        Nha_final = int(round(Nha))

        layer.changeAttributeValue(feat.id(), target_plt_dens, Nha_final)

    #===Calcul du DM===

        dm_final = round(((dmpb*dpb) + (dmbm*dbm) + (dmgb*dgb) + (dmtgb*dtgb)) / Nha if Nha else 0, 2)

        layer.changeAttributeValue(feat.id(), target_plt_dm,dm_final)


    layer.commitChanges()

    print(f"La collone {target_col} à été mise à jour ")
    print(f"La collone PLT_REP_NHA à été mise à jour")
    print("Calcul de PLT_STR basé sur N/ha terminé")
    print("Calcul du champs PLT_NHA (par point) terminé")
    print ("Calcul du diamètre moyen par point terminé")
    print("Traitement terminé")       

build_PLT_STR(layer, target_col="PLT_STR", str_dens="PLT_STR_NHA", concat_dens="PLT_REP_NHA", plt_dens="PLT_NHA", plt_dm="PLT_DM")
    

