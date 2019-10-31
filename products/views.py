from django.shortcuts import render, get_object_or_404, redirect
from .models import Product,Order,OrderItem
from django.views import generic
from django.contrib.auth.decorators import login_required
#from accounts.models import User
from django.contrib.auth.models import User
from django import template
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail
from .models import Order
from braces.views import SuperuserRequiredMixin
register = template.Library()
# Create your views here.

# class SingleProduct(generic.DetailView):
#     template_name = 'products/product_list.html'
#     model = Product
def SingleProduct(request,id):

    template_name = 'products/product_detail.html'
    context ={'product': Product.objects.get(id=id)}
    if(context is None):
        return #404
    return render(request,template_name,context)

def MultipleProducts(request):
    template_name = 'products/product_list.html'

    cat = request.GET.get('cat', 'all') #All means all categpries of food
    if cat == "all":
        context = {'products':Product.objects.all()}
    elif cat == "I":
        print("RAN")
        context = {'products':Product.objects.filter(category=Product.indian)}
    elif cat == "CN":
        context = {'products':Product.objects.filter(category=Product.continental)}
    elif cat == "BV":
        context = {'products':Product.objects.filter(category=Product.beverages)}
    elif cat == "CH":
        context = {'products':Product.objects.filter(category=Product.chinese)}
    else:
        context = {'products':Product.objects.all()}
    return render(request, template_name, context)



# @login_required
# def addToCart(request,id):
#     if request.user.is_authenticated:
#         product = Product.objects.get(id=id)
#
#         user = User.objects.get(username=request.user.username)
#         try:
#             current_cart = Order.objects.get(user=user,in_cart=True)
#         except:
#             current_cart = Order(user=user,in_cart=True)
#             current_cart.save()
#
#         order_item = OrderItem(order_id=current_cart,product=product,quantity=1)
#         order_item.save()
#         return MultipleProducts(request)

# class CheckoutView(generic.View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'order': order,
#             }
#             return render(self.request, "checkout.html", context)
#         except ObjectDoesNotExist:
#             messages.info(self.request, "You do not have an active order")
#             return redirect("products:checkout")
#
#     def post(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             return redirect("products:checkout")
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("products:summary")


class PlaceOrder(LoginRequiredMixin,generic.View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            items = order.items
            total = order.get_total()
            message = "Thanks for placing an order (Order ID-{}). Please pay ₹{} when collecting the order. An e-mail will be sent to you when your food is ready.".format(order.id,total)
            subject = "Order Confirmation"
            emailFrom = settings.EMAIL_HOST_USER
            emailTo = [self.request.user.email]
            send_mail(subject, message, emailFrom, emailTo, fail_silently=False,)
            order.ordered = True
            order.save()
            context={'success':messages.success(self.request,'Order successfully placed! An email has been sent to you on your registered Email ID.')}
            return render(self.request,'index.html',context)
        except ObjectDoesNotExist:
            messages.warning(self.request,"You do not have an existing order")


class OrderList(SuperuserRequiredMixin,generic.ListView):
    #permission_required = ('user.is_superuser')
    template_name = 'products/allorders.html'
    model = Order

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['pendingorders'] = Order.objects.filter(ordered=True,being_delivered=False,received=False)
        context['preparedorders'] = Order.objects.filter(ordered=True,being_delivered=True,is_cancelled=False,received=False)
        return context

class OrderReady(SuperuserRequiredMixin,generic.View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user__username__iexact=self.kwargs.get("username"),id=self.kwargs.get("id"),ordered=True,being_delivered=False,is_cancelled=False,received=False)
        #             return queryset.filter(
        #     user__username__iexact=self.kwargs.get("username")
        # )  #### bug
            # username = order.user.username
            total = order.get_total()
            message = "Your order (Order ID-{}) is ready for you. Please pay ₹{} when collecting the order. Thank you for purchasing from CollegeDine.".format(order.id,total)
            subject = "Order Ready"
            emailFrom = settings.EMAIL_HOST_USER
            emailTo = [order.user.email]
            send_mail(subject, message, emailFrom, emailTo, fail_silently=False,)
            order.being_delivered = True
            order.save()
            return redirect('products:manage-orders')
            #return render(self.request,'products/allorders.html',{})
        except ObjectDoesNotExist:
            messages.warning(self.request,"This order does not exist.")


class OrderCancelled(SuperuserRequiredMixin,generic.View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user__username__iexact=self.kwargs.get("username"),id=self.kwargs.get("id"),ordered=True,being_delivered=False,is_cancelled=False,received=False)
            total = order.get_total()
            message = "Your order (Order ID-{}) could not be completed. We sincerely apologise for the inconvenience caused.".format(order.id)
            subject = "Order Cancelled"
            emailFrom = settings.EMAIL_HOST_USER
            emailTo = [order.user.email]
            send_mail(subject, message, emailFrom, emailTo, fail_silently=False,)
            order.being_delivered = True
            order.is_cancelled = True
            order.save()
            return redirect('products:manage-orders')
            #return render(self.request,'products/allorders.html',{})
        except ObjectDoesNotExist:
            messages.warning(self.request,"This order does not exist.")


class OrderCollected(SuperuserRequiredMixin,generic.View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user__username__iexact=self.kwargs.get("username"),id=self.kwargs.get("id"),ordered=True,being_delivered=True,is_cancelled=False,received=False)
            total = order.get_total()
            order.received = True
            order.save()
            return redirect('products:manage-orders')
            #return render(self.request,'products/allorders.html',{})
        except ObjectDoesNotExist:
            messages.warning(self.request,"This order does not exist.")


class OrderSummaryView(LoginRequiredMixin,generic.View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order ###CHECK AGAIN
            }
            return render(self.request,'products/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order. Head on over to our menu to select from a delicious variety of items!")
            return redirect("/") ##check url


#for all following functions check if slug can replace id
@login_required
def add_to_cart(request,slug):
    product = get_object_or_404(Product,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("products:summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("products:summary")
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("products:summary")


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("products:summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("products:all")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("products:all")


@login_required
def remove_single_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=product.slug).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("products:summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("products:all")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("products:all")


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0

#################################################################################################3########

# class CheckoutView(View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'order': order,
#             }
#             return render(self.request, "checkout.html", context)
#         except ObjectDoesNotExist:
#             messages.info(self.request, "You do not have an active order")
#             return redirect("core:checkout")
#
#     def post(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             return redirect("core:checkout")
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("core:order-summary")

# class OrderSummaryView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'object': order
#             }
#             return render(self.request, 'order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("/")

# @login_required
# def add_to_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_item, created = OrderItem.objects.get_or_create(
#         item=item,
#         user=request.user,
#         ordered=False
#     )
#     order_qs = Order.objects.filter(user=request.user, ordered=False)
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item.quantity += 1
#             order_item.save()
#             messages.info(request, "This item quantity was updated.")
#             return redirect("core:order-summary")
#         else:
#             order.items.add(order_item)
#             messages.info(request, "This item was added to your cart.")
#             return redirect("core:order-summary")
#     else:
#         ordered_date = timezone.now()
#         order = Order.objects.create(
#             user=request.user, ordered_date=ordered_date)
#         order.items.add(order_item)
#         messages.info(request, "This item was added to your cart.")
#         return redirect("core:order-summary")

# @login_required
# def remove_from_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_qs = Order.objects.filter(
#         user=request.user,
#         ordered=False
#     )
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False
#             )[0]
#             order.items.remove(order_item)
#             messages.info(request, "This item was removed from your cart.")
#             return redirect("core:order-summary")
#         else:
#             messages.info(request, "This item was not in your cart")
#             return redirect("core:product", slug=slug)
#     else:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:product", slug=slug)


# @login_required
# def remove_single_item_from_cart(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#     order_qs = Order.objects.filter(
#         user=request.user,
#         ordered=False
#     )
#     if order_qs.exists():
#         order = order_qs[0]
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False
#             )[0]
#             if order_item.quantity > 1:
#                 order_item.quantity -= 1
#                 order_item.save()
#             else:
#                 order.items.remove(order_item)
#             messages.info(request, "This item quantity was updated.")
#             return redirect("core:order-summary")
#         else:
#             messages.info(request, "This item was not in your cart")
#             return redirect("core:product", slug=slug)
#     else:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:product", slug=slug)
