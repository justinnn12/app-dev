from wtforms import Form, StringField, TextAreaField, DecimalField, validators, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed


class CreateProductForm(Form):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    price = DecimalField('Price ($)', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Electronics', 'Electronics'),
                                                 ('Clothing', 'Clothing'),
                                                 ('Home', 'Home'),
                                                 ('Other', 'Other')], validators=[DataRequired()])
    remarks = TextAreaField('Remarks', [validators.Optional()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png'], 'Images only')])
    submit = SubmitField('Create Product')
