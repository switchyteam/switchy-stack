from flask import Flask, request, flash, url_for, redirect, render_template, make_response
from view import view
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')
app.register_blueprint(view, url_prefix="/")

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column('pet_id', db.Integer, primary_key=True)
    name = db.Column(db.String())
    animal = db.Column(db.String())
    breed = db.Column(db.String())


def __init__(self, name, animal, breed):
    self.name = name
    self.animal = animal
    self.breed = breed


@app.route('/')
def show_all():
    db.create_all()
    return render_template('show_all.html', pets=Pet.query.all())


@app.route('/new', methods=['GET', 'POST'])
def new():
    db.create_all()
    if request.method == 'POST':
        if not request.form['name'] or not request.form['animal'] or not request.form['breed']:
            flash('Please enter all the fields', 'error')
        else:
            pet = Pet(name=request.form['name'], animal=request.form['animal'],
                      breed=request.form['breed'])

            db.session.add(pet)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/test_db')
def test_db():
    db.create_all()
    # db.session.commit()
    pet = Pet.query.first()
    if not pet:
        u = Pet(name='Charlie', animal='Dog', breed='Lab')
        db.session.add(u)
        db.session.commit()
    pet = Pet.query.first()
    return "Pet '{} {} {}' is in database".format(pet.name, pet.animal, pet.breed)


# For debugging only
if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)