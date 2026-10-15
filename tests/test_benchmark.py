import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from benchmark import evaluate

def row(**kw):
    return dict(dict(sample='kid',chrom='chr1',start=300,end=400,type='INS',delta=60,
        basis='PARENT_ALLELE',tier='HIGH_CONFIDENCE_CANDIDATE'),**kw)

def test_duplicate_truth_cannot_reuse_one_candidate():
    result=evaluate([row(truth_id='a'),row(truth_id='b')],[row(event_id='e')],[])
    assert result['one_to_one_compatible']==1
    assert result['precision'] is None

def test_basis_family_and_mask_are_not_interchangeable():
    truth=[row(truth_id='a')]
    for change in ({'basis':'REFERENCE'},{'sample':'other'},{'type':'DEL'}):
        assert evaluate(truth,[row(event_id='e',**change)],[])['one_to_one_compatible']==0
    assert evaluate(truth,[row(event_id='e')],[('chr1',399,500)])['events_in_scope']==0

def test_insertion_boundary_is_masked_as_one_base():
    t=row(truth_id='a',start=300,end=300)
    e=row(event_id='e',start=300,end=300)
    assert evaluate([t],[e],[('chr1',300,301)])['truth_in_scope']==0
