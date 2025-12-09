
#Fusionne les entités de la couche active ayant la même valeur
#dans le champ indiqué , sauf si cette valeur est NULL.
    
#param champ_nom: Nom du champ utilisé pour regrouper les entités
# Les champs NULL sont fusionné entre eux !!

#selectionnez votre couche dans le panneau des couches

#executez le script

#Crédit Alexandre Le Bars


champ_nom = "" #Indiquez le nom du champs qui comporte le nom 


from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsField,
    QgsVectorLayerUtils, 
)
from qgis.utils import iface

def fusionner_par_champ(champ_nom: str):

    # Récupérer la couche active

    couche = iface.activeLayer()
    if not couche or not isinstance(couche, QgsVectorLayer):
        raise Exception("Aucune couche vectorielle active.")

    idx = couche.fields().indexFromName(champ_nom)
    if idx == -1:
        raise Exception(f"Le champ '{champ_nom}' n'existe pas dans la couche.")

    groupes = {}

    for feat in couche.getFeatures():
        valeur = feat[champ_nom]
        if valeur is None:
            continue
        if valeur not in groupes:
            groupes[valeur] = []
        groupes[valeur].append(feat)

    couche.startEditing()

    for valeur, features in groupes.items():
        if len(features) < 2:
            continue

        # Fusion des géométries
        geometries = [f.geometry() for f in features]
        geom_fusion = QgsGeometry.unaryUnion(geometries)
        print(valeur)

        # Supprimer les anciennes entités
        ids = [f.id() for f in features]
        couche.deleteFeatures(ids)

        # Créer une nouvelle entité avec les attributs conservés
        new_feat = QgsFeature(couche.fields())
        new_feat.setGeometry(geom_fusion)

        for i, field in enumerate(couche.fields()):
            if field.name() == champ_nom:
                new_feat.setAttribute(i, valeur)
            else:
                # Prendre la première valeur non NULL
                for f in features:
                    val = f[i]
                    if val is not None:
                        new_feat.setAttribute(i, val)
                        break

        couche.addFeature(new_feat)

    couche.commitChanges()

    print("Fusion terminée avec succès.")

fusionner_par_champ(champ_nom)