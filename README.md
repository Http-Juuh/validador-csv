# Validador de CSV de pedidos

**Python · Qualidade de dados · CLI · Testes automatizados**

Ferramenta que verifica arquivos antes de uma analise ou carga em banco.
Identifica erros por linha e campo, produz JSON e preserva o arquivo original.
Os exemplos incluidos sao ficticios.

## Executar

Python 3.10+, apenas biblioteca padrao:

```bash
python validador.py exemplo-valido.csv
python validador.py exemplo-invalido.csv --saida relatorio-exemplo.json
python -m unittest -v
```

O segundo comando retorna **codigo 1 de proposito**, pois o exemplo contem erros.
Codigos: `0` = valido, `1` = regras violadas, `2` = erro de leitura ou argumentos.
Consulte [o relatorio do exemplo](relatorio-exemplo.json).

## Contrato do CSV

UTF-8 (com ou sem BOM), separador virgula, cabecalho obrigatorio. Colunas adicionais sao permitidas.

| Coluna | Regra |
|---|---|
| pedido_id | Texto preenchido e unico apos remover espacos nas extremidades |
| data | Data real no formato AAAA-MM-DD |
| valor | Decimal finito, nao negativo, com ponto e no maximo duas casas decimais |
| status | concluido, cancelado ou pendente, em minusculas |

Tambem rejeita cabecalhos duplicados, colunas obrigatorias ausentes, registros sem campos suficientes ou com campos excedentes e arquivos sem registros.
A linha informada e a linha fisica final do registro, conforme `csv.DictReader.line_num` (relevante para campos com quebra de linha).

## Exemplo de uso em um fluxo

Execute a validacao antes de carregar os pedidos. Interrompa a carga quando o codigo de saida for diferente de zero e consulte o JSON para corrigir a origem.
O relatorio registra regras, sem copiar os valores dos campos.

## Limites e evolucao

O esquema e especifico para pedidos. O programa nao verifica existencia dos produtos nem regras contabilisticas.
O processamento percorre o CSV, mas mantem IDs e erros em memoria; nao foi dimensionado para arquivos gigantes.
Proximos passos: esquema configuravel, limite de erros e suporte explicito a outros separadores.

Licenca: MIT.
