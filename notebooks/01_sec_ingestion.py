import pandas as pd

files = {
    2023: "data/raw/sec_filings/AMZN_2023.html",
    2022: "data/raw/sec_filings/AMZN_2022.html"
}

segments = ["North America", "International", "AWS"]

final_data = []

for year, file_path in files.items():
    print(f"\nProcessing {year}...")

    tables = pd.read_html(file_path)
    print(f"Tables found: {len(tables)}")

    segment_table = None

    # Find correct table
    for i, table in enumerate(tables):
        table_str = table.astype(str).to_string().lower()

        if (
            all(seg.lower() in table_str for seg in segments)
            and ("net sales" in table_str or "operating income" in table_str)
        ):
            segment_table = table
            print(f"✅ Correct segment table found at index {i}")
            break

    if segment_table is None:
        print(f"❌ No valid segment table found for {year}")
        continue

    print(segment_table.head())

    # Reset columns
    segment_table.columns = range(segment_table.shape[1])
    table_str_df = segment_table.astype(str)

    # Find column containing target year
    target_col = None

    for col in segment_table.columns:
       col_text = " ".join([str(x) for x in table_str_df[col]]).lower()

        if str(year) in col_text:
            target_col = col

    if target_col is None:
        print(f"❌ No column found for year {year}")
        continue

    print(f"Using column {target_col} for {year}")

    # Extract values
    for _, row in segment_table.iterrows():
        row_clean = [str(x) for x in row if pd.notna(x)]
        row_text = " ".join(row_clean).lower()

        for seg in segments:
            if seg.lower() in row_text:

                val = str(row[target_col]).replace(",", "").replace("$", "").strip()

                if "(" in val and ")" in val:
                    val = "-" + val.replace("(", "").replace(")", "")

                try:
                    num = float(val)

                    # Only keep meaningful financial values
                    if abs(num) > 1000:
                        final_data.append({
                            "year": year,
                            "segment": seg,
                            "value": num
                        })

                except:
                    continue

df = pd.DataFrame(final_data)

print("\nFinal Data:")
print(df)

df.to_csv("data/interim/extracted_tables/segment_structured.csv", index=False)