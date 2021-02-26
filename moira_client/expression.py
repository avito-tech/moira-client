import ast


class ConvertError(Exception):
    pass


def _parse_cmp_op(node):
    if isinstance(node, ast.Lt):
        return '<'
    if isinstance(node, ast.Gt):
        return '>'
    if isinstance(node, ast.LtE):
        return '<='
    if isinstance(node, ast.GtE):
        return '>='
    if isinstance(node, ast.Eq):
        return '=='
    if isinstance(node, ast.NotEq):
        return '!='

    raise ConvertError('unknown op node={}'.format(ast.dump(node)))


def _parse_logic_op(node):
    if isinstance(node, ast.Or):
        return '||'
    if isinstance(node, ast.And):
        return '&&'
    raise ConvertError('unknown logic op node={}'.format(ast.dump(node)))


def _parse_comparator(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.BoolOp):
        return _parse_boolop(node)
    elif isinstance(node, ast.Compare):
        return _parse_compare(node)
    raise ConvertError('unknown comparator node={}'.format(ast.dump(node)))


def _parse_boolop(node):
    need_parens = len(node.values) > 1
    cmps = []
    for v in node.values:
        r = _parse_comparator(v)
        if need_parens:
            r = '(' + r + ')'
        cmps.append(r)

    op = _parse_logic_op(node.op)
    op = f' {op} '
    return op.join(cmps)


def _parse_compare(node):
    if len(node.ops) != 1 or len(node.comparators) != 1:
        raise ConvertError('multiple ops/comparators {}'.format(ast.dump(node.body)))

    op = _parse_cmp_op(node.ops[0])
    right = _parse_comparator(node.comparators[0])
    left = node.left.id
    return f'{left} {op} {right}'


def _parse_ifnode(node):
    cond = _parse_comparator(node.test)

    if isinstance(node.orelse, ast.IfExp):
        else_ = _parse_ifnode(node.orelse)
        else_ = '(' + else_ + ')'
    else:
        else_ = node.orelse.id

    if_ = node.body.id

    return f'({cond}) ? {if_} : {else_}'


def _convert_expression(expr):
    node = ast.parse(expr, mode='eval')
    if not isinstance(node, ast.Expression):
        raise ConvertError('unknown root node={}'.format(ast.dump(node)))

    if not isinstance(node.body, ast.IfExp):
        raise ConvertError('unknown if node={}'.format(ast.dump(node.body)))

    return _parse_ifnode(node.body)


def convert_python_expression(expr):
    """
    converts old python moira expression to new govaluate expression
    """
    try:
        return _convert_expression(expr)
    except Exception as e:
        raise ConvertError("convert error") from e
