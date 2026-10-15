import json
from pathlib import Path

for minimum,expected in [(30,{'de_novo_indel':30,'de_novo_SV':60}),(50,{'de_novo_SV':60})]:
    root=Path(f'results/demo{minimum}')
    rows=[json.loads(l) for l in (root/'calls/high_confidence_candidates.jsonl').read_text().splitlines()]
    assert {r['variant_class']:r['delta'] for r in rows}==expected
    assert json.loads((root/'calls/status.json').read_text())['stage']=='COMPLETE'
    assert json.loads((root/'benchmark.json').read_text())['one_to_one_compatible']==len(expected)
    assert json.loads((root/'provenance.inputs.json').read_text())['truth_used'] is False
print('Synthetic SV/indel workflow, input provenance and diagnostic benchmark passed.')
