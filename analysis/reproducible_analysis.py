#!/usr/bin/env python3
"""
VBP / ITM Manuscript — Reproducible Analysis Pipeline
=====================================================

This module contains ONLY analyses that are reproducible from verified data.
It replaces the non-reproducible claims in vbp_analysis_fixes.py (which carried
fabricated/unsourced numbers: health Bai-Perron break 2022 F=8.10, non-health
break years 2018/2019, ITS b7=-0.033/+0.022 from no underlying data).

DATA SOURCES (all on disk under 集采/data/):
  - verified_data.py            : health + all-industry 2015-2025 (NBS),
                                  5 confirmed provinces, NHC hospital monitoring,
                                  OECD ratios, VBP rounds
  - nbs_raw/industry_wages_2016-2024.json : 19 industries x 2016-2024
                                  (NBS, browser-downloaded by author 2026-06-27)
  - worldbank/china_health_expenditure.json : macro health expenditure

OUTPUTS:
  - real_P3_analysis.json       : all reproducible P3 numbers
  - console summary

REPRODUCIBLE FINDINGS (vs old manuscript claims):
  - Health Bai-Perron break 2022 F=8.10  ->  FALSE. Real supF=1.44, NO break.
  - Non-health breaks (Edu 2018, PA 2019)->  FALSE. Real: Finance 2021 (supF=23.9),
                                              Public Admin weak 2021, others none.
  - ITS b7 Manufacturing -0.033          ->  Real -0.018 (p<0.001). Direction/signif OK.
  - ITS b7 Public Admin +0.022           ->  Real +0.023 (p<0.001). Nearly identical.
  - ITS b7 Education ns                  ->  Confirmed ns (p=0.95).
  - COVID decomp +0.8/-0.5/-1.6          ->  Real +0.59/-0.52/-1.38 (direction OK).
  - Ratio changes -0.017/-0.032          ->  Exact match.

Author: Zhensheng Dai
Date: 2026-06-27
"""

import json
import os
import sys
import numpy as np
from scipy import stats

try:
    import statsmodels.api as sm
    from statsmodels.regression.linear_model import OLS
    HAVE_SM = True
except Exception:
    HAVE_SM = False

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, DATA)

INDUSTRY_FILE = os.path.join(DATA, "nbs_raw", "industry_wages_2016-2024.json")
OUTPUT_FILE = os.path.join(DATA, "real_P3_analysis.json")

# 7 industries used in the ITM cross-industry analysis
SEVEN = ['Health', 'Education', 'Manufacturing', 'Finance',
         'IT', 'Scientific_Research', 'Public_Admin']


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def load_industry_wages():
    """Load 19-industry wage series 2016-2024 (NBS, browser-downloaded)."""
    with open(INDUSTRY_FILE, encoding='utf-8') as f:
        raw = json.load(f)
    # JSON keys are strings -> convert year keys to int
    out = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            out[k] = {int(y): val for y, val in v.items()}
        else:
            out[k] = v
    return out


def compute_ratio_series(d, inds, years):
    """Compute industry-to-all-industry wage ratio for each industry."""
    allw = [d['_all'][y] for y in years]
    return {k: np.array([d[k][y] / d['_all'][y] for y in years]) for k in inds}


# ----------------------------------------------------------------------------
# Bai-Perron structural break test (BIC selection + supF)
# ----------------------------------------------------------------------------
def _ssr(seg):
    return float(np.sum((seg - np.mean(seg)) ** 2))


def _bic(ssr, n, npar):
    return n * np.log(ssr / n) + npar * np.log(n)


def bai_perron(series, year_labels, min_seg=3):
    """
    Test 0 vs 1 structural break by BIC; report supF and BIC-selected break.
    series: 1D array (annual ratio CHANGES)
    year_labels: list of years corresponding to series entries
    Returns dict with supF, bic_selected_break, bic_no_break, bic_1break, verdict.
    """
    n = len(series)
    s0 = _ssr(series)
    b0 = _bic(s0, n, 1)
    best_f = 0.0
    best_by = None
    best_bic = b0
    best_bi = None
    for i in range(min_seg, n - min_seg + 1):
        s = _ssr(series[:i]) + _ssr(series[i:])
        b = _bic(s, n, 3)
        q, k = 1, 2
        f = ((s0 - s) / q) / (s / (n - k)) if s > 0 else 0.0
        if b < best_bic:
            best_bic = b
            best_bi = year_labels[i]
        if f > best_f:
            best_f = f
            best_by = year_labels[i]
    # Bai-Perron 5% critical value for single break, n~8-10, is ~7-8
    sig = best_f > 7.0 and (best_bic < b0 - 2.0)
    return {
        'supF': round(best_f, 2),
        'supF_year': best_by,
        'bic_selected_break': best_bi,
        'bic_no_break': round(b0, 2),
        'bic_1break': round(best_bic, 2),
        'delta_BIC': round(b0 - best_bic, 2),
        'verdict': ('significant break ' + str(best_bi)) if sig else 'no significant break',
    }


# ----------------------------------------------------------------------------
# Interrupted Time Series with Newey-West HAC SE
# ----------------------------------------------------------------------------
def its_differential(health_ratio, comp_ratio, years, break_year=2019, maxlags=2):
    """
    Segmented regression on health + comparator panel:
      ratio = b0 + b1*t + b2*post + b3*time_after + b4*health
            + b5*health*t + b6*health*post + b7*health*time_after
    b7 = differential slope change (health vs comparator).
    Returns b7, HAC SE, t, p, DW. Requires statsmodels.
    """
    if not HAVE_SM:
        return {'error': 'statsmodels not installed'}
    rows = []
    t0 = years[0]
    for ind, rv in [('Health', health_ratio), ('Comp', comp_ratio)]:
        for i, y in enumerate(years):
            t = y - t0
            post = 1 if y >= (break_year + 1) else 0
            ta = max(0, y - break_year)
            h = 1 if ind == 'Health' else 0
            rows.append([1, t, post, ta, h, h * t, h * post, h * ta, rv[i]])
    arr = np.array(rows, dtype=float)
    X, y = arr[:, :8], arr[:, 8]
    m = OLS(y, sm.add_constant(X)).fit(cov_type='HAC', cov_kwds={'maxlags': maxlags})
    resid = m.resid
    dw = float(np.sum(np.diff(resid) ** 2) / np.sum(resid[1:] ** 2)) if len(resid) > 1 else None
    return {
        'b7': round(float(m.params[7]), 4),
        'HAC_SE': round(float(m.bse[7]), 4),
        't': round(float(m.tvalues[7]), 2),
        'p': round(float(m.pvalues[7]), 4),
        'DW': round(dw, 2) if dw else None,
    }


# ----------------------------------------------------------------------------
# COVID decomposition + ratio changes
# ----------------------------------------------------------------------------
def covid_decomposition(d, yrs):
    """Health growth minus all-industry growth, by period (pp)."""
    def grp(ys):
        hs = [(d['Health'][y] / d['Health'][y - 1] - 1) * 100 for y in ys]
        al = [(d['_all'][y] / d['_all'][y - 1] - 1) * 100 for y in ys]
        return float(np.mean([h - a for h, a in zip(hs, al)]))
    return {
        'pre_VBP_2017_2019': round(grp([2017, 2018, 2019]), 2),
        'VBP_COVID_2020_2022': round(grp([2020, 2021, 2022]), 2),
        'post_COVID_2023_2024': round(grp([2023, 2024]), 2),
    }


def ratio_changes(ratio, yrs):
    def seg(y1, y2):
        return round(float(ratio[yrs.index(y2)] - ratio[yrs.index(y1)]), 4)
    return {'2019_to_2022': seg(2019, 2022), '2022_to_2024': seg(2022, 2024)}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def run_all():
    d = load_industry_wages()
    yrs = list(range(2016, 2025))
    ratio = compute_ratio_series(d, SEVEN, yrs)

    results = {
        'data_source': 'NBS 19-industry wages 2016-2024 (industry_wages_2016-2024.json)',
        'years': yrs,
        'industries': SEVEN,
    }

    # 1. Bai-Perron on each industry's ratio CHANGE series (2017-2024)
    rch_yrs = list(range(2017, 2025))
    results['bai_perron_ratio_change'] = {}
    for k in SEVEN:
        rch = np.diff(ratio[k])
        results['bai_perron_ratio_change'][k] = bai_perron(rch, rch_yrs)

    # 2. ITS differential slope (break 2019, HAC)
    results['ITS_HAC_break2019'] = {}
    for comp in ['Manufacturing', 'Public_Admin', 'Education']:
        results['ITS_HAC_break2019'][f'Health_vs_{comp}'] = its_differential(
            ratio['Health'], ratio[comp], yrs)

    # 3. Health slope change (pre/post 2019)
    pre = stats.linregress([y - 2016 for y in [2016, 2017, 2018, 2019]],
                           [ratio['Health'][yrs.index(y)] for y in [2016, 2017, 2018, 2019]]).slope
    post = stats.linregress([y - 2016 for y in [2019, 2020, 2021, 2022, 2023, 2024]],
                            [ratio['Health'][yrs.index(y)] for y in [2019, 2020, 2021, 2022, 2023, 2024]]).slope
    results['health_slope_change_2019'] = {
        'pre_2016_2019': round(float(pre), 4),
        'post_2019_2024': round(float(post), 4),
        'slope_change': round(float(post - pre), 4),
    }

    # 4. COVID decomposition + ratio changes
    results['covid_decomposition_pp'] = covid_decomposition(d, yrs)
    results['ratio_changes'] = ratio_changes(ratio['Health'], yrs)

    # 5. Cross-industry 2023->2024 ratio change (reproducible snapshot)
    results['cross_industry_2023_to_2024'] = {
        k: round(float(ratio[k][yrs.index(2024)] - ratio[k][yrs.index(2023)]), 4)
        for k in SEVEN
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Console summary
    print('=' * 70)
    print('REPRODUCIBLE ANALYSIS — VBP/ITM manuscript')
    print('=' * 70)
    print('\n[1] Bai-Perron (ratio change series 2017-2024):')
    for k in SEVEN:
        r = results['bai_perron_ratio_change'][k]
        print(f'  {k:18s} supF={r["supF"]:6.2f}  break={str(r["bic_selected_break"]):6s}  {r["verdict"]}')
    print('\n[2] ITS (break 2019, Newey-West HAC):')
    for comp in ['Manufacturing', 'Public_Admin', 'Education']:
        r = results['ITS_HAC_break2019'][f'Health_vs_{comp}']
        if 'error' in r:
            print(f'  Health vs {comp:14s}: {r["error"]}')
        else:
            print(f'  Health vs {comp:14s}: b7={r["b7"]:+.4f} SE={r["HAC_SE"]:.4f} t={r["t"]:+.2f} p={r["p"]:.3f} DW={r["DW"]}')
    hs = results['health_slope_change_2019']
    print(f'\n[3] Health slope: pre={hs["pre_2016_2019"]:+.4f} post={hs["post_2019_2024"]:+.4f} change={hs["slope_change"]:+.4f}')
    cd = results['covid_decomposition_pp']
    print(f'[4] COVID decomp (pp): pre={cd["pre_VBP_2017_2019"]:+.2f} COVID={cd["VBP_COVID_2020_2022"]:+.2f} post={cd["post_COVID_2023_2024"]:+.2f}')
    rc = results['ratio_changes']
    print(f'[5] Ratio changes: 2019->22={rc["2019_to_2022"]:+.4f}  2022->24={rc["2022_to_2024"]:+.4f}')
    print(f'\nSaved -> {OUTPUT_FILE}')


if __name__ == '__main__':
    run_all()
