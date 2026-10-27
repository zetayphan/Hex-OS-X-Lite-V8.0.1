"""HEX OS X V34 subsystem adapter: quantum."""
def run(ctx):
 import math
 n=int(ctx['data'].get('qubits',2));assert 1<=n<=8
 return {'qubits':n,'basis_states':2**n,'note':'Use /api/quantum/experiment for gate simulation'}
