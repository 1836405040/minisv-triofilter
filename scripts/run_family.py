"""Run the pinned tool in a fresh attempt directory; retain failed attempts."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import uuid


def main():
    p=argparse.ArgumentParser()
    for key in ('manifest','output','policy'):p.add_argument('--'+key,required=True)
    p.add_argument('--minimum',type=int,choices=(30,50),required=True)
    p.add_argument('--rate',type=float,required=True);p.add_argument('--threads',type=int,required=True)
    a=p.parse_args();out=Path(a.output)
    if out.exists():raise FileExistsError(f'Refusing to overwrite {out}; use a new run ID')
    attempt=out.parent/('.attempts/'+out.name+'-'+uuid.uuid4().hex)
    attempt.mkdir(parents=True)
    c=json.loads(Path(a.manifest).read_text())
    c.update(minimum_variant_length=a.minimum,confidence_policy='strict',parent_readability_policy=a.policy)
    manifest=attempt/'manifest.json';manifest.write_text(json.dumps(c,indent=2))
    cmd=['minisv','denovo','run','--manifest',str(manifest),'--output',str(attempt/'result'),
        '--workers',str(a.threads),'--error-rate',str(a.rate)]
    (attempt/'command.json').write_text(json.dumps(dict(argv=cmd,started=datetime.now(timezone.utc).isoformat()),indent=2))
    subprocess.run(cmd,check=True)
    status=json.loads((attempt/'result/status.json').read_text())
    if status['stage']!='COMPLETE':raise RuntimeError('Tool did not complete')
    (attempt/'result').rename(out)

if __name__=='__main__':main()
