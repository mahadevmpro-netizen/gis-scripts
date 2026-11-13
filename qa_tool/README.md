
# NORDHAVEN GIS Quality Assurance Tool

A Python-based GIS quality assurance tool developed as part of my GIS Skills Sprint.

The tool uses GeoPandas and pandas to validate infrastructure data stored in a GeoPackage. Validation rules are maintained separately in a JSON configuration file.

## Project Overview

The tool checks five infrastructure layers:

- infrastructure_lines
- infrastructure_points
- road-areas
- study_area
- traffic_signs

It generates two reports:

- `qa_report.csv` – structured validation results.
- `qa_report.html` – formatted report for browser review.

## QA Checks

The tool performs checks for:

- Missing or empty geometry
- Invalid geometry
- Lines shorter than 1 metre (where applicable)
- Duplicate feature identifiers
- Empty required attributes
- Attribute values outside configured allowed lists

## Project Structure

```text
qa_tool/
│
├── qa_tool.py
├── config.json
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.12
- GeoPandas
- pandas

## Installation

Create and activate a Python environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

Open a terminal in the `qa_tool` folder and execute:

```bash
python qa_tool.py "PATH_TO_YOUR_GEOPACKAGE.gpkg"
```

Example:

```bash
python qa_tool.py "D:/GIS_Data/Nordhaven_Infrastructure.gpkg"
```

The GeoPackage must contain the five expected layers and the attribute fields referenced in `config.json`.

## Configuration

The `config.json` file stores:

- Layer names
- Identifier fields
- Required attributes
- Permitted attribute values

This separates validation rules from the Python processing logic. Rules can be updated in the JSON file without changing the Python code, provided the validation type is already supported by the script.

## Output

The tool generates:

| Output | Description |
|---|---|
| `qa_report.csv` | Detailed check results in tabular format |
| `qa_report.html` | Browser-readable QA report |

The terminal also displays the number of passed and failed checks for each layer.

The reports are saved in the current working directory.

## Demonstration Results

Using the NORDHAVEN demonstration GeoPackage:

**Clean dataset**
- 45 checks
- 45 PASS
- 0 FAIL

**Older backup dataset**
- 45 checks
- 44 PASS
- 1 FAIL
- Three invalid material values detected in the infrastructure_points layer.

These results demonstrate the tool's ability to identify attribute values that do not comply with configured validation rules.

## Data and Scope

NORDHAVEN is a demonstration infrastructure GIS dataset based on OpenStreetMap-derived context data for Bremerhaven, State of Bremen, Germany.

The QA tool is designed around the five NORDHAVEN layer schemas and their configured attribute rules. It is not a general-purpose validator for arbitrary GeoPackages without configuration and schema adjustments.

## Author

Mahadev M

GitHub: https://github.com/mahadevmpro-netizen
