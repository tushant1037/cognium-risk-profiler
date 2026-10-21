import json
import math
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.models.questionnaire import (
    ExclusionOption,
    Constraints,
)

class InstrumentUniverse:
    def __init__(self, universe_path: Optional[Path] = None):
        self.universe_path = universe_path or settings.UNIVERSE_PATH
        self.instruments: List[dict] = []
        self.instruments_by_ticker: Dict[str, dict] = {}
        self.load_universe()

    def load_universe(self) -> None:
        try:
            if self.universe_path and self.universe_path.exists():
                with open(self.universe_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.instruments = data.get("instruments", [])
                    for inst in self.instruments:
                        self.instruments_by_ticker[inst["ticker"]] = inst
                print(f"Loaded {len(self.instruments)} instruments from universe.json.")
            else:
                print(f"Universe path does not exist: {self.universe_path}")
        except Exception as e:
            print(f"Error loading universe.json: {e}")

    def filter_and_rank_for_sleeve(
        self,
        sleeve: str,
        constraints: Constraints
    ) -> List[dict]:
        """
        Narrows the universe of ETFs for a sleeve based on investor constraints,
        then ranks candidates by liquidity (AUM), low expense ratio, and institutional quality.
        """
        exclusions = set(constraints.exclusions)
        sharia_required = ExclusionOption.SHARIA_COMPLIANT_ONLY in exclusions
        esg_preferred = ExclusionOption.ESG_PREFERENCE in exclusions
        no_crypto = ExclusionOption.NO_CRYPTO in exclusions

        candidates = [i for i in self.instruments if i.get("sleeve") == sleeve]

        # 1. Mandatory Sharia Filter
        if sharia_required:
            candidates = [i for i in candidates if i.get("sharia_compliant") is True]

        # 2. Mandatory Crypto Filter
        if no_crypto:
            candidates = [i for i in candidates if not i.get("crypto", False)]

        if not candidates:
            # Fallback if no specific candidate exists under strict sleeve filter
            if sharia_required:
                # Return Sharia global/equity alternative if available
                candidates = [i for i in self.instruments if i.get("sharia_compliant") is True]
            else:
                candidates = [i for i in self.instruments if i.get("sleeve") == sleeve]

        # 3. Scoring / Ranking Function
        def rank_score(inst: dict) -> float:
            score = 0.0

            # Scale / AUM factor
            aum = inst.get("fund_net_assets_usd") or 100_000_000
            log_aum = math.log10(max(aum, 10_000_000))
            score += log_aum * 10.0

            # Expense ratio penalty (lower is much better)
            er = inst.get("expense_ratio_pct")
            if er is not None:
                score -= er * 50.0
            else:
                score -= 15.0

            # ESG preference boost
            if esg_preferred and inst.get("esg") is True:
                score += 50.0

            # Sharia bonus when applicable
            if sharia_required and inst.get("sharia_compliant") is True:
                score += 50.0

            return score

        candidates.sort(key=rank_score, reverse=True)
        return candidates


universe_service = InstrumentUniverse()
