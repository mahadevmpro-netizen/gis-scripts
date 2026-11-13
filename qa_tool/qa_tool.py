
"""
NORDHAVEN GIS Quality Assurance Tool

Outputs:
    qa_report.csv
    qa_report.html

Usage:
    python qa_tool.py PATH_TO_GEOPACKAGE
"""

import sys
import json
from pathlib import Path
from datetime import datetime

import geopandas as gpd
import pandas as pd


def load_config():
    """Read QA rules from the external JSON file."""

    config_path = Path(__file__).with_name("config.json")

    if not config_path.exists():
        print("Configuration file not found:", config_path)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)

        print("Configuration loaded:", config_path.name)
        return config

    except json.JSONDecodeError as error:
        print("Invalid JSON configuration:", error)
        sys.exit(1)


def check_layer(gdf, cfg):
    """Run validation checks on one GeoDataFrame."""

    results = []

    results.append((
        "Missing or empty geometry",
        int((gdf.geometry.isna() | gdf.geometry.is_empty).sum())
    ))

    results.append((
        "Invalid geometry",
        int((~gdf.geometry.is_valid).sum())
    ))

    if gdf.geom_type.isin(["LineString", "MultiLineString"]).all():
        results.append((
            "Lines shorter than 1 m",
            int((gdf.length < 1).sum())
        ))

    id_field = cfg["id_field"]

    results.append((
        "Duplicate " + id_field,
        int(gdf[id_field].duplicated(keep=False).sum())
    ))

    for col in cfg["required"]:
        results.append((
            "Empty " + col,
            int(gdf[col].isna().sum())
        ))

    for col, ok_values in cfg["allowed"].items():
        results.append((
            col + " not in allowed list",
            int((~gdf[col].isin(ok_values)).sum())
        ))

    return results


def run_qa(gpkg_path, layers_config):

    all_results = []

    for layer_name, cfg in layers_config.items():

        print("Checking:", layer_name)

        gdf = gpd.read_file(gpkg_path, layer=layer_name)

        for check, count in check_layer(gdf, cfg):

            all_results.append({
                "layer": layer_name,
                "check": check,
                "failures": count,
                "status": "PASS" if count == 0 else "FAIL"
            })

    return pd.DataFrame(all_results)


def create_html_report(report, output_path):
    """Create a browser-readable HTML QA report."""

    total_checks = len(report)
    failed_checks = int((report["status"] == "FAIL").sum())
    passed_checks = total_checks - failed_checks

    # Create a summary for each layer.
    summary_rows = []

    for layer_name, group in report.groupby("layer", sort=False):

        failed = int((group["status"] == "FAIL").sum())
        passed = len(group) - failed

        summary_rows.append({
            "Layer": layer_name,
            "Total checks": len(group),
            "Passed": passed,
            "Failed": failed,
            "Status": "PASS" if failed == 0 else "FAIL"
        })

    summary = pd.DataFrame(summary_rows)

    summary_html = summary.to_html(
        index=False,
        border=0,
        classes="report-table",
        escape=True
    )

    details_html = report.to_html(
        index=False,
        border=0,
        classes="report-table",
        escape=True
    )

    generated_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    overall_status = "PASS" if failed_checks == 0 else "FAIL"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>NORDHAVEN GIS QA Report</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f3f5f7;
            color: #263238;
            margin: 0;
            padding: 30px;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
        }}

        h1 {{
            color: #17365d;
            margin-bottom: 5px;
        }}

        h2 {{
            color: #17365d;
            margin-top: 35px;
        }}

        .meta {{
            color: #667085;
            font-size: 14px;
        }}

        .cards {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 25px 0;
        }}

        .card {{
            flex: 1;
            min-width: 150px;
            padding: 20px;
            background: #f3f5f7;
            border-radius: 8px;
        }}

        .number {{
            font-size: 28px;
            font-weight: bold;
        }}

        .pass {{
            color: #16803c;
        }}

        .fail {{
            color: #c62828;
        }}

        .report-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}

        .report-table th {{
            background: #17365d;
            color: white;
            text-align: left;
        }}

        .report-table th,
        .report-table td {{
            padding: 12px;
            border: 1px solid #dce1e6;
        }}

        .report-table tr:nth-child(even) {{
            background: #f3f5f7;
        }}

        .footer {{
            margin-top: 35px;
            padding-top: 15px;
            border-top: 1px solid #dce1e6;
            color: #667085;
            font-size: 12px;
        }}
    </style>
</head>

<body>

<div class="container">

    <h1>NORDHAVEN GIS Quality Assurance Report</h1>

    <p class="meta">
        Generated on: {generated_at}
    </p>

    <h2>Overall QA Summary</h2>

    <div class="cards">

        <div class="card">
            <div class="number">{total_checks}</div>
            Total checks
        </div>

        <div class="card">
            <div class="number pass">{passed_checks}</div>
            Passed
        </div>

        <div class="card">
            <div class="number fail">{failed_checks}</div>
            Failed
        </div>

        <div class="card">
            <div class="number">{overall_status}</div>
            Overall status
        </div>

    </div>

    <h2>Layer-wise Results</h2>

    {summary_html}

    <h2>Detailed Validation Results</h2>

    {details_html}

    <div class="footer">
        NORDHAVEN GIS QA Tool | Automated validation report
    </div>

</div>

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print("HTML report saved to:", output_path.resolve())


def main():

    if len(sys.argv) != 2:
        print("Usage: python qa_tool.py PATH_TO_GEOPACKAGE")
        sys.exit(1)

    gpkg_path = Path(sys.argv[1])

    if not gpkg_path.exists():
        print("File not found:", gpkg_path)
        sys.exit(1)

    layers_config = load_config()

    report = run_qa(gpkg_path, layers_config)

    print("\n----- QA RESULTS -----\n")

    for layer_name, group in report.groupby("layer", sort=False):

        failed = group[group["status"] == "FAIL"]

        status = "PASS" if failed.empty else "FAIL"

        print(
            f"{status}  {layer_name}: "
            f"{len(group) - len(failed)} of {len(group)} checks passed"
        )

        for _, row in failed.iterrows():
            print(f"        - {row['check']}: {row['failures']}")

    total = len(report)
    n_fail = int((report["status"] == "FAIL").sum())

    print(f"\n{total} checks: {total - n_fail} PASS, {n_fail} FAIL")

    # Save the CSV report.
    csv_path = Path("qa_report.csv")
    report.to_csv(csv_path, index=False)

    print("CSV report saved to:", csv_path.resolve())

    # Save the HTML report.
    html_path = Path("qa_report.html")
    create_html_report(report, html_path)

    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
