from functools import wraps
import random
from datetime import datetime

from flask import session, redirect, request, render_template

from project4 import app, db
from project4.models import User, Category, Meal, Order
from project4.forms import LoginForm, RegistrationForm, OrderForm


month = {'1': 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}


def get_date(date):
    return '{} {}'.format(date.day, month.get(date.month))


def get_cart_info():
    cart = session.get("cart", [])
    cart_count = len(cart)
    cart_summ = session.get("cart_summ", 0)
    if not cart:
        return None
    else:
        return {'count': cart_count, 'summ': cart_summ, 'cart': cart}


# ------------------------------------------------------
# Декораторы авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin')
def admin_view():
    return render_template("page_admin.html")


# ------------------------------------------------------
# Страница аутентификации
@app.route("/login/", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect("/")

    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        if user and user.password_valid(form.password.data):
            session["user"] = {
                "id": user.id,
                "mail": user.mail
            }
            return redirect("/account")
        form.password.errors.append("Неверное имя или пароль")

    return render_template("login.html", form=form)


# -----------------------------------------------------
@app.route('/logout/', methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    return redirect("/login/")


# ------------------------------------------------------
# Страница добавления пользователя
@app.route("/register/", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()

    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(mail=form.mail.data).first()
        if user:
            form.mail.errors.append("Пользователь с таким именем уже существует")
            return render_template('register.html', form=form)

        user = User()
        user.mail = form.mail.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()

        session["user"] = {"id": user.id, "mail": user.mail}

        return redirect("/")

    return render_template('register.html', form=form)


@app.route("/")
def home_view():
    categories = db.session.query(Category).all()
    meals = {}
    for category in categories:
        meals_in_cat = db.session.query(Meal).filter(Meal.category_id == category.id)
        id_list = []
        for meal in meals_in_cat:
            id_list.append(meal.id)
        list_of_meals = set()
        while len(list_of_meals) < 3:
            item = random.choice(id_list)
            list_of_meals.add(db.session.query(Meal).get(item))
        meals[category.id] = list_of_meals
    cart_info = get_cart_info()
    is_logged = False if not session.get('user') else True
    return render_template('main.html', meals=meals, categories=categories, cart_info=cart_info, is_logged=is_logged)


@app.route("/cart/", methods=['GET', 'POST'])
def cart_view():

    count = {}
    meals = []
    mail = ''
    cart_info = get_cart_info()
    meals_on_cart = []

    if cart_info is not None:
        meals_on_cart = cart_info['cart']
        for id in meals_on_cart:
            add_meal = Meal.query.get(id)
            meals.append(add_meal)
            count[id] = meals_on_cart.count(id)
            order_summ = cart_info['summ']
    else:
        order_summ = 0

    if session.get('user'):
        mail = session["user"].get('mail')
        is_logged = True
    else:
        is_logged = False

    form = OrderForm(meals_on_cart=meals_on_cart, mail=mail, order_summ=order_summ)

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        phone = form.phone.data
        order_summ = form.order_summ.data
        status = 'Создан'
        new_order = Order(address=address, phone=phone, mail=mail, summ=order_summ, date=datetime.now().date(), status=status)
        db.session.add(new_order)
        for meal in meals_on_cart:
            new_meal = db.session.query(Meal).get(meal)
            new_order.meals.append(new_meal)

        db.session.commit()
        return redirect('/ordered/')

    if session.get('show_del_msg'):
        del_msg = session.pop('show_del_msg')
    else:
        del_msg = False

    return render_template('cart.html',
                           cart_info=cart_info,
                           is_logged=is_logged,
                           count=count, meals_on_cart=meals,
                           del_msg=del_msg, form=form)


@app.route("/account/")
@login_required
def account_view():
    cart_info = get_cart_info()
    orders = db.session.query(Order).filter(Order.mail == session["user"].get('mail'))
    meals = db.session.query(Meal).all()

    return render_template('account.html', orders=orders, cart_info=cart_info, meals=meals, month=month)


@app.route("/addtocart/<int:item>")
def add_to_cart(item):
    cart = session.get("cart", [])
    if item not in cart:
        new_item = Meal.query.get_or_404(item)
        cart.append(new_item.id)
        session['cart'] = cart
        cart_summ = session.get("cart_summ", 0)
        cart_summ += new_item.price
        session['cart_summ'] = cart_summ
    return redirect('/cart/')


@app.route("/delete/<int:item>")
def delete_from_cart(item):
    target_item = Meal.query.get_or_404(item)
    cart = session.get("cart", [])
    cart.remove(target_item.id)
    session['cart'] = cart
    cart_summ = session.get("cart_summ", 0)
    cart_summ -= target_item.price
    session['cart_summ'] = cart_summ
    session['show_del_msg'] = True
    return redirect('/cart/')


@app.route("/ordered/")
def ordered_view():
    session.pop('cart')
    session.pop('cart_summ')
    return render_template('ordered.html')
