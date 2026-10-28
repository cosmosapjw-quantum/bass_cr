#!/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python
import sys
lines=sys.stdin.read().splitlines()
n,m,s,t,b=lines[1].split()
print(lines[0])
print(n,m,0,0,0)
print('\n'.join(['0']*int(m)))
