from typing import Dict, List, Tuple
from app.models.assessment import RiskProfile
from app.models.questionnaire import ExclusionOption, Constraints

# Sleeve display names and asset class categories
SLEEVE_METADATA: Dict[str, Tuple[str, str]] = {
    "us_equity": ("US Equities", "Equity"),
    "intl_developed_equity": ("International Developed Equities", "Equity"),
    "em_equity": ("Emerging Markets Equities", "Equity"),
    "global_equity": ("Global Equities", "Equity"),
    "sector_equity": ("Sector & Thematic Equities", "Equity"),
    "treasuries": ("US Treasury Bonds", "Fixed Income"),
    "corporate_bonds": ("Investment Grade Corporate Bonds", "Fixed Income"),
    "aggregate_bonds": ("Broad Aggregate Bonds", "Fixed Income"),
    "high_yield": ("High Yield Corporate Credit", "Fixed Income"),
    "municipal_bonds": ("Municipal Bonds", "Fixed Income"),
    "inflation_linked": ("TIPS / Inflation-Protected Bonds", "Fixed Income"),
    "em_bonds": ("Emerging Markets Sovereign Debt", "Fixed Income"),
    "sukuk": ("Sukuk (Islamic Fixed Income)", "Fixed Income"),
    "cash": ("Cash & Ultra-Short Liquidity", "Cash"),
    "gold": ("Gold & Precious Metals", "Real Assets & Alts"),
    "commodities": ("Broad Commodities", "Real Assets & Alts"),
    "real_estate": ("Real Estate / REITs", "Real Assets & Alts"),
    "crypto": ("Digital Assets / Crypto", "Real Assets & Alts"),
    "alternatives": ("Liquid Alternatives", "Real Assets & Alts"),
    "multi_asset": ("Multi-Asset Solutions", "Multi-Asset"),
}

# Base Target Allocations by Risk Profile (Percentage weights summing to 100.0)
BASE_ALLOCATIONS: Dict[RiskProfile, Dict[str, float]] = {
    RiskProfile.CONSERVATIVE: {
        "cash": 15.0,
        "treasuries": 30.0,
        "aggregate_bonds": 25.0,
        "corporate_bonds": 15.0,
        "us_equity": 15.0,
    },
    RiskProfile.MODERATELY_CONSERVATIVE: {
        "cash": 10.0,
        "treasuries": 20.0,
        "corporate_bonds": 20.0,
        "aggregate_bonds": 15.0,
        "us_equity": 20.0,
        "intl_developed_equity": 10.0,
        "gold": 5.0,
    },
    RiskProfile.BALANCED: {
        "us_equity": 35.0,
        "intl_developed_equity": 15.0,
        "em_equity": 5.0,
        "aggregate_bonds": 15.0,
        "corporate_bonds": 10.0,
        "treasuries": 10.0,
        "real_estate": 5.0,
        "cash": 5.0,
    },
    RiskProfile.GROWTH: {
        "us_equity": 45.0,
        "intl_developed_equity": 15.0,
        "em_equity": 10.0,
        "sector_equity": 5.0,
        "corporate_bonds": 10.0,
        "high_yield": 5.0,
        "real_estate": 5.0,
        "commodities": 5.0,
    },
    RiskProfile.AGGRESSIVE: {
        "us_equity": 50.0,
        "intl_developed_equity": 18.0,
        "em_equity": 12.0,
        "sector_equity": 10.0,
        "real_estate": 5.0,
        "crypto": 5.0,
    },
}


def adapt_allocation_for_constraints(
    base_allocation: Dict[str, float],
    constraints: Constraints
) -> Tuple[Dict[str, float], List[str]]:
    """
    Dynamically adapts target sleeve allocations based on investor exclusions.
    Specifically handles:
    - 'no crypto': redirects crypto allocation into core equity.
    - 'sharia-compliant only': conventional bonds & interest cash redirect to Sukuk;
      unsupported foreign equity sleeves redirect to global Sharia equity.
    """
    allocation = dict(base_allocation)
    notes = []
    exclusions = set(constraints.exclusions)

    # 1. Crypto Exclusion
    if ExclusionOption.NO_CRYPTO in exclusions or ExclusionOption.SHARIA_COMPLIANT_ONLY in exclusions:
        if "crypto" in allocation and allocation["crypto"] > 0:
            crypto_weight = allocation.pop("crypto")
            allocation["us_equity"] = round(allocation.get("us_equity", 0.0) + crypto_weight, 2)
            notes.append(
                f"Crypto excluded by investor preference: {crypto_weight}% reallocated to core US Equities."
            )

    # 2. Sharia-Compliant Only Adaptation
    if ExclusionOption.SHARIA_COMPLIANT_ONLY in exclusions:
        # In universe.json, Sharia funds exist only in:
        # us_equity, global_equity, sector_equity, real_estate, and sukuk.
        # Conventional debt (treasuries, corporate_bonds, aggregate_bonds, high_yield)
        # and interest-bearing cash cannot be held under Islamic finance standards.
        fixed_income_and_cash_sleeves = [
            "treasuries", "corporate_bonds", "aggregate_bonds", "high_yield",
            "municipal_bonds", "inflation_linked", "em_bonds", "cash"
        ]
        total_debt_and_cash_to_reallocate = 0.0
        for sleeve in fixed_income_and_cash_sleeves:
            if sleeve in allocation:
                total_debt_and_cash_to_reallocate += allocation.pop(sleeve)

        if total_debt_and_cash_to_reallocate > 0:
            allocation["sukuk"] = round(
                allocation.get("sukuk", 0.0) + total_debt_and_cash_to_reallocate, 2
            )
            notes.append(
                f"Sharia compliance mandate: {total_debt_and_cash_to_reallocate}% in conventional fixed income and cash reallocated into Sukuk (Islamic investment certificates, SPSK)."
            )

        # Equity sleeves without direct Sharia ETFs in universe:
        # intl_developed_equity and em_equity map to global_equity (UMMA / SPWO)
        unsupported_equity = ["intl_developed_equity", "em_equity"]
        total_unsupported_eq = 0.0
        for eq in unsupported_equity:
            if eq in allocation:
                total_unsupported_eq += allocation.pop(eq)

        if total_unsupported_eq > 0:
            allocation["global_equity"] = round(
                allocation.get("global_equity", 0.0) + total_unsupported_eq, 2
            )
            notes.append(
                f"Sharia compliance mandate: {total_unsupported_eq}% in non-compliant regional equities reallocated into Global Sharia Equities (UMMA/SPWO)."
            )

        # Commodities / Gold
        if "commodities" in allocation:
            comm_wt = allocation.pop("commodities")
            allocation["us_equity"] = round(allocation.get("us_equity", 0.0) + comm_wt, 2)
            notes.append(f"Sharia compliance mandate: {comm_wt}% in commodities reallocated to US Sharia Equity.")

    # Validate sum to 100%
    total_wt = round(sum(allocation.values()), 2)
    if total_wt != 100.0:
        # Adjust any rounding discrepancy on the largest sleeve
        largest_sleeve = max(allocation.keys(), key=lambda k: allocation[k])
        diff = round(100.0 - total_wt, 2)
        allocation[largest_sleeve] = round(allocation[largest_sleeve] + diff, 2)

    return allocation, notes
