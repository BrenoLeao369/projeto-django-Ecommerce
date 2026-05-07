from django.db import models
from PIL import Image
import os
from django.conf import settings
from django.utils.text import slugify

# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='product_image/%Y/%m', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name="Preço")
    preco_marketing_promocional = models.FloatField(default=0, verbose_name="Preço Promo")
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', "variação"),
            ('S', "Simples"),
            )
    )

    def get_preco_formatado(self):
        return f'R$ {self.preco_marketing:.2f}'.replace('.', ',')
    get_preco_formatado.short_description = "Preço"

    def get_preco_promocional_formatado(self):
        return f'R$ {self.preco_marketing_promocional:.2f}'.replace('.', ',')
    get_preco_promocional_formatado.short_description = "Preço Promo"

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        orriginal_width, original_height = img_pil.size

        if orriginal_width <= new_width:
            img_pil.close()
            return
        
        new_height = round((new_width * original_height) / orriginal_width)

        new_img = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            quality=50,
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.nome)}'
            self.slug = slug

        super().save(*args, **kwargs)
        
        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome
    
class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50, blank=True, null=True)
    preco = models.FloatField()
    preco_prompcional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'