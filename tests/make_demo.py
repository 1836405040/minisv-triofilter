"""Generate a tiny family with a 30 bp indel and a 60 bp SV, no real samples."""
import json
from pathlib import Path
import pysam
import yaml

def main():
    root=Path('demo').resolve();root.mkdir(exist_ok=False)
    ref=root/'reference.fa';ref.write_text('>chr1\n'+'A'*1000+'\n');pysam.faidx(str(ref))
    members={}
    for sample,length in [('father',0),('mother',0),('child30',30),('child60',60)]:
        bam=root/(sample+'.bam')
        with pysam.AlignmentFile(bam,'wb',header={'SQ':[{'SN':'chr1','LN':1000}]}) as f:
            for i in range(12):
                n=length if i<4 else 0
                r=pysam.AlignedSegment();r.query_name=f'{sample}.{i}';r.reference_id=0;r.reference_start=0
                r.mapping_quality=60;r.flag=16 if i%2 else 0
                r.query_sequence='A'*(1000+n);r.cigartuples=[(0,400),(1,n),(0,600)] if n else [(0,1000)]
                f.write(r)
        pysam.index(str(bam));members[sample]=dict(sample=sample,bam=str(bam))
    empty=root/'c3.vcf';empty.write_text('##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n')
    children=[]
    for sample,length in [('child30',30),('child60',60)]:
        directory=root/sample;directory.mkdir()
        models={k:'A'*(100+length if k=='C0.0' else 100) for k in ('C0.0','C1.0','F0.0','F1.0','M0.0','M1.0')}
        reads={}
        for role,name in [('C',sample),('F','father'),('M','mother')]:
            reads[role]=[dict(name=f'{name}.{i}',length=100+length if role=='C' and i<4 else 100,
                distances={k:abs((100+length if role=='C' and i<4 else 100)-len(s)) for k,s in models.items()}) for i in range(12)]
        event=dict(child=sample,trid='chr1_300_400_demo',models=models,full_reads=reads,
            family={r:dict(sample=s) for r,s in [('C',sample),('F','father'),('M','mother')]},
            transmissions=[dict(total_edit_distance=length,paternal_child='C0.0',father='F0.0',maternal_child='C1.0',mother='M0.0')])
        (directory/'chr1_300_400_demo.json').write_text(json.dumps(event))
        children.append(dict(members[sample],local_directory=str(directory),c3_vcf=str(empty)))
    manifest=root/'family.json';manifest.write_text(json.dumps(dict(reference=str(ref),father=members['father'],mother=members['mother'],children=children),indent=2))
    truth=root/'truth.tsv';truth.write_text('truth_id\tsample\tchrom\tstart\tend\ttype\tdelta\tbasis\n'+'\n'.join(
        f't{n}\tchild{n}\tchr1\t300\t400\tINS\t{n}\tPARENT_ALLELE' for n in (30,60))+'\n')
    mask=root/'mask.bed';mask.write_text('# Synthetic example: no masked intervals\n')
    config=dict(runs={f'demo{n}':dict(manifest=str(manifest),minimum_variant_length=n,threads=2,mem_mb=2000) for n in (30,50)},
        benchmarks={f'demo{n}':dict(truth=str(truth),mask=str(mask)) for n in (30,50)})
    (root/'config.yaml').write_text(yaml.safe_dump(config))

if __name__=='__main__':main()
