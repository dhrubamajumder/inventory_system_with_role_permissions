from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from . models import Category, Product, Purchase, Stock, Supplier
from . forms import CategoryForm, ProductForm, PurchaseForm, PurchaseItem, SupplierForm
from collections import defaultdict



# --------------------------------  Category Create  -----------------------------------------------------------------
@login_required
def create_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category/category_form.html', {'form':form})


# --------------------------------  Category List  --------------------------
@login_required
def category_list(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, 'category/category_list.html', {'categories':categories})


# --------------------------------  Category Update  --------------------------
@login_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category/category_form.html', {'form': form,'is_update': True })


# ---------------------- Category  Delete   -------------------
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')


# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Product     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

@login_required
def product_list(request):
    products = Product.objects.select_related('stock').order_by('-id')
    return render(request, 'product/product_list.html', {'products': products})
    
# ---------------------- Product  Create   ------------------------------

@login_required
def create_product(request):
    products = Product.objects.all().order_by('id')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  
    else:
        form = ProductForm()
    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'product/product_form.html', context)


# ----------------------  Product Update   ------------------------------
@login_required
def product_update(request, pk):
    products = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=products)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'product/product_form.html', {'form':form, 'is_update':True})


# ---------------------- Product Delete  ------------------------------
@login_required
def product_delete(request, pk):
    prodcuts = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        prodcuts.delete()
        return redirect('product_list')
    
    

# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Supplier     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-id')
    return render(request, 'supplier/supplier_list.html', {'suppliers':suppliers})


# ---------------------- Supplier Create ------------------------------
@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm() 
    return render(request, 'supplier/supplier_form.html', {'form': form})


# ---------------------- Supplier  Update   ------------------------------
@login_required
def supplier_update(request, pk):
    suppliers = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=suppliers)
    if form.is_valid():
        form.save()
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_form.html', {'form':form, 'is_update': True})



# ---------------------- Supplier Delete   ------------------------------
@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')



# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Purchase     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

# ---------------------- Purchase  Create   ------------------------------
@login_required
def create_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            products = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity')
            prices = request.POST.getlist('purchase_price')
            product_qty_map = defaultdict(int)
            for prod_id, qty in zip(products, quantities):
                if prod_id and qty:
                    product_qty_map[int(prod_id)] += int(qty)
            for prod_id, total_qty in product_qty_map.items():
                price = float(prices[products.index(str(prod_id))])
                item = PurchaseItem.objects.create(purchase=purchase, product_id=prod_id, quantity=total_qty, purchase_price=price)
                stock, _ = Stock.objects.get_or_create(product_id=prod_id, defaults={'quantity': 0})
                stock.quantity += total_qty
                stock.save()
            return redirect('purchase_detail', pk=purchase.id)
    else:
        form = PurchaseForm()
    products = Product.objects.all()
    return render(request, 'purchase/purchase_form.html', {
        'form': form,
        'products': products
    })

# ----------------------------------------  Purchase Update  -------------------------------------------
@login_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    products = Product.objects.all().order_by('id')
    items = [
        {'product_id': item.product.id, 'quantity': item.quantity, 'purchase_price': item.purchase_price,}
        for item in purchase.items.all()]
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            updated_purchase = form.save(commit=False)
            updated_purchase.created_by = request.user
            date_str = request.POST.get('purchase_date')
            if date_str:
                updated_purchase.purchase_date = date_str
            updated_purchase.save()
            for item in purchase.items.all():
                stock, _ = Stock.objects.get_or_create(product=item.product)
                stock.quantity -= item.quantity
                if stock.quantity < 0:
                    stock.quantity = 0
                stock.save()
            purchase.items.all().delete()
            product_ids = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity')
            prices = request.POST.getlist('purchase_price')
            for prod_id, qty, price in zip(product_ids, quantities, prices):
                if prod_id:
                    prod_id = int(prod_id)
                    qty = int(qty)
                    price = float(price)
                    item = PurchaseItem.objects.create(purchase=purchase, product_id=prod_id, quantity=qty, purchase_price=price)
                    stock, _ = Stock.objects.get_or_create(product=item.product, defaults={'quantity': 0})
                    stock.quantity += qty
                    stock.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, 'purchase/purchase_form.html', {'form': form,'products': products,'purchase': purchase,'items': items, 'is_update': True})


# ----------------------------------------  Purchase  List  -------------------------------------------
@login_required
def purchase_list(request):
    purchases = Purchase.objects.prefetch_related('items__product').order_by('-id')
    grand_total = 0
    for p in purchases:
        try:
            grand_total += p.total  
        except Exception as e:
            print(f"Error calculating total for Purchase {p.id}: {e}")
            continue
    return render(request, 'purchase/purchase_list.html', {
        'purchases': purchases,
        'grand_total': grand_total
    })

# ----------------------------------------  Purchase  Details  -------------------------------------------
@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, 'purchase/purchase_details.html', {'purchase': purchase})




