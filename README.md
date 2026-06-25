# VBP-ITM China: Institutional Transmission Model of Drug Price Regulation

**Manuscript:** "Institutional coupling as a framework for understanding
drug price regulation effects on health worker remuneration: descriptive
evidence from China's health industry wage decline and three-country
comparison"

**Target journal:** Social Science & Medicine (Health Policy Office)

**Corresponding author:** Zhensheng Dai, Department of Hematology,
Shanghai Pudong Hospital, Fudan University Pudong Medical Center,
Shanghai, China. Email: 20505@shpdh.org. ORCID: 0009-0009-7476-8163.

## Authors

- Zhensheng Dai (Department of Hematology, Shanghai Pudong Hospital,
  Fudan University Pudong Medical Center) — first and corresponding author
- Yueling Jin (Shanghai Science and Technology Museum)

## Repository Contents

```
├── VBP_Health_Wage_Decline.docx        # Manuscript (latest)
├── Cover_Letter_SSM.docx               # Cover letter to SSM
├── HIGHLIGHTS.txt                       # Key highlights
├── STROBE_checklist.txt                 # STROBE reporting checklist
├── README.md                            # This file
├── Figure1.jpg ... Figure6.jpg          # Figures 1–6
├── analysis/
│   └── vbp_analysis_fixes.py            # Methodological analyses
│       (Bai-Perron, bootstrap, BCa, Manski, Monte Carlo, etc.)
└── data/
    └── verified_data.py                 # Verified data with source URLs
```

## Data Sources

All data are from publicly available sources:

1. **China National Bureau of Statistics (NBS)** — Annual wage releases
   - https://www.stats.gov.cn/sj/zxfb/202505/t20250516_1959826.html (2024)
   - https://www.stats.gov.cn/sj/zxfb/202405/t20240520_1950434.html (2023)
2. **Provincial Statistical Bureaus** — Guangdong, Jiangsu, Shandong,
   Henan, Sichuan (quality-A confirmed); URLs in `data/verified_data.py`
3. **Japan Ministry of Health, Labour and Welfare (MHLW)** — Wage
   Structure Basic Survey. https://www.mhlw.go.jp
4. **OECD Health Statistics** — Physician remuneration data.
   https://data.oecd.org
5. **National Health Commission** — Tertiary Hospital Performance
   Monitoring Report 2023
   https://www.nhc.gov.cn/yzygj/c100067/202503/5afa3c26abf6461ba02bf0f3997d821e.shtml

## Data Status Notes

- Health-industry wage values for **2015–2025** are confirmed from NBS
  annual releases (2015–2016 and 2025 independently web-verified against
  NBS releases; 2017–2018 cross-validated against the 2019 confirmed
  value and reported growth rates; 2019–2024 from NBS annual releases).
- **2025 values** (health 146,266; national 129,441) are confirmed from
  the NBS 2026-05 release.
- **2018 national average wage:** 82,413 yuan (NBS official; an earlier
  manuscript draft showed 82,461, which has been corrected).
- **Five provinces** have quality-A confirmed data: Guangdong, Jiangsu,
  Shandong, Henan, Sichuan. The remaining 26 provinces are estimated.

## Reproducibility

Run `data/verified_data.py` to verify confirmed data against primary
sources. Run `analysis/vbp_analysis_fixes.py` to reproduce the
methodological analyses.

**Python 3.10+** required. Dependencies: numpy, scipy, pandas, statsmodels.

## License

CC BY 4.0 — matching the manuscript's open access licence.

## Citation

Dai Z, Jin Y. Institutional coupling as a framework for understanding
drug price regulation effects on health worker remuneration: descriptive
evidence from China's health industry wage decline and three-country
comparison. [Journal TBD]. 2026.

## Archived DOI

**https://doi.org/10.5281/zenodo.20844884**

The manuscript, data, and code are archived on Zenodo (GitHub release
v1.0.1 of `tongyuanzhongzhi/vbp-itm-china`).

## Contact

Zhensheng Dai, MD — 20505@shpdh.org
Department of Hematology, Shanghai Pudong Hospital, Fudan University
Pudong Medical Center
