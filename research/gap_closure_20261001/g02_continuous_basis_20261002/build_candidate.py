"""Create one separate endpoint-factored diagnostic bank and optional strict native build."""
import argparse
import json
from basis_representation import build_candidate, compile_kernel

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-npz',required=True);p.add_argument('--original-metadata',required=True)
    p.add_argument('--expected-npz-sha256',required=True);p.add_argument('--expected-metadata-sha256',required=True)
    p.add_argument('--out',required=True);p.add_argument('--native-out');p.add_argument('--compiler',default='gfortran')
    a=p.parse_args();m=build_candidate(a.original_npz,a.original_metadata,a.out,a.expected_npz_sha256,a.expected_metadata_sha256)
    print(json.dumps({'identity':m['identity'],'candidate_npz_sha256':m['candidate_npz_sha256']}))
    if a.native_out: print(json.dumps(compile_kernel(a.native_out,a.compiler)))

if __name__=='__main__':main()
