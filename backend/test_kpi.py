from kpi_engine import calculate_kpis
import json

result = calculate_kpis()
print(json.dumps(result, indent=2, default=str))