from django.db import models
from PIL import Image
import os
from django.conf import settings

# Create your models here.
class Product(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField
    imagem = models.ImageField(upload_to='product_image/%Y/%m', blank=True, null=True)
    slug = models.SlugField(unique=True)
    preco_marketing = models.FloatField()
    preco_marketing_promocional = models.FloatField(default=0)
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', "variação"),
            ('S', "Simples"),
            )
    )

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
        super().save(*args, **kwargs)
        
        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.nome
    
class Variacao(models.Model):
    produto = models.ForeignKey(Product, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    preco = models.FloatField()
    preco_prompcional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'