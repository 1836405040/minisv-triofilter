import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from workflow_support import manifest_assets,sha256


def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--lock',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();lock=json.loads(Path(a.lock).read_text())
    direct=json.loads(importlib.metadata.distribution('minisv').read_text('direct_url.json') or '{}')
    if (direct.get('vcs_info',{}).get('commit_id')!=lock['commit']
            or direct.get('url','').removesuffix('.git')!=lock['repository'].removesuffix('.git')):
        raise ValueError('Installed Minisv does not match tool.lock.json; install requirements.txt')
    version=subprocess.check_output(['minimap2','--version'],text=True).strip()
    if version!=lock['minimap2']:raise ValueError('minimap2 does not match lock')
    assets=[]
    for name in manifest_assets(a.manifest):
        path=Path(name);stat=path.stat()
        assets.append(dict(path=str(path.resolve()),bytes=stat.st_size,sha256=sha256(path)))
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    environment=subprocess.check_output([sys.executable,'-m','pip','freeze','--all'],text=True).splitlines()
    output.write_text(json.dumps(dict(python=sys.version,tool=direct,minimap2=version,environment=environment,
        assets=assets,truth_used=False),indent=2))

if __name__=='__main__':main()
