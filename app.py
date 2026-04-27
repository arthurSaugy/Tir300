import os
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
)
from werkzeug.utils import secure_filename
from forms import ResultatForm, DummyForm, RdvForm
from models import db, Resultat, AgendaEntry, EventFlyer, GaleriePhoto
from datetime import datetime, timedelta
import storage

# Charge les variables d'environnement depuis .env (en local).
# En production sur Render, les variables sont fournies par la plateforme.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import locale
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')


# Fonction qui supprime les RDV qui ont plus d'un an
def supprimer_anciens_rdv():
    seuil = datetime.now().date() - timedelta(days=365)
    anciens = AgendaEntry.query.filter(AgendaEntry.date < seuil).all()
    for rdv in anciens:
        db.session.delete(rdv)
    db.session.commit()


def get_database_uri():
    """
    Retourne l'URI de la base de donnees a utiliser.

    - En production (Render) : la variable DATABASE_URL est injectee
      automatiquement par la base PostgreSQL attachee au service.
      Render utilise historiquement le prefixe 'postgres://' que
      SQLAlchemy 2.x ne reconnait plus : on le normalise en
      'postgresql://'.
    - En developpement local : si DATABASE_URL n'est pas definie, on
      retombe sur la base SQLite locale (instance/mydatabase.db) pour
      eviter d'avoir a installer PostgreSQL sur la machine de dev.
    """
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return 'sqlite:///mydatabase.db'
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return db_url


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'une-cle-secrete-tres-secrete')
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    supprimer_anciens_rdv()


# Expose storage.public_url comme fonction Jinja `r2_url` dans tous les templates.
@app.context_processor
def _inject_r2_url():
    return {'r2_url': storage.public_url}

# ================== MDP ========================
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Décorateur pour protéger les routes admin
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Connexion requise", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ================== ROUTES USER ======================

@app.route('/')
def home():
    coords = (46.73628887245213, 6.862805375176529)
    return render_template('home.html', lat=coords[0], lng=coords[1])

@app.route('/agenda')
def agenda():
    supprimer_anciens_rdv()
    agenda_entries = AgendaEntry.query.order_by(AgendaEntry.date).all()
    return render_template('agenda.html', agenda_entries=agenda_entries)

@app.route('/evenements')
def evenements():
    # Cherche les flyers existants pour chaque position
    flyer1 = EventFlyer.query.filter_by(position='box1').first()
    flyer2 = EventFlyer.query.filter_by(position='box2').first()
    return render_template('event.html', flyer1=flyer1, flyer2=flyer2)

@app.route('/resultats')
def resultats():
    resultats = Resultat.query.order_by(Resultat.date.desc()).all()
    return render_template('resultats.html', resultats=resultats)

@app.route('/galerie')
def galerie():
    photos = GaleriePhoto.query.order_by(GaleriePhoto.id).all()
    return render_template('galerie.html', photos=photos)

# ================== ROUTES ADMIN ======================

# Page login admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    now = datetime.now()

    session.setdefault('login_attempts', 0)
    session.setdefault('lock_until', None)

    if session['lock_until']:
        lock_time = datetime.fromisoformat(session['lock_until'])
        if now < lock_time:
            remaining = int((lock_time - now).total_seconds())
            flash(f"Trop de tentatives. Réessaie dans <span id='timer'>{remaining}</span> secondes.", "danger")
            return render_template('admin_login.html')
        else:
            # Déblocage : période de blocage terminée, on supprime la clé
            session.pop('lock_until', None)
            session['login_attempts'] = 0  # on reset aussi les tentatives

    if request.method == 'POST':
        password = request.form.get('password', '')

        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.pop('login_attempts', None)
            session.pop('lock_until', None)
            return redirect(url_for('admin_resultats'))
        else:
            session['login_attempts'] += 1
            if session['login_attempts'] >= 5:
                lock_until = now + timedelta(seconds=15)
                session['lock_until'] = lock_until.isoformat()
                flash("Trop de tentatives. Réessaie dans <span id='timer'>15</span> secondes.", "danger")
            else:
                flash("Mot de passe incorrect.", "danger")

    return render_template('admin_login.html')

# Déconnexion admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

# ============ Evenement Admin

def _replace_flyer(position: str, file_field: str, current_flyer):
    """
    Helper interne : remplace (ou cree) un flyer pour la position donnee
    via le fichier soumis dans le champ `file_field`. Stocke dans R2 sous
    la cle 'event_images/<filename>'.
    """
    if file_field not in request.files:
        return current_flyer
    f = request.files[file_field]
    if not f or f.filename == '':
        return current_flyer

    filename = secure_filename(f.filename)
    new_key = f'event_images/{filename}'

    # Supprime l'ancien flyer dans R2 si different.
    if current_flyer and current_flyer.filename and current_flyer.filename != filename:
        storage.delete_object(f'event_images/{current_flyer.filename}')

    # Uploade le nouveau flyer.
    storage.upload_fileobj(f.stream, new_key, content_type=f.mimetype)

    if current_flyer:
        current_flyer.filename = filename
    else:
        current_flyer = EventFlyer(position=position, filename=filename)
        db.session.add(current_flyer)
    return current_flyer


@app.route('/admin_events', methods=['GET', 'POST'])
@admin_required
def admin_events():
    flyer1 = EventFlyer.query.filter_by(position='box1').first()
    flyer2 = EventFlyer.query.filter_by(position='box2').first()

    if request.method == 'POST':
        flyer1 = _replace_flyer('box1', 'flyer1_file', flyer1)
        flyer2 = _replace_flyer('box2', 'flyer2_file', flyer2)
        db.session.commit()
        flash("Flyers mis à jour.")
        return redirect(url_for('admin_events'))

    return render_template('admin_events.html', flyer1=flyer1, flyer2=flyer2)


# ============ Agenda Admin
@app.route('/admin/agenda', methods=['GET'])
@admin_required
def admin_agenda():
    form = RdvForm()
    agenda_entries = AgendaEntry.query.order_by(AgendaEntry.date).all()
    return render_template('admin_agenda.html', agenda_entries=agenda_entries, form=form)

@app.route('/admin/agenda/add', methods=['POST'])
@admin_required
def admin_agenda_add():
    form = RdvForm()
    if form.validate_on_submit():
        nouveau_rdv = AgendaEntry(
            date=form.date.data,
            heure_debut=form.debut.data,
            heure_fin=form.fin.data,
            description=form.description.data
        )
        db.session.add(nouveau_rdv)
        db.session.commit()
        flash("RDV ajouté avec succès.", "success")
    else:
        flash("Erreur dans le formulaire d'ajout.", "danger")
    return redirect(url_for('admin_agenda'))

@app.route('/admin/agenda/edit/<int:id>', methods=['POST'])
@admin_required
def admin_agenda_edit(id):
    form = RdvForm()
    if form.validate_on_submit():
        ancien_rdv = AgendaEntry.query.get_or_404(id)

        # Création nouveau RDV modifié
        nouveau_rdv = AgendaEntry(
            date=form.date.data,
            heure_debut=form.debut.data,
            heure_fin=form.fin.data,
            description=form.description.data
        )
        db.session.add(nouveau_rdv)
        db.session.delete(ancien_rdv)
        db.session.commit()

        flash("RDV modifié avec succès.", "success")
    else:
        flash("Erreur dans le formulaire de modification.", "danger")
    return redirect(url_for('admin_agenda'))


@app.route('/admin/agenda/delete/<int:id>', methods=['POST'])
@admin_required
def supprimer_rdv(id):
    rdv = AgendaEntry.query.get_or_404(id)
    db.session.delete(rdv)
    db.session.commit()
    flash("RDV supprimé avec succès.", "info")
    return redirect(url_for('admin_agenda'))


# =============== Admin Resultats
@app.route('/admin/resultats', methods=['GET', 'POST'])
@admin_required
def admin_resultats():
    form = ResultatForm()
    delete_form = DummyForm()  # Formulaire vide pour CSRF des suppressions

    if form.validate_on_submit():
        f = form.fichier_pdf.data
        filename = secure_filename(f.filename)
        key = f"resultats_pdfs/{filename}"

        # Uploade le PDF vers R2.
        storage.upload_fileobj(f.stream, key, content_type='application/pdf')

        nouveau_resultat = Resultat(
            titre=form.titre.data,
            date=form.date.data,
            fichier_pdf=key  # on stocke la cle R2 complete (compatible avec l'ancien format)
        )
        db.session.add(nouveau_resultat)
        db.session.commit()

        flash("Résultat ajouté avec succès !", "success")
        return redirect(url_for('admin_resultats'))

    resultats = Resultat.query.order_by(Resultat.date.desc()).all()
    return render_template('admin_resultats.html', resultats=resultats, form=form, delete_form=delete_form)

@app.route('/admin/resultats/delete/<int:id>', methods=['POST'])
@admin_required
def delete_resultat(id):
    resultat = Resultat.query.get_or_404(id)

    # Supprime le PDF dans R2.
    if resultat.fichier_pdf:
        storage.delete_object(resultat.fichier_pdf)

    # Supprime de la BDD
    db.session.delete(resultat)
    db.session.commit()
    flash("Résultat supprimé avec succès.", "success")
    return redirect(url_for('admin_resultats'))

# =========== Admin Galerie

@app.route('/admin_galerie', methods=['GET'])
@admin_required
def admin_galerie():
    photos = GaleriePhoto.query.order_by(GaleriePhoto.id).all()
    return render_template('admin_galerie.html', photos=photos)


def _upload_galerie_photo(image_file) -> str:
    """
    Helper interne : uploade l'image originale + un preview WebP genere
    automatiquement vers R2. Retourne le filename securise.
    """
    filename = secure_filename(image_file.filename)
    image_bytes = image_file.read()

    # Image originale (full)
    storage.upload_bytes(
        image_bytes,
        f'galerie/{filename}',
        content_type=image_file.mimetype,
    )

    # Preview WebP genere a la volee
    try:
        preview_bytes = storage.make_preview(image_bytes)
        storage.upload_bytes(
            preview_bytes,
            storage.preview_key_for(filename, prefix='galerie'),
            content_type='image/webp',
        )
    except Exception as e:
        # Si la generation du preview echoue, on log mais on n'echoue pas
        # l'upload : la galerie tombera en fallback sur l'image originale.
        print(f"[galerie] generation preview echouee pour {filename}: {e}")

    return filename


def _delete_galerie_photo(filename: str) -> None:
    """Supprime image originale + preview de R2."""
    if not filename:
        return
    storage.delete_object(f'galerie/{filename}')
    storage.delete_object(storage.preview_key_for(filename, prefix='galerie'))


@app.route('/admin_galerie/ajouter', methods=['POST'])
@admin_required
def ajouter_photo():
    image = request.files.get('image')
    description = request.form.get('description')
    if image and description:
        filename = _upload_galerie_photo(image)
        nouvelle_photo = GaleriePhoto(description=description, filename=filename)
        db.session.add(nouvelle_photo)
        db.session.commit()
    return redirect(url_for('admin_galerie'))


@app.route('/admin_galerie/edit', methods=['POST'])
@admin_required
def edit_photo():
    photo_id = request.form.get('id')
    new_description = request.form.get('description')
    image = request.files.get('image')

    photo = GaleriePhoto.query.get(photo_id)
    if photo:
        photo.description = new_description

        if image and image.filename:
            # Supprime ancienne image + preview dans R2.
            _delete_galerie_photo(photo.filename)
            # Uploade la nouvelle image + preview.
            photo.filename = _upload_galerie_photo(image)

        db.session.commit()
    return redirect(url_for('admin_galerie'))



@app.route('/admin_galerie/delete/<int:photo_id>', methods=['POST'])
@admin_required
def delete_photo(photo_id):
    photo = GaleriePhoto.query.get(photo_id)
    if photo:
        _delete_galerie_photo(photo.filename)
        db.session.delete(photo)
        db.session.commit()
    return redirect(url_for('admin_galerie'))



# =========== ROBOTS GOOGLE

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

@app.route('/llms.txt')
def llms():
    return app.send_static_file('llms.txt')

@app.route('/security.txt')
def security():
    return app.send_static_file('security.txt')


if __name__ == '__main__':
    app.run(debug=True)
