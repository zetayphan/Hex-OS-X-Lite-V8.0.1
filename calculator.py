"""HEX OS X V34 subsystem adapter: calculator."""
def run(ctx):
 import ast,operator
 ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow}
 def calc(n):
  if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -calc(n.operand)
  if isinstance(n,ast.BinOp) and type(n.op) in ops:return ops[type(n.op)](calc(n.left),calc(n.right))
  raise ValueError('unsupported expression')
 expr=str(ctx['data'].get('expression','0'))[:100];v=calc(ast.parse(expr,mode='eval').body);assert abs(v)<1e100,'result too large';return {'expression':expr,'value':v}
