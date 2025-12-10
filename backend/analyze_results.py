import sys

import pandas as pd


def main(path: str) -> None:
    df = pd.read_csv(path)

    print("Columns:", list(df.columns))

    # Adjust these if your exporter uses different names
    area_col = "area_sqft"
    type_col = "type"  # e.g. 'concrete', 'asphalt', 'building', 'pervious'

    if area_col not in df.columns or type_col not in df.columns:
        print("\nExpected columns not found. Available columns:")
        for c in df.columns:
            print(" -", c)
        return

    total_area = df[area_col].sum()
    print(f"\nTotal area (sf): {total_area:,.2f}")

    print("\nArea by type (sf):")
    by_type = df.groupby(type_col)[area_col].sum().sort_values(ascending=False)
    for t, a in by_type.items():
        print(f" - {t}: {a:,.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_results.py <path_to_results_csv>")
        sys.exit(1)

    main(sys.argv[1])
