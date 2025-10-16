import camelot
import pandas as pd
import os
import fitz  # PyMuPDF library
import unicodedata

def normalize_text(text):
    if text is None: return ""
    nfkd_form = unicodedata.normalize('NFKD', str(text))
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8').lower()
    return ' '.join(only_ascii.split())

def merge_concepto_lines(df):
    """
    Post-processes the DataFrame to merge multi-line 'concepto' entries.
    A new transaction is identified by a value in the 'dia' column.
    """
    if 'dia' not in df.columns or 'concepto' not in df.columns:
        print("  -> ⚠️ 'dia' or 'concepto' column not found. Skipping concept merging.")
        return df

    processed_rows = []
    current_transaction_index = -1

    for index, row in df.iterrows():
        # ========================= THE FIX IS HERE =========================
        # The check is changed from '.notna()' to the universal 'pd.notna()' function.
        is_new_transaction = pd.notna(pd.to_numeric(row['dia'], errors='coerce'))
        # =================================================================

        if is_new_transaction:
            processed_rows.append(row.copy())
            current_transaction_index = len(processed_rows) - 1
        else:
            if current_transaction_index != -1 and pd.notna(row['concepto']) and str(row['concepto']).strip() != '':
                processed_rows[current_transaction_index]['concepto'] += ' ' + str(row['concepto'])
    
    if not processed_rows:
        return pd.DataFrame()

    return pd.DataFrame(processed_rows).reset_index(drop=True)

def find_transaction_tables(pdf_path):
    print(f"📄 Processing file: {os.path.basename(pdf_path)}")
    required_headers = [normalize_text(h) for h in ['dia', 'concepto', 'cargos', 'abonos', 'saldo']]
    start_marker = normalize_text("saldo inicial")
    end_marker = normalize_text("saldo minimo requerido")

    start_page, end_page = None, None
    try:
        doc = fitz.open(pdf_path)
        print(f"  -> Analyzing {doc.page_count} pages to find the page range...")
        for page_num, page in enumerate(doc, start=1):
            text = normalize_text(page.get_text("text"))
            if start_page is None and start_marker in text:
                start_page = page_num
            if end_marker in text:
                end_page = page_num
        doc.close()
    except Exception as e:
        print(f"  -> ❌ An error occurred while finding page range: {e}")
        return []

    if start_page is None or end_page is None or end_page < start_page:
        print(f"  -> ⚠️ Could not determine a valid page range for this file.")
        return []

    page_range_str = f"{start_page}-{end_page}"
    print(f"  -> Identified transaction page range: {page_range_str}")

    try:
        tables = camelot.read_pdf(pdf_path, pages=page_range_str, flavor='stream')
        print(f"  -> Camelot extracted {tables.n} potential tables.")
    except Exception as e:
        print(f"  -> ❌ An error occurred during Camelot extraction: {e}")
        return []

    final_tables = []
    for table in tables:
        df = table.df
        if df.empty: continue
        
        header_found_at_row = -1
        for i in range(min(5, len(df))):
            row_as_string = ' '.join([normalize_text(cell) for cell in df.iloc[i].fillna('')])
            if all(req_header in row_as_string for req_header in required_headers):
                header_found_at_row = i
                print(f"  -> ✅ Found a valid header in a table.")
                break
        
        if header_found_at_row != -1:
            df.columns = df.iloc[header_found_at_row]
            df = df.iloc[header_found_at_row + 1:].reset_index(drop=True)
            df.columns = [normalize_text(c) for c in df.columns]
            final_tables.append(df)
    
    if final_tables:
        print(f"  -> Successfully processed {len(final_tables)} tables.")
    return final_tables

# --- Main part of the script ---
if __name__ == "__main__":
    statements_folder = 'statements'
    output_excel_file = 'all_transactions_by_company2.xlsx'

    if not os.path.isdir(statements_folder):
        print(f"❌ ERROR: The folder '{statements_folder}' was not found.")
    else:
        pdf_files = sorted([f for f in os.listdir(statements_folder) if f.lower().endswith('.pdf')])
        
        with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
            print(f"\nWriting to Excel file: {output_excel_file}")
            any_data_saved = False
            for filename in pdf_files:
                full_pdf_path = os.path.join(statements_folder, filename)
                tables_from_pdf = find_transaction_tables(full_pdf_path)
                if tables_from_pdf:
                    pdf_df = pd.concat(tables_from_pdf, ignore_index=True)
                    
                    print("  -> Merging multi-line 'concepto' entries...")
                    cleaned_df = merge_concepto_lines(pdf_df)
                    
                    sheet_name = os.path.splitext(filename)[0][:31]
                    cleaned_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  -> ✅ Saved cleaned transactions to sheet: '{sheet_name}'")
                    any_data_saved = True
            
            if any_data_saved:
                print(f"\n🎉 Success! The Excel file has been created with separate sheets.")
            else:
                print("\n❌ No valid transaction tables were found in any of the PDFs.")