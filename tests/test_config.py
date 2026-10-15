import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from workflow_support import validate_runs

@pytest.mark.parametrize('spec',[dict(truth='truth.tsv'),dict(minimum_variant_length=34),dict(parent_readability_policy='c3_or_local')])
def test_rejects_truth_leakage_or_historical_policies(spec):
    with pytest.raises(ValueError):validate_runs(dict(runs={'run':spec}))

def test_rejects_path_traversal():
    with pytest.raises(ValueError):validate_runs(dict(runs={'../x':{}}))
