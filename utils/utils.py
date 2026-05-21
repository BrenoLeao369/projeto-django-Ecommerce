def formata_preco(val):
    return f'R$ {val:.2f}'.replace('.',',')

def cart_total_qtd(carrinho):
    if not carrinho:
        return 0
    if isinstance(carrinho, dict):
        return sum(item.get('quantidade', 0) for item in carrinho.values())
    return sum(item.get('quantidade', 0) for item in carrinho)

def cart_totals(carrinho):
    return sum(
        [
            item.get('preco_quantitativo_promocional')
            if item.get('preco_quantitativo_promocional')
            else item.get('preco_quantitativo')
            for item
              in carrinho.values()
        ]
    )