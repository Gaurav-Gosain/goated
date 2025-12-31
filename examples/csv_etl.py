#!/usr/bin/env python3
"""CSV ETL (Extract, Transform, Load) patterns with goated."""

import io as pyio
from dataclasses import dataclass

from goated import Ok
from goated.std import csv, fmt, strings


@dataclass
class SalesRecord:
    date: str
    product: str
    quantity: int
    price: float
    region: str

    @property
    def total(self) -> float:
        return self.quantity * self.price


def parse_sales_csv(data: str) -> list[SalesRecord]:
    """Parse CSV data into SalesRecord objects."""
    reader = csv.NewReader(pyio.StringIO(data))
    records = []

    header_result = reader.Read()
    if header_result.is_err():
        return records

    for row_result in reader:
        match row_result:
            case Ok(row) if len(row) >= 5:
                records.append(
                    SalesRecord(
                        date=row[0],
                        product=row[1],
                        quantity=int(row[2]),
                        price=float(row[3]),
                        region=row[4],
                    )
                )
            case _:
                continue

    return records


def filter_by_region(records: list[SalesRecord], region: str) -> list[SalesRecord]:
    """Filter records by region (case-insensitive)."""
    return [r for r in records if strings.EqualFold(r.region, region)]


def aggregate_by_product(records: list[SalesRecord]) -> dict[str, float]:
    """Sum total sales by product."""
    totals: dict[str, float] = {}
    for r in records:
        key = strings.ToLower(r.product)
        totals[key] = totals.get(key, 0) + r.total
    return totals


def records_to_csv(records: list[SalesRecord]) -> str:
    """Convert records back to CSV."""
    buf = pyio.StringIO()
    writer = csv.NewWriter(buf)

    writer.Write(["date", "product", "quantity", "price", "region", "total"])

    for r in records:
        writer.Write(
            [
                r.date,
                r.product,
                str(r.quantity),
                fmt.Sprintf("%.2f", r.price),
                r.region,
                fmt.Sprintf("%.2f", r.total),
            ]
        )

    writer.Flush()
    return buf.getvalue()


def main():
    print("=== CSV ETL Example ===\n")

    sample_csv = """date,product,quantity,price,region
2024-01-15,Widget,100,9.99,North
2024-01-15,Gadget,50,19.99,South
2024-01-16,Widget,75,9.99,East
2024-01-16,Gadget,30,19.99,North
2024-01-17,Widget,120,9.99,West
2024-01-17,Sprocket,200,4.99,North"""

    records = parse_sales_csv(sample_csv)
    print(f"Loaded {len(records)} records\n")

    print("=== All Records ===")
    for r in records:
        print(f"  {r.date} | {r.product:10} | qty:{r.quantity:3} | ${r.total:.2f}")

    print("\n=== North Region Only ===")
    north_records = filter_by_region(records, "north")
    for r in north_records:
        print(f"  {r.date} | {r.product:10} | ${r.total:.2f}")

    print("\n=== Sales by Product ===")
    by_product = aggregate_by_product(records)
    for product, total in sorted(by_product.items(), key=lambda x: -x[1]):
        print(f"  {product:10}: ${total:.2f}")

    print("\n=== Export to CSV ===")
    output = records_to_csv(north_records)
    print(output)


if __name__ == "__main__":
    main()
