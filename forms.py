from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    username = StringField('Nom utilisateur', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Connexion')

class StoreForm(FlaskForm):
    name = StringField('Nom boutique', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    whatsapp = StringField('Numéro WhatsApp', validators=[Optional(), Length(min=10, max=20)])
    image = FileField('Image boutique', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement !')])
    submit = SubmitField('Ajouter boutique')

class ProductForm(FlaskForm):
    name = StringField('Nom article', validators=[DataRequired(), Length(min=2, max=100)])
    price = FloatField('Prix FCFA', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Image article', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement !')])
    submit = SubmitField('Sauvegarder article')

class OfferForm(FlaskForm):
    title = StringField('Titre offre', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    discount = FloatField('Réduction %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    store_id = IntegerField('ID Boutique', validators=[DataRequired(), NumberRange(min=1)])
    image = FileField('Image offre', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement!')])
    submit = SubmitField('Ajouter offre')

class NewsForm(FlaskForm):
    title = StringField('Titre actualité', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Contenu', validators=[DataRequired(), Length(min=10)])
    image1 = FileField('Image 1 (optionnel)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement!')])
    image2 = FileField('Image 2 (optionnel)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement!')])
    image3 = FileField('Image 3 (optionnel)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images seulement!')])
    submit = SubmitField('Publier actualité')

class JobForm(FlaskForm):
    title = StringField('Titre poste', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    location = StringField('Localisation', validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Type contrat', choices=[('CDI', 'CDI'), ('CDD', 'CDD'), ('Stage', 'Stage'), ('Freelance', 'Freelance')], validators=[DataRequired()])
    salary = StringField('Salaire', validators=[DataRequired()])
    whatsapp = StringField('WhatsApp contact', validators=[Optional()])
    image = FileField('Image (optionnel)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Publier offre')
