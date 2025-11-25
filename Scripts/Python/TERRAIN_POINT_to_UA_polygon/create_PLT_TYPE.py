from qgis.core import QgsField
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer = iface.activeLayer()

print("Valide :", layer.isValid())
print("Editable :", layer.isEditable())
print("Provider :", layer.providerType())
print("ReadOnly :", layer.readOnly())

def classify_PLT_TYPE():
    provider = layer.dataProvider()
    fields = layer.fields()

    layer.startEditing()

    # Ajout des champs si absents
    if "PLT_TYPE" not in [f.name() for f in fields]:
        provider.addAttributes([QgsField("PLT_TYPE", QVariant.String)])
    if "DENSITY_CLASS" not in [f.name() for f in fields]:
        provider.addAttributes([QgsField("DENSITY_CLASS", QVariant.String)])

    layer.updateFields()

    for feat in layer.getFeatures():
        plt_type = feat["PLT_TYPE"] if "PLT_TYPE" in [f.name() for f in fields] else "FF"
        densite = feat["Tai_den"]
        g_total = feat["Gtot_BABO"]

        def classify_density(g_total):
            if g_total >= 20: return "1"
            elif 15 <= g_total < 20: return "2"
            elif 10 <= g_total < 15: return "3"
            elif 5 <= g_total < 10: return "4"
            elif 1 <= g_total < 5: return "5"
            else: return ""

        def add_NB(plt_type_str, density):
            if plt_type_str.endswith("5"):
                return plt_type_str.replace("5", "NB/T")
            return plt_type_str

        # Transformation FT si conditions
        if plt_type == "FF" and densite in ["d", "md"]:
            plt_type = "FT"

        density_class = classify_density(g_total)
        plt_type_final = add_NB(f"{plt_type}{density_class}", densite)


        layer.changeAttributeValue(feat.id(), layer.fields().indexFromName("PLT_TYPE"), plt_type_final)
        layer.changeAttributeValue(feat.id(), layer.fields().indexFromName("DENSITY_CLASS"), density_class)

    layer.commitChanges()
    print("terminé")

classify_PLT_TYPE()

