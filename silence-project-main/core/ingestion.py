import pandas as pd
from .models import UploadedDataset, ComplaintRecord

REQUIRED_COLUMNS = {"region", "district", "population", "complaints", "history_avg"}

def ingest_csv_to_db(file_obj, silence_threshold: float) -> UploadedDataset:
    df = pd.read_csv(file_obj)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")

    dataset = UploadedDataset.objects.create(
        original_filename=getattr(file_obj, "name", "uploaded.csv"),
        silence_threshold=float(silence_threshold),
    )

    # Bulk insert for speed
    records = []
    for row in df.to_dict("records"):
        records.append(
            ComplaintRecord(
                dataset=dataset,
                region=str(row["region"]),
                district=str(row["district"]),
                population=int(row["population"]),
                complaints=int(row["complaints"]),
                history_avg=int(row["history_avg"]),
            )
        )

    ComplaintRecord.objects.bulk_create(records)
    return dataset
