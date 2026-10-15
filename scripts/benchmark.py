"""Post-discovery diagnostic matching; never estimates precision from sparse truth."""
import argparse
import csv
import json
from pathlib import Path


def load_mask(path):
    rows=[]
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith('#'):continue
        c,s,e,*_=line.split();rows.append((c,int(s),int(e)))
    return rows


def regular(row,mask):
    if row['chrom'] not in {'chr'+str(i) for i in range(1,23)}:return False
    start=int(row['start']);end=max(start+1,int(row['end']))
    return not any(c==row['chrom'] and start<e and s<end for c,s,e in mask)


def compatible(t,e,tolerance,ratio):
    if any(t[k]!=e[k] for k in ('sample','chrom','type','basis')):return False
    if abs(int(t['start'])-int(e['start']))>tolerance:return False
    a,b=abs(int(t['delta'])),abs(int(e['delta']))
    return a>0 and b>0 and min(a,b)/max(a,b)>=ratio


def evaluate(truth,events,mask,tolerance=100,ratio=.5):
    if tolerance<0 or not 0<ratio<=1:raise ValueError('Invalid matching parameters')
    if len({r['truth_id'] for r in truth})!=len(truth):raise ValueError('Duplicate truth_id')
    if len({r['event_id'] for r in events})!=len(events):raise ValueError('Duplicate event_id')
    unsupported=[e for e in events if e.get('type') not in ('INS','DEL') or e.get('delta') is None]
    selected=[e for e in events if e not in unsupported and regular(e,mask)]
    rows=[]
    for t in truth:
        supported=t.get('type') in ('INS','DEL') and t.get('delta') is not None
        inside=supported and regular(t,mask)
        matches=[e for e in selected if compatible(t,e,tolerance,ratio)] if inside else []
        rows.append(dict(truth_id=t['truth_id'],in_scope=inside,
            assessment_status='SUPPORTED' if supported else 'UNSUPPORTED_STRUCTURAL_BENCHMARK',
            matches=[dict(event_id=e['event_id'],tier=e['tier']) for e in matches]))
    # Do not collapse overlapping truth records into an inflated recovery count.
    event_to_truth={}
    def augment(i,seen):
        for m in rows[i]['matches']:
            key=m['event_id']
            if key in seen:continue
            seen.add(key)
            if key not in event_to_truth or augment(event_to_truth[key],seen):
                event_to_truth[key]=i;return True
        return False
    for i in range(len(rows)):augment(i,set())
    return dict(unsupported_event_ids=[e['event_id'] for e in unsupported],metric='diagnostic_same_basis_compatibility',truth_in_scope=sum(r['in_scope'] for r in rows),
        one_to_one_compatible=len(event_to_truth),events_in_scope=len(selected),
        assignments={e:rows[i]['truth_id'] for e,i in event_to_truth.items()},rows=rows,
        tolerance_bp=tolerance,length_ratio=ratio,precision=None,
        interpretation='No sequence equivalence or de novo certification; unmatched events are not labeled false positives.')


def main():
    p=argparse.ArgumentParser()
    for k in ('events','truth','mask','output'):p.add_argument('--'+k,required=True)
    p.add_argument('--tolerance',type=int,default=100);p.add_argument('--ratio',type=float,default=.5)
    a=p.parse_args()
    with open(a.truth) as f:truth=list(csv.DictReader(f,delimiter='\t'))
    events=[json.loads(l) for l in Path(a.events).read_text().splitlines() if l.strip()]
    result=evaluate(truth,events,load_mask(a.mask),a.tolerance,a.ratio)
    Path(a.output).write_text(json.dumps(result,indent=2))

if __name__=='__main__':main()
