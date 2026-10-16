"""
Multi-Format Office Document Streaming Extractor for InfinityScrape.
Streams and extracts .docx Word documents and .xlsx Excel spreadsheets
directly into clean Markdown and structured JSON without disk bloat.
"""

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
import httpx


# =============================================================================
# 📄 DOCX WORD DOCUMENT EXTRACTOR
# =============================================================================

def extract_docx_from_bytes(file_bytes: bytes, file_name: str = "document.docx") -> Dict[str, Any]:
    """
    Parses a Word (.docx) file from memory bytes into clean structured Markdown.
    Extracts Headings (H1-H4), bullet points, standard paragraphs, and tables.
    """
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        return {
            "status": "error",
            "file_name": file_name,
            "error": f"Failed to parse DOCX document: {str(e)}"
        }

    md_lines: List[str] = [f"# 📄 {file_name}", ""]
    total_words = 0
    tables_data: List[Dict[str, Any]] = []

    # 1. Extract Paragraphs
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        total_words += len(text.split())
        style_name = p.style.name.lower() if p.style else ""

        if "heading 1" in style_name:
            md_lines.append(f"\n# {text}\n")
        elif "heading 2" in style_name:
            md_lines.append(f"\n## {text}\n")
        elif "heading 3" in style_name:
            md_lines.append(f"\n### {text}\n")
        elif "list" in style_name or "bullet" in style_name:
            md_lines.append(f"- {text}")
        else:
            md_lines.append(f"{text}\n")

    # 2. Extract Tables
    for t_idx, table in enumerate(doc.tables, 1):
        table_rows = []
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            table_rows.append(row_cells)

        if not table_rows:
            continue

        headers = table_rows[0]
        data_rows = table_rows[1:] if len(table_rows) > 1 else []

        md_lines.append(f"\n#### Table {t_idx}\n")
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for dr in data_rows:
            # Pad row if mismatched cell counts
            padded = dr + [""] * (len(headers) - len(dr))
            md_lines.append("| " + " | ".join(padded[:len(headers)]) + " |")
        md_lines.append("")

        tables_data.append({
            "table_index": t_idx,
            "headers": headers,
            "row_count": len(data_rows),
            "rows": data_rows
        })

    full_markdown = "\n".join(md_lines)

    return {
        "status": "success",
        "file_name": file_name,
        "total_paragraphs": len(doc.paragraphs),
        "total_tables": len(doc.tables),
        "word_count": total_words,
        "tables": tables_data,
        "markdown": full_markdown
    }


async def extract_docx_from_url(url: str) -> Dict[str, Any]:
    """
    Streams a remote online .docx file via TLS and extracts it into clean Markdown.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "http_status": resp.status_code,
                    "error": f"Failed to download DOCX: HTTP {resp.status_code}",
                    "url": url
                }
            file_name = url.split("/")[-1].split("?")[0] or "remote_document.docx"
            res = extract_docx_from_bytes(resp.content, file_name=file_name)
            res["source_url"] = url
            return res
    except Exception as e:
        return {"status": "error", "url": url, "error": f"DOCX fetch error: {str(e)}"}


# =============================================================================
# 📊 XLSX EXCEL SPREADSHEET EXTRACTOR (Zero-Dependency XML Parser)
# =============================================================================

def extract_xlsx_from_bytes(file_bytes: bytes, file_name: str = "spreadsheet.xlsx", max_rows_per_sheet: int = 100) -> Dict[str, Any]:
    """
    Fast in-memory parser for .xlsx Excel spreadsheets using standard ZIP + XML.
    Extracts all worksheets into structured Markdown tables and JSON records.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_bytes))
    except Exception as e:
        return {"status": "error", "file_name": file_name, "error": f"Invalid XLSX zip file: {str(e)}"}

    # 1. Parse Shared Strings (xl/sharedStrings.xml)
    shared_strings = []
    if "xl/sharedStrings.xml" in zf.namelist():
        try:
            ss_xml = zf.read("xl/sharedStrings.xml")
            root = ET.fromstring(ss_xml)
            for si in root:
                # Text can be directly in <t> or nested in <r><t>
                text_parts = [t.text for t in si.iter() if t.tag.endswith("t") and t.text]
                shared_strings.append("".join(text_parts))
        except Exception:
            pass

    # 2. Parse Workbook Sheet Names (xl/workbook.xml)
    sheet_names = []
    if "xl/workbook.xml" in zf.namelist():
        try:
            wb_xml = zf.read("xl/workbook.xml")
            wb_root = ET.fromstring(wb_xml)
            for elem in wb_root.iter():
                if elem.tag.endswith("sheet"):
                    sname = elem.attrib.get("name")
                    if sname:
                        sheet_names.append(sname)
        except Exception:
            pass

    # 3. Parse Worksheet Data (xl/worksheets/sheet1.xml, sheet2.xml, ...)
    sheet_files = sorted([f for f in zf.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")])
    sheets_output = []
    md_lines = [f"# 📊 {file_name}", ""]

    for idx, sfile in enumerate(sheet_files):
        sname = sheet_names[idx] if idx < len(sheet_names) else f"Sheet {idx+1}"
        try:
            sxml = zf.read(sfile)
            sroot = ET.fromstring(sxml)
            rows_data = []

            for row in sroot.iter():
                if row.tag.endswith("row"):
                    row_cells = []
                    for c in row.iter():
                        if c.tag.endswith("c"):
                            cell_type = c.attrib.get("t")
                            v_elem = None
                            for child in c:
                                if child.tag.endswith("v"):
                                    v_elem = child
                                    break
                            val = v_elem.text if v_elem is not None and v_elem.text else ""
                            if cell_type == "s" and val.isdigit():
                                s_idx = int(val)
                                val = shared_strings[s_idx] if s_idx < len(shared_strings) else val
                            row_cells.append(str(val).strip())
                    if row_cells:
                        rows_data.append(row_cells)

            if not rows_data:
                continue

            headers = rows_data[0]
            data_rows = rows_data[1:max_rows_per_sheet + 1]

            md_lines.append(f"\n### Worksheet: {sname} ({len(rows_data)-1} rows)\n")
            md_lines.append("| " + " | ".join(headers) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for dr in data_rows:
                padded = dr + [""] * (len(headers) - len(dr))
                md_lines.append("| " + " | ".join(padded[:len(headers)]) + " |")

            # Structured records
            records = []
            for dr in data_rows:
                padded = dr + [""] * (len(headers) - len(dr))
                records.append({headers[i]: padded[i] for i in range(len(headers))})

            sheets_output.append({
                "sheet_name": sname,
                "total_rows": len(rows_data),
                "headers": headers,
                "records": records
            })

        except Exception as sheet_err:
            md_lines.append(f"\n*Error reading {sname}: {str(sheet_err)}*")

    return {
        "status": "success",
        "file_name": file_name,
        "total_sheets": len(sheets_output),
        "sheets": sheets_output,
        "markdown": "\n".join(md_lines)
    }


async def extract_xlsx_from_url(url: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Streams a remote online .xlsx spreadsheet via TLS and extracts it into clean Markdown tables.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "http_status": resp.status_code,
                    "error": f"Failed to download XLSX: HTTP {resp.status_code}",
                    "url": url
                }
            file_name = url.split("/")[-1].split("?")[0] or "remote_spreadsheet.xlsx"
            res = extract_xlsx_from_bytes(resp.content, file_name=file_name, max_rows_per_sheet=max_rows)
            res["source_url"] = url
            return res
    except Exception as e:
        return {"status": "error", "url": url, "error": f"XLSX fetch error: {str(e)}"}
