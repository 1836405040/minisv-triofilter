import argparse
from collections import Counter
import csv
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();counts=Counter()
    for line in Path(a.input).read_text().splitlines():
        e=json.loads(line)
        counts[(e['sample'],e['variant_class'],e['tier'],e['basis'])]+=1
    with open(a.output,'w',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['sample','variant_class','tier','basis','events'])
        for keys,n in sorted(counts.items()):w.writerow([*keys,n])
if __name__=='__main__':main()
