from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.file import FileField, FileAllowed
from Forms import CreateProductForm
from werkzeug.utils import secure_filename
import shelve, Product, os

app = Flask(__name__)



class Order:
    _order_counter = 1  # Class-level counter for unique IDs

    def __init__(self, product_name, total_price):
        self.__order_id = Order._order_counter  # Assign current counter value as ID
        Order._order_counter += 1  # Increment the counter for the next order
        self.__product_name = product_name
        self.__total_price = total_price

    def get_order_id(self):
        return self.__order_id

    def get_product_name(self):
        return self.__product_name

    def get_total_price(self):
        return self.__total_price



@app.route('/')
def home():
    if not os.path.exists('product.db'):
        # product_dict = {}
        # db = shelve.open('product.db', 'c')
        # product_dict = db['Products']
        # db.close()
        #
        # product_list = []
        # for key in product_dict:
        #     product = product_dict.get(key)
        #     product_list.append(product)
        # with shelve.open('product.db', 'c') as db:
        #     db['Products'] = {}  # Initialize an empty 'Products' dictionary

        # Open the existing database and safely check if 'Products' exists
        with shelve.open('product.db', 'c') as db:
            product_dict = db.get('Products', {})  # Default to empty dict if 'Products' doesn't exist

        product_list = list(product_dict.values())

        return render_template('retrieveProducts.html', count=len(product_list), product_list=product_list)


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/createProduct', methods=['GET', 'POST'])
def create_product():
    create_product_form = CreateProductForm(request.form)  # call the form to create a new product
    if request.method == 'POST' and create_product_form.validate():  # if the form is valid
        product_dict = {}
        db = shelve.open('product.db', 'w')

        try:
            product_dict = db['Products']
        except:
            print('Error in retrieving products from product.db')

        product_dict = db.get('Products', {})
        last_product_id = db.get('last_product_id', 0)

        image_filename = None
        if 'image' in request.files:  # Check if an image file is uploaded
            file = request.files['image']
            if file and file.filename:  # If a file is provided
                image_filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                try:
                    file.save(image_path)  # Save the image to the uploads folder
                except Exception as e:
                    print(f"Error saving file {image_filename}: {e}")

        product = Product.Product(create_product_form.product_name.data,
                                  create_product_form.description.data,
                                  create_product_form.price.data,
                                  create_product_form.category.data,
                                  create_product_form.remarks.data,
                                  image_filename=image_filename
                                  )
        product_dict[product.get_product_id()] = product  # add the product to product_dict
        db['Products'] = product_dict

        db['last_product_id'] = last_product_id + 1
        db.close()

        return redirect(url_for('home'))
    return render_template('createProduct.html', form=create_product_form)


@app.route('/retrieveProducts')
def retrieve_products():
    product_dict = {}
    db = shelve.open('product.db', 'r')
    product_dict = db['Products']
    db.close()

    product_list = []
    for key in product_dict:
        product = product_dict.get(key)
        product_list.append(product)

    return render_template('retrieveProducts.html', count=len(product_list), product_list=product_list)


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    update_product_form = CreateProductForm(request.form)
    if request.method == 'POST' and update_product_form.validate():
        product_dict = {}
        db = shelve.open('product.db', 'w')
        product_dict = db['Products']

        product = product_dict.get(id)
        product.set_name(update_product_form.product_name.data)
        product.set_description(update_product_form.description.data)
        product.set_price(update_product_form.price.data)
        product.set_category(update_product_form.category.data)
        product.set_remarks(update_product_form.remarks.data)

        db['Products'] = product_dict
        db.close()

        return redirect(url_for('retrieve_products'))
    else:
        product_dict = {}
        db = shelve.open('product.db', 'r')
        product_dict = db['Products']
        db.close()

        product = product_dict.get(id)
        update_product_form.product_name.data = product.get_product_name()
        update_product_form.description.data = product.get_description()
        update_product_form.price.data = product.get_price()
        update_product_form.category.data = product.get_category()
        update_product_form.remarks.data = product.get_remarks()

        return render_template('updateProduct.html', form=update_product_form)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    product_dict = {}
    db = shelve.open('product.db', 'w')
    product_dict = db['Products']

    product_dict.pop(id)

    db['Products'] = product_dict
    db.close()

    return redirect(url_for('retrieve_products'))


@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    with shelve.open('product.db', 'c') as db:
        product_dict = db.get('Products', {})
        cart_list = db.get('Cart', [])

        if id not in cart_list:
            cart_list.append(id)

    # product = product_dict.get(id)
    # if product not in cart_list:
    #     cart_list.append(product)

    # cart_item={}
    # cart_item[id] = product
    # cart_list.append(
    #     cart_item
    # )

        db['Cart'] = cart_list  # save this to the cart
    print('cart content: ', cart_list)

    return redirect(url_for('view_cart'))


@app.route('/view_cart')
def view_cart():
    with shelve.open('product.db', 'r') as db:
        # db = shelve.open('product.db', 'r')
        cart_list = db.get('Cart', [])  # retrieve from the cart
        product_dict = db.get('Products', {})

    cart_items = []
    total_price = 0
    for product_id in cart_list:
        if product_id in product_dict:
            product = product_dict[product_id]
            cart_items.append(product_dict[product_id])
            total_price += product.get_price()

    print(product_dict)

    return render_template('view_cart.html', cart_list=cart_items, total_price=total_price)


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    with shelve.open('product.db', 'r') as db:
        cart_list = db.get('Cart', [])  # Global cart
        product_dict = db.get('Products', {})

    for cart_item in cart_list:
        print(f"cart_item ={cart_item}")
    #     prod = cart_item.get(product_id,"none")
        if product_id == cart_item:
            cart_list.remove(cart_item)

    with shelve.open('product.db', 'w') as db:
        db['Cart'] = cart_list

    return redirect(url_for('view_cart'))


# @app.route('/clear_cart', methods=['POST'])
# def clear_cart():
#     db = shelve.open('product.db', 'c')
#     db['Cart'] = []  # Clear the cart
#     db.close()
#
#     return redirect(url_for('view_cart'))
#
#
# @app.route('/checkout', methods=['POST'])
# def checkout():
#     db = shelve.open('product.db', 'c')
#     db['Cart'] = []  # Empty the cart after checkout
#     db.close()
#
#     return redirect(url_for('retrieve_products'))


if __name__ == '__main__':
    app.run(debug=True)