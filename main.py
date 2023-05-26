from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_fruits.db'

# Clé secrète utilisée pour la session
app.config['SECRET_KEY'] = 'Je suis une clé secrète de la guerre qui tue 69'

# Initialisation de l'extension SQLAlchemy avec l'application Flask
db = SQLAlchemy(app)

# Définition du modèle Fruit
class Fruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Définition du modèle User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def home():
    # Récupère tous les fruits de la base de données
    fruits = Fruit.query.all()
    # Rend le template 'home.html' en passant les fruits récupérés en tant que variable 'fruits'
    # Si aucun fruit n'est trouvé, passe 'None' à la place
    return render_template('home.html', fruits=fruits if fruits else None)

@app.route('/fruits', methods=['GET'])
def get_fruits():
    # Récupère tous les fruits de la base de données
    fruits = Fruit.query.all()
    # Convertit les fruits en une liste de dictionnaires JSON contenant les attributs id, name et price
    fruits_json = [{'id': fruit.id, 'name': fruit.name, 'price': fruit.price} for fruit in fruits]
    # Retourne les fruits sous forme de réponse JSON
    return jsonify(fruits_json)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            if username == "admin":
                # Si l'utilisateur est un administrateur, le connecte en définissant les variables de session appropriées
                session['logged_in'] = True
                session['username'] = username
                flash('Connecté avec succès.', 'alert-success')
                return redirect(url_for('profile'))
            else:
                # Si l'utilisateur n'est pas un administrateur, affiche un message d'erreur et redirige vers la page de connexion
                flash('Vous devez être un administrateur pour accéder à cette page.', 'alert-danger')
                return redirect(url_for('login'))
        else:
            # Si les identifiants sont invalides, affiche un message d'erreur et redirige vers la page de connexion
            flash('Identifiants invalides.', 'alert-danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Déconnecte l'utilisateur en définissant la variable de session 'logged_in' à False
    session['logged_in'] = False
    flash('Vous avez été déconnecté.', 'alert-info')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET'])
def profile():
    # Vérifie si l'utilisateur est connecté en tant qu'administrateur
    if not session.get('logged_in'):
        flash('Vous devez être un administrateur pour accéder à cette page.', 'alert-danger')
        return redirect(url_for('login'))
    # Vérifie si l'utilisateur est connecté
    if 'username' not in session:
        return redirect(url_for('login'))
    # Récupère tous les fruits de la base de données
    fruits = Fruit.query.all()
    # Rend le template 'profile.html' en passant les fruits récupérés en tant que variable 'fruits'
    # Si aucun fruit n'est trouvé, passe 'None' à la place
    return render_template('profile.html', fruits=fruits if fruits else None)

@app.route('/profile/add', methods=['POST'])
def add_fruit():
    fruit_name = request.form.get('fruit_name')
    fruit_price = request.form.get('fruit_price')
    new_fruit = Fruit(name=fruit_name, price=fruit_price)
    # Ajoute le nouveau fruit à la base de données
    db.session.add(new_fruit)
    db.session.commit()
    flash('Fruit ajouté avec succès.', 'alert-success')
    return redirect(url_for('profile'))

@app.route('/profile/update', methods=['POST'])
def update_fruit():
    fruit_id = request.form.get('fruit_id')
    new_price = request.form.get('new_price')
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        fruit.price = new_price
        # Met à jour le prix du fruit dans la base de données
        db.session.commit()
        flash('Fruit mis à jour avec succès.', 'alert-success')
    return redirect(url_for('profile'))

@app.route('/profile/delete', methods=['POST'])
def delete_fruit():
    fruit_id = request.form.get('fruit_id')
    fruit = Fruit.query.get(fruit_id)
    if fruit:
        # Supprime le fruit de la base de données
        db.session.delete(fruit)
        db.session.commit()
        flash('Fruit supprimé avec succès.', 'alert-success')
    return redirect(url_for('profile'))

@app.cli.command("initdb")
def initdb_command():
    # Crée toutes les tables de la base de données
    db.create_all()
    # Ajoute un utilisateur administrateur par défaut à la base de données
    user = User(username='admin', password='root')
    db.session.add(user)
    db.session.commit()
    print("Base de données initialisée.")

if __name__ == "__main__":
    app.run(debug=True)
