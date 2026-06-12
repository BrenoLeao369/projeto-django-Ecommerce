def formata_preco(val):
    """Formata um valor numérico para moeda BR (R$ 0,00).

    Aceita int, float, Decimal ou string (ex: '19.9', '19,9', 'R$ 19,90').
    Retorna string formatada segura mesmo quando o input for inválido.
    """
    if val is None:
        return 'R$ 0,00'

    # normaliza strings: remove símbolo e transforma vírgula em ponto
    if isinstance(val, str):
        s = val.strip().replace('R$', '').replace('r$', '').strip()
        s = s.replace('.', '').replace(',', '.') if ',' in s else s
        try:
            num = float(s)
        except Exception:
            return 'R$ 0,00'
    else:
        try:
            num = float(val)
        except Exception:
            return 'R$ 0,00'

    return f'R$ {num:.2f}'.replace('.', ',')

def cart_total_qtd(carrinho):
    if not carrinho:
        return 0
    if isinstance(carrinho, dict):
        return sum(item.get('quantidade', 0) for item in carrinho.values())
    return sum(item.get('quantidade', 0) for item in carrinho)

def cart_totals(carrinho):
    total = 0.0
    if not carrinho:
        return 0.0
    for item in (carrinho or {}).values():
        if not isinstance(item, dict):
            continue
        raw = item.get('preco_quantitativo_promocional') or item.get('preco_quantitativo') or 0
        # tenta normalizar strings como '19,90' ou 'R$ 19.90'
        if isinstance(raw, str):
            s = raw.strip().replace('R$', '').replace('r$', '').strip()
            s = s.replace('.', '').replace(',', '.') if ',' in s else s
            try:
                val = float(s)
            except Exception:
                val = 0.0
        else:
            try:
                val = float(raw)
            except Exception:
                val = 0.0
        total += val
    return total