"""CLI de qualidade para CSV de pedidos. Codigo de saida: 0 valido, 1 invalido, 2 erro de entrada."""
import argparse
import csv
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ('pedido_id', 'data', 'valor', 'status')

def validate(path):
    errors, seen, count = [], set(), 0
    def add(line, field, rule):
        errors.append({'linha': line, 'campo': field, 'regra': rule})
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            add(1, '*', 'cabecalho_duplicado')
        for field in REQUIRED:
            if field not in headers:
                add(1, field, 'coluna_ausente')
        if errors:
            return {'valido': False, 'registros': 0, 'erros': errors}
        for row in reader:
            count += 1
            line = reader.line_num
            if None in row or any(v is None for v in row.values()):
                add(line, '*', 'quantidade_de_campos_incorreta')
            values = {key: (row.get(key) or '').strip() for key in REQUIRED}
            for key, value in values.items():
                if not value:
                    add(line, key, 'obrigatorio')
            ident = values['pedido_id']
            if ident:
                if ident in seen:
                    add(line, 'pedido_id', 'duplicado')
                seen.add(ident)
            if values['data']:
                try:
                    parsed = date.fromisoformat(values['data'])
                    if parsed.isoformat() != values['data']:
                        raise ValueError()
                except ValueError:
                    add(line, 'data', 'data_iso_invalida')
            if values['valor']:
                try:
                    amount = Decimal(values['valor'])
                    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
                        raise ValueError()
                except (InvalidOperation, ValueError):
                    add(line, 'valor', 'valor_monetario_invalido')
            if values['status'] and values['status'] not in {'concluido', 'cancelado', 'pendente'}:
                add(line, 'status', 'categoria_invalida')
    if count == 0:
        add(1, '*', 'sem_registros')
    return {'valido': not errors, 'registros': count, 'erros': errors}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path)
    parser.add_argument('--saida', type=Path, help='Salvar relatorio JSON sem modificar o CSV')
    args = parser.parse_args()
    if args.saida and args.saida.resolve() == args.arquivo.resolve():
        parser.error('A saida nao pode sobrescrever o CSV de entrada')
    try:
        report = validate(args.arquivo)
        output = json.dumps(report, ensure_ascii=False, indent=2)
        if args.saida:
            args.saida.write_text(output + '\n', encoding='utf-8')
        print(output)
        return 0 if report['valido'] else 1
    except (OSError, UnicodeError, csv.Error) as exc:
        print(json.dumps({'erro_entrada': str(exc)}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
