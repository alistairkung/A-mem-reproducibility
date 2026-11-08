gates = action_configuration(condition)
tree = ast.parse(verified_author_bytes(Path(root), 'memory_layer.py'))
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
           and n.name == 'AgenticMemorySystem')
method = copy.deepcopy(next(n for n in cls.body
                   if isinstance(n, ast.FunctionDef) and n.name == '_evolve'))
for node in ast.walk(method):
    if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
        test = node.test
        if (isinstance(test.left, ast.Name) and test.left.id == 'action'
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value in gates):
            action = test.comparators[0].value
            node.test = ast.copy_location(
                ast.BoolOp(op=ast.And(), values=[test, ast.Constant(gates[action])]), test)
