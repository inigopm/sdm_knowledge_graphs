import json
from pathlib import Path
import pandas as pd

metrics_list = []

base_dir = Path("C/C3_experiments")
for exp_dir in base_dir.iterdir():
    metrics_file = exp_dir / "metrics.json"
    if metrics_file.exists():
        with open(metrics_file) as f:
            metrics = json.load(f)
        try:
            m = metrics["both"]["realistic"]
            metrics_list.append({
                "experiment": exp_dir.name,
                "hits@10": m["hits_at_10"],
                "hits@5": m["hits_at_5"],
                "hits@3": m["hits_at_3"],
                "hits@1": m["hits_at_1"],
                "MMR": m["harmonic_mean_rank"],
                "MeanRank": m["arithmetic_mean_rank"]
            })
        except KeyError:
            print(f"Missing metrics in {metrics_file}")

df = pd.DataFrame(metrics_list)
df.to_csv("C/C3_experiments_summary.csv", index=False)
print(df)