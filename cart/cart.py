from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):
    def __init__(self, request):
        """
        Inicializa o carrinho de compras.
        :param request:
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # salva um carrinho vazio na sessao
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Adiciona um produto no carrinho de compras ou atializar a sua quantidade.
        :param product:
        :param quantity:
        :param override_quantity:
        :return:
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # marca a sessão como "modificada"para garantir que ela seja salva.
        self.session.modified = True

    def remove(self, product):
        """
        Remove um produto do carrinho de compras
        :param product:
        :return:
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """"
        Itera pelos itens do carrinho de compras e obtém os produtos do banco de dados
        """
        products_ids = self.cart.keys()
        # Obtem os objetos referentes aos produtos e os adiciona no carrinho.
        products = Product.objects.filter(category_id__in=products_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
            for item in cart.values():
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        """
        Contabiliza todos os itens que estão no carrinho de compras.
        :return:
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove o carrinho da sessão
        del self.session[settings.CART_SESSION_ID]
        self.save()
