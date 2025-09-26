#!/usr/bin/env python3
"""
Debug transformation issue
"""

import sys
import os
sys.path.append('src')

from data.csv_reader import CSVReader
from data.transformer import DataTransformer
import traceback

def debug_transformation():
    reader = CSVReader('.')
    transformer = DataTransformer()
    
    # Get a small sample
    df = reader.read_csv_file('warehouse_logs')
    sample_df = df.head(3)
    
    print("Sample data:")
    print(sample_df)
    print("\nColumns:", sample_df.columns.tolist())
    
    # Try transformation row by row
    for idx, row in sample_df.iterrows():
        print(f"\nProcessing row {idx}:")
        print(f"  issues: {row['issues']} (type: {type(row['issues'])})")
        print(f"  delay_reasons: {row.get('delay_reasons', 'NOT_FOUND')}")
        
        try:
            # Test the safe conversion
            issues_result = transformer._safe_list_conversion(row['issues'])
            print(f"  safe conversion result: {issues_result}")
        except Exception as e:
            print(f"  Error in safe conversion: {e}")
            traceback.print_exc()
            
        try:
            # Try the full transformation for this row
            doc = {
                "log_id": int(row['log_id']) if pd.notna(row['log_id']) else None,
                "order_id": int(row['order_id']) if pd.notna(row['order_id']) else None,
                "warehouse_id": int(row['warehouse_id']) if pd.notna(row['warehouse_id']) else None,
                "issues": transformer._safe_list_conversion(row.get('issues', []))
            }
            print(f"  Document created successfully: {doc}")
        except Exception as e:
            print(f"  Error creating document: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    debug_transformation()
