from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from . models import Category, Product, Purchase, Stock, Supplier, Permission, Role, UserProfile, SystemSettings
from . forms import CategoryForm, ProductForm, PurchaseForm, PurchaseItem, SupplierForm, PermissionForm, RoleForm, SystemSettingsForm
from collections import defaultdict
from .decorators import get_role_permissions
from django.contrib import messages
from django.contrib.auth.models import User
from .decorators import admin_required, staff_or_admin_required, get_role_permissions, role_permission_required



# --------------------------------  Category Create  -----------------------------------------------------------------

@login_required(login_url='/login/')
@role_permission_required('category_create')
def create_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category/category_form.html', {'form':form})


# --------------------------------  Category List  --------------------------

@login_required(login_url='/login/')
def category_list(request):
    # get role permissions
    role, permission, permissions_list = get_role_permissions(request.user)

    # superuser হলে সব permission auto add
    if request.user.is_superuser:
        permissions_list = [
            'category_create',
            'category_update',
            'category_delete',
        ]

    categories = Category.objects.all().order_by('-id')
    context = {
        'categories': categories,
        'permissions_list': permissions_list,
    }
    return render(request, 'category/category_list.html', context)


# --------------------------------  Category Update  --------------------------

@login_required(login_url='/login/')
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'category/category_form.html', {'form': form,'is_update': True })


# ---------------------- Category  Delete   -------------------

@login_required(login_url='/login/')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')


# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Product     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='/login/')
def product_list(request):
    products = Product.objects.all().order_by('id')
    role, permissions, permissions_list = get_role_permissions(request.user)

    context = {
        'products': products,
        'role': role,
        'permissions': permissions,
        'permissions_list': permissions_list,
    }
    return render(request, 'product/product_list.html', context)

# ---------------------- Product  Create   ------------------------------



@login_required(login_url='/login/')
@role_permission_required('product_create')
def create_product(request):
    products = Product.objects.all().order_by('id')
    role, permissions, permissions_list = get_role_permissions(request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully!")
            return redirect('product_list')
    else:
        form = ProductForm()
    context = {
        'form': form,
        'products': products,
        'role': role,
        'permissions': permissions,
        'permissions_list': permissions_list,   # ✅ add this
    }
    return render(request, 'product/product_form.html', context)



# ----------------------  Product Update   ------------------------------

@login_required(login_url='/login/')
@role_permission_required('product_update')
def product_update(request, pk):
    products = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=products)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'product/product_form.html', {'form':form, 'is_update':True})


# ---------------------- Product Delete  ------------------------------

@login_required(login_url='/login/')
@role_permission_required('product_delete')
def product_delete(request, pk):
    prodcuts = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        prodcuts.delete()
        return redirect('product_list')
    
    

# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Supplier     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url='/login/')
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-id')
    role, permissions, permissions_list = get_role_permissions(request.user)
    return render(request, 'supplier/supplier_list.html', {'suppliers':suppliers, 'permissions':permissions, 'permissions_list':permissions_list})


# ---------------------- Supplier Create ------------------------------

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def supplier_update(request, pk):
    suppliers = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=suppliers)
    if form.is_valid():
        form.save()
        return redirect('supplier_list')
    return render(request, 'supplier/supplier_form.html', {'form':form, 'is_update': True})



# ---------------------- Supplier Delete   ------------------------------

@login_required(login_url='/login/')
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')



# ---------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------     Purchase     ---------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

# ---------------------- Purchase  Create   ------------------------------


@login_required(login_url='/login/')
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
                item = PurchaseItem.objects.create(
                    purchase=purchase, 
                    product_id=prod_id, 
                    quantity=total_qty, 
                    purchase_price=price
                )
                if purchase.status == 'Received':
                    stock, _ = Stock.objects.get_or_create(
                        product_id=prod_id,
                        defaults={'quantity': 0}
                    )
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

@login_required(login_url='/login/')
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    old_status = purchase.status

    products = Product.objects.all().order_by('id')
    items = [
        {
            'product_id': item.product.id,
            'quantity': item.quantity,
            'purchase_price': item.purchase_price,
        }
        for item in purchase.items.all()
    ]

    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            updated_purchase = form.save(commit=False)
            updated_purchase.created_by = request.user
            updated_purchase.save()

            new_status = updated_purchase.status

            if old_status == 'Received':
                for item in purchase.items.all():
                    stock = Stock.objects.filter(product=item.product).first()
                    if stock:
                        stock.quantity = max(0, stock.quantity - item.quantity)
                        stock.save()

            purchase.items.all().delete()

            product_ids = request.POST.getlist('product')
            quantities = request.POST.getlist('quantity')
            prices = request.POST.getlist('purchase_price')

            for prod_id, qty, price in zip(product_ids, quantities, prices):
                if prod_id and int(qty) > 0:
                    item = PurchaseItem.objects.create(
                        purchase=purchase,
                        product_id=int(prod_id),
                        quantity=int(qty),
                        purchase_price=float(price)
                    )

                    if new_status == 'Received':
                        stock, _ = Stock.objects.get_or_create(
                            product=item.product,
                            defaults={'quantity': 0}
                        )
                        stock.quantity += item.quantity
                        stock.save()

            return redirect('purchase_list')

    else:
        form = PurchaseForm(instance=purchase)

    return render(request, 'purchase/purchase_form.html', {
        'form': form,
        'products': products,
        'purchase': purchase,
        'items': items,
        'is_update': True
    })

# ----------------------------------------  Purchase  List  -------------------------------------------

@login_required(login_url='/login/')
def purchase_list(request):
    purchases = Purchase.objects.prefetch_related('items__product').order_by('-id')
    role, permissions, permissions_list = get_role_permissions(request.user)
    grand_total = 0
    for p in purchases:
        try:
            grand_total += p.total  
        except Exception as e:
            print(f"Error calculating total for Purchase {p.id}: {e}")
            continue
    return render(request, 'purchase/purchase_list.html', {
        'purchases': purchases,
        'grand_total': grand_total, 'permissions':permissions, 'permissions_list':permissions_list
    })

# ----------------------------------------  Purchase  Details  -------------------------------------------

@login_required(login_url='/login/')
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, 'purchase/purchase_details.html', {'purchase': purchase})


# ----------------------------------------  Purchase    ------------------------------------------- 

@login_required(login_url='/login/')
def purchase_delete(request, pk):
    purchases = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        for item in purchases.items.all():
            stock, created= Stock.objects.get_or_create(product=item.product)
            stock.quantity -= item.quantity
            if stock.quantity < 0:
                stock.quantity = 0
            stock.save()
        purchases.delete()
        return redirect('purchase_list')


# ----------------------------------------------------------------------------------- 
# ----------------------------------------  Purmission  List  ------------------------------------------- 
# --------------------------------------------------------------------------------- 

@login_required(login_url='/login/')
def permission_list(request):
    permissions = Permission.objects.all().order_by('-id')
    return render(request, 'permission/permission_list.html', {'permissions':permissions})


@login_required(login_url='/login/')
def permission_create(request):
    form = PermissionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('permission_list')
    return render(request, 'permission/permission_form.html', {'form':form})


# ----------------------------------------------------------------------------------- 
# ----------------------------------------  Role  List  ------------------------------------------- 
# --------------------------------------------------------------------------------- 

@login_required(login_url='/login/')
def role_list(request):
    roles = Role.objects.all().order_by('-id')
    role, permissions, permissions_list = get_role_permissions(request.user)
    return render(request, 'role/role_list.html', {'roles':roles, 'permissions_list':permissions_list, 'permissions':permissions})


@login_required(login_url='/login/')
@role_permission_required('role_create')   
def role_create(request):
    form = RoleForm(request.POST or None)
    if form.is_valid():
        role = form.save(commit=False)  
        role.save()                     
        form.save_m2m()                 
        messages.success(request, "Role created successfully!")
        return redirect('role_list')
    return render(request, 'role/role_form.html', {'form': form})


@login_required(login_url='/login/')
@role_permission_required('role_update')
def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        messages.success(request, "Role updated successfully!")
        return redirect('role_list')
    return render(request, 'role/role_form.html', {'form': form, 'role': role})


@login_required(login_url='/login/')
@role_permission_required('role_delete')
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, "Role deleted successfully!")
        return redirect('role_list')


#----------------------------------   User  --------------------------------------
@login_required(login_url='/login/')

def user_list(request):
    role, permissions, permission_list = get_role_permissions(request.user)
    users = User.objects.all().order_by('-id')
    return render(request, 'user/user_list.html', {'users': users, 'permissions_list': permission_list, 'permissions':permissions, 'role':role})

login_required(login_url='/login/')
@role_permission_required('user_create')
def add_user(request):
    roles = Role.objects.all()
    superuser_role = Role.objects.filter(name='superuser').first()
    superuser_exists = False
    if superuser_role:
        superuser_exists = UserProfile.objects.filter(role=superuser_role).exists()
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        role_id = request.POST.get('role')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already registered.")
            return redirect('add_user')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('add_user')
        if (
            superuser_role and
            role_id and
            int(role_id) == superuser_role.id and
            superuser_exists):
            messages.error(request, "Superuser already exists. Cannot create another one.")
            return redirect('add_user')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password)
        role = Role.objects.get(id=role_id) if role_id else None
        UserProfile.objects.create(user=user, role=role)
        messages.success(request, "User created successfully!")
        return redirect('user_list')
    return render(request,'user/add_user.html',{'roles': roles,'superuser_exists': superuser_exists})


@login_required(login_url='/login/')
def edit_user(request, id):
    target_user = User.objects.get(id=id)
    superuser_role = Role.objects.filter(name='SuperUser').first()
    superuser_exists = False
    if superuser_role:
        superuser_exists = UserProfile.objects.filter(role=superuser_role).exclude(user=target_user).exists()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST.get('password')
        role_id = request.POST.get('role')
        target_user.username = username
        target_user.email = email
        if password:
            target_user.set_password(password)
        target_user.save()
        if role_id:
            selected_role = Role.objects.get(id=role_id)
            if selected_role.name == 'SuperUser' and superuser_exists:
                messages.error(request, "Superuser role is already assigned. Cannot assign again.")
                return redirect('edit_user', user_id=id)

            profile, created = UserProfile.objects.get_or_create(user=target_user)
            profile.role = selected_role
            profile.save()


        messages.success(request, "User updated successfully!")
        return redirect('user_list')
    roles = Role.objects.all()
    if superuser_role and superuser_exists:
        roles = roles.exclude(id=superuser_role.id)
    return render(request, 'user/add_user.html', {'roles': roles,'target_user': target_user,'superuser_exists': superuser_exists})


@login_required(login_url='/login/')
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    


# ---------------   system settings -----------------
@login_required(login_url='/login/')
def system_list(request):
    settings_instance = SystemSettings.objects.first()
    return render(request, 'system/system_list.html', {'settings': settings_instance})

# Create new system settings
@login_required(login_url='/login/')
def company_create(request):
    if SystemSettings.objects.exists():
        return redirect('system_list')
    if request.method == "POST":
        form = SystemSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('delete_logo') and instance.logo:
                instance.logo.delete(save=False)
                instance.logo = None
            instance.save()
            return redirect('system_list')
    else:
        form = SystemSettingsForm()
    print(form.instance.logo)   
    print(form.errors)    
    return render(request, 'system/system.html', {'form': form, 'title': 'Create System Settings'})
      


# Update existing system settings
@login_required(login_url='/login/')
@role_permission_required('system_update')
def system_update(request, pk):
    settings_instance = get_object_or_404(SystemSettings, pk=pk)
    if request.method == "POST":
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_instance)
        if form.is_valid():
            instance = form.save(commit=False)
            if request.POST.get('delete_logo') and instance.logo:
                instance.logo.delete(save=False)
                instance.logo = None
            instance.save()
            return redirect('system_list')
    else:
        form = SystemSettingsForm(instance=settings_instance)
    print(form.instance.logo)   
    print(form.errors) 
    return render(request, 'system/system.html', {'form': form, 'title': 'Update System Settings'})



# -------------------------------------------------  low stock  ----------------------------------
def low_stock_list(request):
    products = Product.objects.filter(stock__quantity__lt=8).order_by('id')
    role, permissions, permissions_list = get_role_permissions(request.user)
    context = {'products': products, 'role': role, 'permissions': permissions, 'permissions_list': permissions_list}
    return render(request, 'low_stock/stock_list.html', context)

