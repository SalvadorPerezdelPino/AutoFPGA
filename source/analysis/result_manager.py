import logging
import pandas as pd
from pathlib import Path
from typing import List

logger = logging.getLogger('Result Manager')

class ResultManager:
    def __init__(self):
        self._partial_results: List[pd.DataFrame] = []
        self._master_df: pd.DataFrame = pd.DataFrame()

    def add(self, result: pd.DataFrame):
        if result is not None and not result.empty:
            self._partial_results.append(result)

    def merge(self) -> pd.DataFrame:
        if not self._partial_results:
            return pd.DataFrame()
        
        self._master_df = pd.concat(self._partial_results, ignore_index=True)
        return self._master_df

    def save(self, path: Path):
        if self._master_df.empty:
            self.merge()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        self._master_df.to_csv(path, index=False, sep=';', decimal=',')
        logger.info(f"Results saved to {path}")

    @property
    def df(self):
        if self._master_df.empty and self._partial_results:
            self.merge()
        return self._master_df