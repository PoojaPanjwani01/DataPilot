import pandas as pd
import io
from backend.app.config import settings
from backend.app.utils.logger import logger


class FileValidator:
    def __init__(self):
        self.max_size_bytes = 50 * 1024 * 1024  # 50 MB

    def validate_file_metadata(self, filename: str, content_size: int):
        """Verifies file size limits and extension compliance before reading."""
        logger.info(f"Validating file metadata for: {filename} ({content_size} bytes)")

        # 1. Check if file is empty
        if content_size == 0:
            raise ValueError("File is empty.")

        # 2. Check maximum size constraint
        if content_size > self.max_size_bytes:
            raise ValueError(
                f"File size exceeds the 50 MB maximum limit (size: {content_size / (1024 * 1024):.2f} MB)."
            )

        # 3. Check file extension support
        ext = filename.lower().split(".")[-1]
        if ext not in ["csv", "xlsx"]:
            raise ValueError(
                "Unsupported file format. Only CSV and XLSX are supported."
            )

    def parse_and_validate_structure(
        self, file_content: bytes, filename: str
    ) -> pd.DataFrame:
        """Parses byte content into a Pandas DataFrame and checks structural constraints."""
        ext = filename.lower().split(".")[-1]

        # 1. Reject duplicate column names and detect corrupted formats
        try:
            if ext == "csv":
                import csv

                # Decode a sample of the file content to extract the header
                sample_text = file_content[: 1024 * 1024].decode(
                    "utf-8", errors="ignore"
                )
                reader = csv.reader(io.StringIO(sample_text))
                header = next(reader, None)
                if header:
                    header_cleaned = [h.strip() for h in header if h is not None]
                    if len(header_cleaned) != len(set(header_cleaned)):
                        raise ValueError("Dataset contains duplicate column names.")
            else:
                import openpyxl

                wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
                sheet = wb.active
                header = []
                for row in sheet.iter_rows(max_row=1, values_only=True):
                    header = [str(cell).strip() for cell in row if cell is not None]
                    break
                wb.close()
                if header and len(header) != len(set(header)):
                    raise ValueError("Dataset contains duplicate column names.")
        except ValueError as ve:
            logger.warning(f"File validation constraint failed: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"File corruption detected: {str(e)}")
            raise ValueError(
                f"Corrupted or invalid {ext.upper()} file structure: {str(e)}"
            )

        # 2. Parse complete structure using Pandas
        try:
            if ext == "csv":
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            logger.error(f"Failed to parse file: {str(e)}")
            raise ValueError(
                f"Failed to read file records (Corrupted or invalid structure): {str(e)}"
            )

        # 4. Check for headers and columns
        if df.columns.empty or len(df.columns) < 1:
            raise ValueError(
                "The dataset must contain a header row and at least 1 column."
            )

        # 5. Check for data rows
        if len(df) < 1:
            raise ValueError("The dataset must contain at least 1 data row.")

        # 6. Check row and column limits
        if len(df.columns) > settings.max_dataset_columns:
            raise ValueError(
                f"Dataset exceeds column limit of {settings.max_dataset_columns} (found {len(df.columns)} columns)."
            )

        if len(df) > settings.max_dataset_rows:
            raise ValueError(
                f"Dataset exceeds row limit of {settings.max_dataset_rows} (found {len(df)} rows)."
            )

        logger.info(
            f"File structure validation successful for {filename} (Shape: {df.shape})"
        )
        return df


file_validator = FileValidator()
