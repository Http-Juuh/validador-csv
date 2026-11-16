import tempfile
import unittest
from pathlib import Path
from validador import validate

class ValidatorTests(unittest.TestCase):
    def report(self, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'dados.csv'
            path.write_text(text, encoding='utf-8')
            return validate(path)

    def test_valid(self):
        self.assertTrue(self.report('pedido_id,data,valor,status\nA,2024-02-29,1.25,concluido\n')['valido'])

    def test_multiple_errors(self):
        r = self.report('pedido_id,data,valor,status\nA,2025-02-29,-1,x\nA,,NaN,pendente\n')
        self.assertEqual(len(r['erros']), 6)
        self.assertEqual(r['registros'], 2)

    def test_missing_column(self):
        self.assertIn('coluna_ausente', [e['regra'] for e in self.report('pedido_id,data\n1,2025-01-01\n')['erros']])

    def test_duplicate_header(self):
        self.assertFalse(self.report('pedido_id,data,valor,status,status\n')['valido'])

    def test_empty_data(self):
        self.assertFalse(self.report('pedido_id,data,valor,status\n')['valido'])

    def test_extra_field(self):
        r = self.report('pedido_id,data,valor,status\nA,2025-01-01,1,pendente,extra\n')
        self.assertEqual(r['erros'][0]['regra'], 'quantidade_de_campos_incorreta')

    def test_nonfinite_and_precision(self):
        for value in ['Infinity', 'NaN', '1.001']:
            with self.subTest(value=value):
                self.assertFalse(self.report(f'pedido_id,data,valor,status\nA,2025-01-01,{value},pendente\n')['valido'])

    def test_bom(self):
        self.assertTrue(self.report('\ufeffpedido_id,data,valor,status\nA,2025-01-01,1,pendente\n')['valido'])

if __name__ == '__main__':
    unittest.main()
