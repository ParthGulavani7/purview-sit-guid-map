# Microsoft Purview eDiscovery GUID Mapping Solution
## Complete Documentation

---

## 📋 Overview

This solution helps you map Microsoft Purview Sensitive Information Type (SIT) GUIDs from eDiscovery reports to their human-readable classification names.

**Problem:** eDiscovery exports contain GUIDs like `50842eb7-edc8-4019-85dd-5a5c1f2bb085`  
**Solution:** Map them to names like `Credit card number`

---

## 📦 Package Contents

### Component 1: Master SIT GUID Mapping Files

1. **Purview_SIT_Master_Mapping_Starter.xlsx**
   - Ready-to-use Excel file with 34 most common SIT mappings
   - Columns: Classification_Name, GUID, Notes
   - Can be shared with clients
   - No sensitive data - just Microsoft's public classifications

2. **extract_purview_sit_guids.py**
   - Python script to extract ALL SITs from Microsoft documentation
   - Creates comprehensive mapping file automatically
   - Requires internet connection
   - Use this to extend beyond the 34 starter SITs

### Component 2: eDiscovery Search Results Mapper

3. **eDiscovery_GUID_Mapper_Template.xlsx**
   - Excel template for mapping your search results
   - Auto-populating formula for multiple comma-separated GUIDs
   - Includes Power Query alternative method
   - Step-by-step instructions included

---

## 🚀 Quick Start Guide

### For Component 1 (Master Mapping File)

**Option A: Use the Starter File (Fastest)**
1. Open `Purview_SIT_Master_Mapping_Starter.xlsx`
2. This covers 34 most common SITs
3. Ready to use immediately!

**Option B: Generate Complete List (Most Comprehensive)**

Requirements:
- Python 3.7+
- Internet connection
- Libraries: requests, beautifulsoup4, pandas, openpyxl

Steps:
```bash
# 1. Install dependencies
pip install requests beautifulsoup4 pandas openpyxl

# 2. Run the extraction script
python extract_purview_sit_guids.py

# 3. Output file created: Purview_SIT_Master_Mapping.xlsx
```

The script will:
- Fetch Microsoft's official SIT documentation
- Extract all GUIDs and classification names
- Create a comprehensive Excel mapping file
- Takes ~5-10 minutes to complete

---

### For Component 2 (Mapping Your eDiscovery Data)

**Step 1: Prepare Your Master Lookup**
1. Open `eDiscovery_GUID_Mapper_Template.xlsx`
2. Go to the `Lookup_Data` sheet
3. Paste your complete master mapping:
   - Column A: Classification names
   - Column B: GUIDs
   - (Copy from `Purview_SIT_Master_Mapping_Starter.xlsx`)

**Step 2: Add Your eDiscovery Data**
1. Go to the `Search_Results` sheet
2. Paste your eDiscovery data:
   - Column A: Email ID or item identifier
   - Column B: SensitiveType column (containing GUIDs)

**Step 3: Magic Happens!**
- The `Classifications` column (Column C) will **AUTO-POPULATE**
- Handles single GUIDs: `50842eb7-...` → `Credit card number`
- Handles multiple GUIDs: `50842eb7-..., a44669fe-...` → `Credit card number, U.S. social security number (SSN)`

---

## 🔧 Excel Formula Explanation

The formula in the Classifications column:
```excel
=IF(B2="","",TEXTJOIN(", ",TRUE,
IF(TRIM(MID(SUBSTITUTE(B2,",",REPT(" ",100)),ROW(INDIRECT("1:"&LEN(B2)-LEN(SUBSTITUTE(B2,",",""))+1))*100-99,100))="","",
IFERROR(VLOOKUP(TRIM(MID(SUBSTITUTE(B2,",",REPT(" ",100)),ROW(INDIRECT("1:"&LEN(B2)-LEN(SUBSTITUTE(B2,",",""))+1))*100-99,100)),Lookup_Data!$A:$B,1,FALSE),"GUID Not Found"))))
```

**What it does:**
1. Splits comma-separated GUIDs
2. Looks up each GUID in the Lookup_Data sheet
3. Joins the classification names back together
4. Shows "GUID Not Found" if a GUID is missing from your master list

**If you get #N/A errors:**
- The GUID is not in your master mapping
- Add it to the Lookup_Data sheet
- Or run the full extraction script to get all SITs

---

## 💡 Alternative Method: Power Query

If the formula is too complex, use Power Query (more visual, easier to debug):

### Power Query Steps:

**1. Split GUIDs into Rows**
   - Load Search_Results into Power Query
   - Select SensitiveType column
   - Transform → Split Column → By Delimiter → Comma → Into Rows

**2. Merge with Lookup Data**
   - Home → Merge Queries
   - Match SensitiveType with Lookup_Data GUID column
   - Expand Classification_Name

**3. Group Back Together**
   - Transform → Group By
   - Group by: EmailID
   - New column: Classifications
   - Operation: Text.Combine([Classification_Name], ", ")

**Result:** Same output, but with a visual interface!

---

## 📊 Sample Data

### Input (SensitiveType column):
```
50842eb7-edc8-4019-85dd-5a5c1f2bb085
a44669fe-0d48-453d-a9b1-2cc83f2cba77, c5b41cc5-8fcc-4b17-aef8-c6e295b0da31
50842eb7-edc8-4019-85dd-5a5c1f2bb085, c7bc98e8-551a-4c35-a92d-d2c8cda714a7
```

### Output (Classifications column):
```
Credit card number
U.S. social security number (SSN), U.S. driver's license number
Credit card number, Azure storage account key
```

---

## 🔍 Confirming GUID Universality

**Q: Are these GUIDs the same across all Microsoft tenants?**  
**A: YES!** 

These are Microsoft's built-in SIT GUIDs, which are universal across all tenants. You can:
- Create the mapping once
- Use it across all your client environments
- Share it internally and with clients
- The GUIDs will always be consistent

**Exception:** Custom SITs created by your client will have tenant-specific GUIDs. These won't appear in Microsoft's documentation and must be documented separately.

---

## 📝 Common SITs Included in Starter File

### Financial:
- Credit card number
- ABA routing number
- U.S. bank account number
- International banking account number (IBAN)
- SWIFT code

### US Identity:
- U.S. social security number (SSN)
- U.S. driver's license number
- U.S. individual taxpayer identification number (ITIN)
- U.S./U.K. passport number

### Healthcare:
- Drug Enforcement Agency (DEA) number
- Medicare Beneficiary Identifier (MBI) card

### Azure/Cloud:
- Azure DocumentDB auth key
- Azure IAAS database connection string
- Azure storage account key
- Azure Redis cache connection string

### International:
- EU debit card, passport, tax ID
- Canada SIN, passport, driver's license
- UK NINO, NHS number, driver's license
- Australia tax file number, passport
- India PAN, Aadhaar

And more! (34 total in starter file)

---

## 🛠 Troubleshooting

### "GUID Not Found" appears in Classifications column
**Solution:** The GUID is not in your master mapping file
- Check if it's a custom SIT created by your client
- Run the full extraction script to get all Microsoft SITs
- Manually add client custom SITs to the Lookup_Data sheet

### Formula shows #N/A error
**Solution:** 
- Ensure the Lookup_Data sheet name is correct
- Check that columns A and B in Lookup_Data contain your mapping
- Verify there are no extra spaces in the GUID values

### Python script fails with network error
**Solution:**
- Check your internet connection
- Some corporate networks block external scripts
- Try running from a different network or machine
- Use the starter file as a fallback

### Too many GUIDs to handle manually
**Solution:**
- Use the Power Query method instead of formulas
- Or use Python/Power BI for large datasets
- Consider automating with Power Automate for recurring tasks

---

## 📞 Support & Extensions

### Need More SITs?
Run the full extraction script or manually add them to your master file using Microsoft's documentation:
https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-entity-definitions

### Custom SITs?
For tenant-specific custom SITs:
1. Contact your client's Purview admin
2. Get the GUID from the Purview portal or via PowerShell
3. Add manually to your Lookup_Data sheet

### Automation?
This solution can be integrated into:
- Power Automate flows
- Power BI reports
- Python ETL pipelines
- Azure Data Factory

---

## 📄 Files Summary

| File | Purpose | Required For |
|------|---------|--------------|
| `Purview_SIT_Master_Mapping_Starter.xlsx` | Quick-start master mapping (34 common SITs) | Component 1 |
| `extract_purview_sit_guids.py` | Generate complete master mapping from Microsoft docs | Component 1 (optional) |
| `eDiscovery_GUID_Mapper_Template.xlsx` | Template for mapping your eDiscovery results | Component 2 |
| `README.md` | This documentation | Reference |

---

## ✅ Quick Checklist

- [ ] Download all files
- [ ] Review `Purview_SIT_Master_Mapping_Starter.xlsx` 
- [ ] Decide: Use starter file or run full extraction?
- [ ] Open `eDiscovery_GUID_Mapper_Template.xlsx`
- [ ] Paste master mapping into Lookup_Data sheet
- [ ] Paste eDiscovery GUIDs into Search_Results sheet
- [ ] Watch Classifications auto-populate!
- [ ] Share with client (optional)

---

**Created:** March 31, 2026  
**Version:** 1.0  
**Author:** Parth's Purview Project Team  
**License:** Internal Use - Neoware Consulting

---

*Questions? Check the Instructions sheet in the Excel files or refer to Microsoft's official documentation.*
