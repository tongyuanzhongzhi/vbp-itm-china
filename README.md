# VBP-ITM China: Institutional Transmission Model of Drug Price Regulation

**Manuscript:** "Institutional coupling as a framework for understanding
drug price regulation effects on health worker remuneration: evidence
from China's health industry wage decline, hospital finance, and
three-country comparison"

**Target journal:** Social Science & Medicine (Health Policy Office)

## Repository Contents

```
├── README.md
├── analysis/
│   └── reproducible_analysis.py     # Full analysis pipeline (Bai-Perron,
│                                      ITS HAC, COVID decomposition, P2 DID,
│                                      κ estimation, Monte Carlo)
└── data/
    ├── verified_data.py             # National + provincial wage data with
    │                                  source URLs (NBS releases 2015-2025)
    ├── real_P3_analysis.json        # All reproducible P3 output numbers
    ├── nbs_raw/
    │   ├── industry_wages_2016-2024.json     # 19-industry panel (NBS)
    │   ├── provincial_panel_raw.csv          # 30-province panel 2016-2024
    │   ├── hospital_financial_series_2010-2024.json  # Yearbook table 4-4-1
    │   ├── hospital_staff_2015-2024.json
    │   ├── hospital_per_worker_compensation.json
    │   ├── nbs_2024_industry_wages.json
    │   └── nbs_2024_wage_release.html        # NBS 2024公报原文
    └── worldbank/
        └── china_health_expenditure.json     # GDP% health spending
```

## Data Sources

All data are from publicly available sources:

1. **National Bureau of Statistics (NBS)** — Annual wage releases 2015-2025
   (stats.gov.cn)
2. **Provincial Statistical Bureaus** — Guangdong, Jiangsu, Shandong,
   Henan, Sichuan (cross-validated); URLs in `data/verified_data.py`
3. **China Health Statistics Yearbook** — Public hospital finances
   2010-2024, table 4-4-1 (National Health Commission, 2016-2025)
4. **MHLW Japan** — Wage Structure Basic Survey (mhlw.go.jp)
5. **OECD Health Statistics** — Physician remuneration (data.oecd.org)
6. **World Bank** — World Development Indicators, health expenditure

## Reproducibility

```bash
cd analysis
python3 reproducible_analysis.py
```

Outputs: `data/real_P3_analysis.json` with all P3 numbers (Bai-Perron,
ITS HAC, COVID decomposition, P2 provincial DID, κ estimation,
Monte Carlo projections).

**Python 3.10+** required. Dependencies: numpy, scipy, pandas, statsmodels.

Verified data can be inspected via:
```bash
python3 data/verified_data.py
```

## License

CC BY 4.0

## Archived DOI

https://doi.org/10.5281/zenodo.20844884
