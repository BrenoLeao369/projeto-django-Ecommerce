from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpRequest, HttpResponse, Http404
from django.contrib import messages
from utils import utils

from product.models import Variacao
from .models import Pedido, ItemPedido
# Create your views here.

class DispatchLoginRequiredMixin(View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):

        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self, *args, **kwargs): 
        qs = super().get_queryset(*args, **kwargs)

        qs = qs.filter(user=self.request.user)
        return qs


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name='pedidos/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name ='pedido'

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         pedido = getattr(self, 'object', None)
         if pedido is None:
             raise Http404('Pedido não encontrado')

         itens_qs = ItemPedido.objects.filter(pedido=pedido)
         itens = []
         for item in itens_qs:
             quantidade = item.quantidade or 0
             try:
                 preco_total = float(item.preco or 0)
             except Exception:
                 preco_total = 0.0
             preco_unit = (preco_total / quantidade) if quantidade else 0.0
             itens.append({
                 'produto': item.produto,
                 'variacao': item.variacao,
                 'imagem': item.imagem,
                 'quantidade': quantidade,
                 'preco_unit': preco_unit,
                 'preco_total': preco_total,
             })

         context['itens_pedido'] = itens
         context['total'] = pedido.total
         context['qtd_total'] = pedido.qtd_total
         context['status'] = pedido.get_status_display()
         return context

class SalvarPedido(View):
    template_name = 'pedidos/pagar.html'

    def get(self, *args, **kwarks):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'você precisa fazer login'
            )
            return redirect('perfil:Criar')
        
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'carrinho vazio'
            )
            return redirect('Produto:lista')
        
        carrinho = self.request.session.get('carrinho')
        # Garante que iteramos apenas sobre chaves numéricas válidas
        carrinho_variacao_ids = [int(k) for k in (carrinho or {}).keys() if str(k).isdigit()]
        bd_variacoes = list(
            Variacao.objects.select_related('produto').filter(pk__in=carrinho_variacao_ids)
        )

        for variacao in bd_variacoes:
            key_str = str(variacao.pk)
            key_int = variacao.pk
            estoque = variacao.estoque

            # Suporta chaves do carrinho tanto como string quanto como int
            item = None
            if isinstance(carrinho, dict):
                if key_str in carrinho:
                    item = carrinho.get(key_str)
                elif key_int in carrinho:
                    item = carrinho.get(key_int)

            # Validação defensiva: item deve ser um dict com os dados esperados
            if not isinstance(item, dict):
                messages.error(self.request, 'carrinho inválido — remova itens inválidos e tente novamente')
                return redirect('Produto:carrinho')

            qtd_carrinho = int(item.get('quantidade', 0))
            preco_unt = float(item.get('preco_unitario', 0) or 0)
            preco_unt_promo = float(item.get('preco_unitario_promocional', 0) or 0)

            if estoque < qtd_carrinho:
                item['quantidade'] = estoque
                item['preco_quantitativo'] = estoque * preco_unt
                item['preco_quantitativo_promocional'] = estoque * preco_unt_promo

                messages.error(
                    self.request,
                    'estoque insuficiente de algum produto em seu carrinho'
                )
                # grava alterações na sessão
                self.request.session['carrinho'] = carrinho
                self.request.session.save()
                return redirect('Produto:carrinho')

            # garante que os totais por item existam quando há estoque suficiente
            item.setdefault('preco_quantitativo', qtd_carrinho * preco_unt)
            item.setdefault('preco_quantitativo_promocional', qtd_carrinho * preco_unt_promo)

        # salva possíveis alterações feitas no carrinho
        self.request.session['carrinho'] = carrinho
        self.request.session.save()

        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)

        pedido = Pedido(
            user=self.request.user,
            total=valor_total_carrinho,
            qtd_total= qtd_total_carrinho,
            status='C'
        )

        pedido.save()

        # Filtra apenas entradas válidas do carrinho antes de criar itens
        itens_para_criar = []
        for v in (carrinho or {}).values():
            if not isinstance(v, dict):
                continue
            itens_para_criar.append(
                ItemPedido(
                    pedido=pedido,
                    produto=v.get('produto_nome'),
                    produto_id=v.get('produto_id'),
                    variacao=v.get('variacao_nome'),
                    variacao_id=v.get('variacao_id'),
                    preco=v.get('preco_quantitativo', 0),
                    preco_promocional=v.get('preco_quantitativo_promocional', 0),
                    quantidade=v.get('quantidade', 0),
                    imagem=v.get('imagem'),
                )
            )

        if itens_para_criar:
            ItemPedido.objects.bulk_create(itens_para_criar)

        del self.request.session['carrinho']
        renderiza = render(self.request, self.template_name)

        return redirect(reverse('pedido:pagar', kwargs={'pk': pedido.pk}))

class Detalhes(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalhe.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedido = getattr(self, 'object', None)
        if pedido is None:
            raise Http404('Pedido não encontrado')

        itens_qs = ItemPedido.objects.filter(pedido=pedido)
        itens = []
        for item in itens_qs:
            quantidade = item.quantidade or 0
            try:
                preco_total = float(item.preco or 0)
            except Exception:
                preco_total = 0.0
            preco_unit = (preco_total / quantidade) if quantidade else 0.0
            itens.append({
                'produto': item.produto,
                'variacao': item.variacao,
                'imagem': item.imagem,
                'quantidade': quantidade,
                'preco_unit': preco_unit,
                'preco_total': preco_total,
            })

        context['itens_pedido'] = itens
        context['total'] = pedido.total
        context['qtd_total'] = pedido.qtd_total
        context['status'] = pedido.get_status_display()
        return context

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user)
    
class lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedidos/lista.html'
    paginate_by = 10
    ordering = ['-id']