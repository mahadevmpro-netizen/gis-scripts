from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes

for layer in QgsProject.instance().mapLayers().values():
    if not isinstance(layer, QgsVectorLayer):
        continue
    print("LAYER:", layer.name())
    print("  Geometry:", QgsWkbTypes.displayString(layer.wkbType()))
    print("  CRS:", layer.crs().authid())
    print("  Features:", layer.featureCount())
    for f in layer.fields():
        print("   -", f.name(), "|", f.typeName(), "| length", f.length())
    print()