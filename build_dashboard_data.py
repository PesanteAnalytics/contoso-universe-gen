"""
Aggregate FactSales CSV into yearly KPI JSON for the dashboard.
Run: python build_dashboard_data.py
Output: output/dashboard_data.json
"""
import csv, json, pathlib, collections

CSV_PATH = "output/csv/FactSales.csv"
OUT_PATH  = "output/dashboard_data.json"

def main():
    yearly = collections.defaultdict(lambda: {
        "sales": 0.0, "cost": 0.0, "qty": 0, "orders": 0
    })

    print("Reading CSV…")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = row["OrderDate"][:4]
            qty  = int(row["Quantity"])
            net  = float(row["NetPrice"])
            cost = float(row["UnitCost"])
            yearly[year]["sales"]  += net * qty
            yearly[year]["cost"]   += cost * qty
            yearly[year]["qty"]    += qty
            yearly[year]["orders"] += 1

    result = {}
    years = sorted(yearly.keys())
    for y in years:
        d = yearly[y]
        margin     = d["sales"] - d["cost"]
        margin_pct = (margin / d["sales"] * 100) if d["sales"] else 0
        cost_pct   = (d["cost"] / d["sales"] * 100) if d["sales"] else 0
        avg_sales  = d["sales"] / d["orders"] if d["orders"] else 0
        avg_cost   = d["cost"]  / d["orders"] if d["orders"] else 0
        avg_qty    = d["qty"]   / d["orders"] if d["orders"] else 0
        result[y] = {
            "sales":      round(d["sales"],  2),
            "cost":       round(d["cost"],   2),
            "qty":        d["qty"],
            "orders":     d["orders"],
            "margin":     round(margin,     2),
            "margin_pct": round(margin_pct, 2),
            "cost_pct":   round(cost_pct,   2),
            "avg_sales":  round(avg_sales,  2),
            "avg_cost":   round(avg_cost,   2),
            "avg_qty":    round(avg_qty,    2),
        }

    pathlib.Path(OUT_PATH).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Written → {OUT_PATH}")

    # Print quick summary
    total_sales = sum(v["sales"] for v in result.values())
    total_qty   = sum(v["qty"]   for v in result.values())
    print(f"Total Sales: ${total_sales/1e6:.1f}M   Total Qty: {total_qty/1e6:.1f}M")

if __name__ == "__main__":
    main()
