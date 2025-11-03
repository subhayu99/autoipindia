"""
CSV Import Logic for Trademark Batch Upload

This module handles parsing and validation of CSV files containing trademark data.
"""

import pandas as pd
from io import StringIO
from typing import List, Dict, Tuple, Optional
from pydantic import ValidationError

from logic.trademark_search import TrademarkSearchParams


class CSVImportError(Exception):
    """Custom exception for CSV import errors"""
    pass


def parse_csv_file(file_content: str) -> pd.DataFrame:
    """
    Parse CSV file content into a pandas DataFrame.

    Args:
        file_content: String content of the CSV file

    Returns:
        pd.DataFrame: Parsed CSV data

    Raises:
        CSVImportError: If CSV parsing fails
    """
    try:
        # Try to read the CSV with various common delimiters
        df = pd.read_csv(StringIO(file_content), skipinitialspace=True)

        if df.empty:
            raise CSVImportError("CSV file is empty")

        return df
    except Exception as e:
        raise CSVImportError(f"Failed to parse CSV: {str(e)}")


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate that the CSV has the correct structure.

    Expected formats:
    1. application_number only
    2. wordmark, class_name
    3. application_number, wordmark, class_name (all fields)

    Args:
        df: DataFrame to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    columns = [col.strip().lower() for col in df.columns]

    # Check for required column combinations
    has_app_number = 'application_number' in columns
    has_wordmark = 'wordmark' in columns
    has_class = 'class_name' in columns or 'class' in columns

    # Rename 'class' to 'class_name' if present
    if 'class' in df.columns and 'class_name' not in df.columns:
        df.rename(columns={'class': 'class_name'}, inplace=True)

    # Standardize column names to lowercase
    df.columns = [col.strip().lower() for col in df.columns]

    # Valid combinations:
    # 1. application_number only
    # 2. wordmark + class_name
    # 3. application_number + wordmark + class_name (all)

    if has_app_number:
        return True, None
    elif has_wordmark and has_class:
        return True, None
    else:
        return False, (
            "CSV must contain either:\n"
            "1. 'application_number' column, OR\n"
            "2. Both 'wordmark' and 'class_name' (or 'class') columns"
        )


def csv_to_trademark_params(df: pd.DataFrame) -> Tuple[List[TrademarkSearchParams], List[Dict]]:
    """
    Convert DataFrame rows to TrademarkSearchParams objects.

    Args:
        df: DataFrame with trademark data

    Returns:
        Tuple of (valid_trademarks, errors)
        - valid_trademarks: List of successfully validated TrademarkSearchParams
        - errors: List of dicts with row number and error message for failed rows
    """
    valid_trademarks = []
    errors = []

    # Ensure columns are lowercase for consistency
    df.columns = [col.strip().lower() for col in df.columns]

    for idx, row in df.iterrows():
        try:
            # Convert row to dict, handling NaN values
            row_dict = {}

            if 'application_number' in df.columns and pd.notna(row.get('application_number')):
                row_dict['application_number'] = str(row['application_number']).strip()

            if 'wordmark' in df.columns and pd.notna(row.get('wordmark')):
                row_dict['wordmark'] = str(row['wordmark']).strip()

            if 'class_name' in df.columns and pd.notna(row.get('class_name')):
                # Try to convert to int, but keep as string if it fails
                try:
                    row_dict['class_name'] = int(float(row['class_name']))
                except (ValueError, TypeError):
                    row_dict['class_name'] = str(row['class_name']).strip()

            # Skip completely empty rows
            if not row_dict:
                continue

            # Create and validate TrademarkSearchParams
            trademark = TrademarkSearchParams(**row_dict)
            valid_trademarks.append(trademark)

        except ValidationError as e:
            error_msg = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
            errors.append({
                'row': idx + 2,  # +2 because: +1 for 0-index, +1 for header row
                'data': row.to_dict(),
                'error': error_msg
            })
        except Exception as e:
            errors.append({
                'row': idx + 2,
                'data': row.to_dict(),
                'error': str(e)
            })

    return valid_trademarks, errors


def process_csv_upload(file_content: str) -> Dict:
    """
    Process uploaded CSV file and return validation results.

    Args:
        file_content: String content of the CSV file

    Returns:
        Dict containing:
        - valid_count: Number of valid records
        - error_count: Number of invalid records
        - trademarks: List of valid TrademarkSearchParams (as dicts)
        - errors: List of error details for invalid rows

    Raises:
        CSVImportError: If CSV structure is invalid
    """
    # Parse CSV
    df = parse_csv_file(file_content)

    # Validate structure
    is_valid, error_msg = validate_csv_structure(df)
    if not is_valid:
        raise CSVImportError(error_msg)

    # Convert to trademark params
    valid_trademarks, errors = csv_to_trademark_params(df)

    return {
        'valid_count': len(valid_trademarks),
        'error_count': len(errors),
        'trademarks': [tm.model_dump() for tm in valid_trademarks],
        'errors': errors
    }
