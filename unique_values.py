from qgis.core import QgsProject, QgsVectorLayer

TARGET = ["infrastructure_lines", "infrastructure_points",
          "road-areas", "study_area", "traffic_signs"]
seen = set()

for layer in QgsProject.instance().mapLayers().values():
    if not isinstance(layer, QgsVectorLayer):
        continue
    match = [t for t in TARGET if layer.name().endswith(t)]
    if not match or match[0] in seen:
        continue
    seen.add(match[0])
    print("LAYER:", match[0])
    for i, f in enumerate(layer.fields()):
        if f.name() == "fid":
            continue
        values = layer.uniqueValues(i)
        shown = sorted(values, key=str)[:10]
        print("  ", f.name(), "->", shown)
    print()
