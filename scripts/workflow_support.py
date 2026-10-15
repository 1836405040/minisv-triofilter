"""Workflow input contracts and streaming provenance, not calling algorithms."""
import hashlib
import json
import re
from pathlib import Path


def validate_runs(config):
    runs=config.get('runs',{})
    if not runs:
        raise ValueError('Configure at least one run')
    for name, spec in runs.items():
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name):
            raise ValueError('Unsafe run identifier')
        if spec.get('minimum_variant_length',50) not in (30,50):
            raise ValueError('Production classes use minimum_variant_length 30 or 50')
        if not 0 < spec.get('error_rate',.08) < 1:
            raise ValueError('Invalid sequence tolerance')
        if spec.get('parent_readability_policy','marker_assisted') not in ('strict','marker_assisted'):
            raise ValueError('Unknown parent readability policy')
        if any(k in spec for k in ('truth','truth_vcf','truth_bed')):
            raise ValueError('Truth belongs in benchmarks, not discovery runs')
        if spec.get('threads',16)<1:
            raise ValueError('threads must be positive')
    if set(config.get('benchmarks',{}))-set(runs):
        raise ValueError('Benchmark references an unknown run')
    return runs


def manifest_assets(manifest):
    """Expose input dependencies to Snakemake, including indexes and caches."""
    manifest=Path(manifest)
    c=json.loads(manifest.read_text())
    paths=[manifest,Path(c['reference']),Path(c['reference']+'.fai')]
    for member in [c['father'],c['mother'],*c['children']]:
        bam=Path(member['bam']);paths.extend([bam,Path(str(bam)+'.bai') if Path(str(bam)+'.bai').exists() else bam.with_suffix('.bai')])
    for path in c.get('parent_assemblies',[]):
        paths.append(Path(path))
    for spec in c.get('parent_haplotype_alignments',{}).values():
        paths.extend([Path(spec['fasta']),Path(spec['fasta']+'.fai'),Path(spec['paf'])])
    for child in c['children']:
        for key in ('candidate_vcf','trgt_signal','parent_paf','parent_gsv','c3_vcf'):
            if child.get(key):paths.append(Path(child[key]))
        paths.extend(Path(p) for p in child.get('candidate_vcfs',[]))
        if child.get('local_directory'):
            files=sorted(Path(child['local_directory']).glob('*.json'))
            if not files:raise ValueError('Empty local evidence directory')
            paths.extend(files)
        else:
            d=Path(c['trgt_directory'])
            for member in (c['father'],c['mother'],child):
                for suffix in ('.sorted.vcf.gz','.sorted.vcf.gz.tbi','.spanning.sorted.bam','.spanning.sorted.bam.bai'):
                    paths.append(d/(member['sample']+suffix))
        if child.get('trgt_signal') and child.get('local_directory'):
            d=Path(c['trgt_directory']); sample=child['sample']
            paths.extend([d/(sample+'.spanning.sorted.bam'),d/(sample+'.spanning.sorted.bam.bai')])
    return sorted({str(p) for p in paths})


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
