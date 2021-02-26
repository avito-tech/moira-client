from unittest import TestCase

from moira_client.expression import convert_python_expression, ConvertError


class ExprTest(TestCase):
    def test_garbage(self):
        exprs = (
            'kokoko',
            'True = False',
            '      bad\nindent'
            ';;;;;;;;;a=2;;;;;'
        )
        for expr in exprs:
            with self.assertRaises(ConvertError):
                convert_python_expression(expr)

    def test_single_if_else_correct(self):
        exprs = (
            'ERROR if t1>11 else OK',
            'ERROR if t2==12 else OK',
            'ERROR if t3!=13 else OK',
            'ERROR if t4<=14 else OK',
            'ERROR if t5>=15 else OK',
            'KOKO if t6<t7 else OKOK',
        )

        expected = (
            '(t1 > 11) ? ERROR : OK',
            '(t2 == 12) ? ERROR : OK',
            '(t3 != 13) ? ERROR : OK',
            '(t4 <= 14) ? ERROR : OK',
            '(t5 >= 15) ? ERROR : OK',
            '(t6 < t7) ? KOKO : OKOK',
        )
        for expr, expected in zip(exprs, expected):
            actual = convert_python_expression(expr)
            self.assertEqual(expected, actual)

    def test_single_if_else_malformed(self):
        exprs = (
            'ERROR if t1&11 else OK',
            'ERROR if t2>11 else',
            'if t1>11 else',
            'if t111 else OK',
        )
        for expr in exprs:
            with self.assertRaises(ConvertError):
                convert_python_expression(expr)

    def test_multi_expr_correct(self):
        exprs = (
            'ERROR if t1>1 else FOO if t2>2 else BAR if t3>3 else BAZ',
            'ERROR if t1>1 else FOO if t2>2 and (tx >3 or ty == 3) else BAR if t3>3 else BAZ',
        )

        expected = (
            '(t1 > 1) ? ERROR : ((t2 > 2) ? FOO : ((t3 > 3) ? BAR : BAZ))',
            '(t1 > 1) ? ERROR : (((t2 > 2) && ((tx > 3) || (ty == 3))) ? FOO : ((t3 > 3) ? BAR : BAZ))'
        )
        for expr, expected in zip(exprs, expected):
            actual = convert_python_expression(expr)
            self.assertEqual(expected, actual)
