from django.db import models
from django.utils.text import slugify
import misaka
from django.urls import reverse
# Create your models here.
from django.contrib.auth.models import User

class Product(models.Model):
    # south_indian = 'SI'
    # meals = 'CH'
    # italian = 'IT'
    # chinese = 'CN'
    # category_choices = ((south_indian,'South Indian'),(meals,'Meals'),(italian,'Italian'),(chinese,'Chinese'))
    indian = 'I'
    chinese = 'CH'
    continental = 'CN'
    beverages = 'BV'
    category_choices = ((indian,'Indian'),(chinese,'Chinese'),(continental,'Continental'),(beverages,'Beverages'))
    category = models.CharField(max_length=20,choices=category_choices)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=250,null=True,blank=True)
    description = models.TextField(max_length=200)
    # description_html = models.TextField(editable=False,default='',blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    prep_time = models.IntegerField()
    image = models.ImageField(upload_to='images/', blank=True)

    class Meta:
        ordering = ('name', )
        index_together = (('id', 'slug'),)

    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        self.description_html = misaka.html(self.description)
        super(Product,self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('products:single',kwargs={'slug':self.slug})

    def get_add_to_cart_url(self):
        return reverse("products:add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("products:remove-from-cart", kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price
    #
    # def get_total_discount_item_price(self):
    #     return self.quantity * self.product.discount_price
    #
    # def get_amount_saved(self):
    #     return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        # if self.item.discount_price:
        #     return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem,related_name='items')
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    slug=models.SlugField(max_length=250,null=True,blank=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def save(self,*args,**kwargs):
        userstring = str(self.user.username)
        slug_str = userstring.join(str(self.id))
        self.slug = slugify(slug_str)
        super(Order,self).save(*args,**kwargs)

    # def get_order_ready_url(self):
    #     return reverse("products:order-ready",kwargs={'slug':self.slug})
# class Order(models.Model):
#     user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
#     in_cart = models.BooleanField(default=True)
#     is_delivered = models.BooleanField(default=False)
#     is_prepared = models.BooleanField(default=False)
#
# class OrderItem(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
#     quantity = models.IntegerField()
#     #OrderID
#     order_id = models.ForeignKey(Order,on_delete = models.CASCADE)

########################################################################################################

# class Item(models.Model):
#     title = models.CharField(max_length=100)
#     price = models.FloatField()
#     discount_price = models.FloatField(blank=True, null=True)
#     category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
#     label = models.CharField(choices=LABEL_CHOICES, max_length=1)
#     slug = models.SlugField()
#     description = models.TextField()
#     image = models.ImageField()
#
#     def __str__(self):
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse("core:product", kwargs={
#             'slug': self.slug
#         })
#
#     def get_add_to_cart_url(self):
#         return reverse("core:add-to-cart", kwargs={
#             'slug': self.slug
#         })
#
#     def get_remove_from_cart_url(self):
#         return reverse("core:remove-from-cart", kwargs={
#             'slug': self.slug
#         })


# class OrderItem(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     ordered = models.BooleanField(default=False)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=1)
#
#     def __str__(self):
#         return f"{self.quantity} of {self.item.title}"
#
#     def get_total_item_price(self):
#         return self.quantity * self.item.price
#
#     def get_total_discount_item_price(self):
#         return self.quantity * self.item.discount_price
#
#     def get_amount_saved(self):
#         return self.get_total_item_price() - self.get_total_discount_item_price()
#
#     def get_final_price(self):
#         if self.item.discount_price:
#             return self.get_total_discount_item_price()
#         return self.get_total_item_price()
#
#
# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.CASCADE)
#     ref_code = models.CharField(max_length=20, blank=True, null=True)
#     items = models.ManyToManyField(OrderItem)
#     start_date = models.DateTimeField(auto_now_add=True)
#     ordered_date = models.DateTimeField()
#     ordered = models.BooleanField(default=False)
#     shipping_address = models.ForeignKey(
#         'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
#     billing_address = models.ForeignKey(
#         'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
#     payment = models.ForeignKey(
#         'Payment', on_delete=models.SET_NULL, blank=True, null=True)
#     coupon = models.ForeignKey(
#         'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
#     being_delivered = models.BooleanField(default=False)
#     received = models.BooleanField(default=False)
#     refund_requested = models.BooleanField(default=False)
#     refund_granted = models.BooleanField(default=False)
#
#     '''
#     1. Item added to cart
#     2. Adding a billing address
#     (Failed checkout)
#     3. Payment
#     (Preprocessing, processing, packaging etc.)
#     4. Being delivered
#     5. Received
#     6. Refunds
#     '''
#
#     def __str__(self):
#         return self.user.username
#
#     def get_total(self):
#         total = 0
#         for order_item in self.items.all():
#             total += order_item.get_final_price()
#         if self.coupon:
#             total -= self.coupon.amount
#         return total
