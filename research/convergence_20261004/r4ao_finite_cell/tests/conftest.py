from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'vendor_r4am/source'),str(ROOT/'vendor_r4am/vendor'),str(ROOT/'vendor_r4an')]
