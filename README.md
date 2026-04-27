# Tir300 Villeneuve FR

Site Flask du stand de tir 300m de Villeneuve FR.

## Prerequis

- Python 3
- dependances de `requirements.txt`
- En production : PostgreSQL (Render). En local : SQLite par defaut
  (aucune installation supplementaire).

## Variables d'environnement

- `SECRET_KEY` : cle secrete Flask (sessions, CSRF)
- `ADMIN_PASSWORD` : mot de passe de l'espace admin
- `DATABASE_URL` (optionnelle) : URL de connexion PostgreSQL. Si non
  definie, l'application utilise la base SQLite locale
  `instance/mydatabase.db`. Voir `.env.example`.

En local, ces variables peuvent etre definies dans un fichier `.env`
charge automatiquement par `python-dotenv`.

## Lancement local

1. Installer les dependances :

   ```bash
   pip install -r requirements.txt
   ```

2. Copier `.env.example` vers `.env` et remplir `SECRET_KEY` et
   `ADMIN_PASSWORD`. Laisser `DATABASE_URL` commentee pour utiliser
   SQLite localement.

3. Lancer l'application :

   ```bash
   python app.py
   ```

   Au demarrage, `db.create_all()` cree les tables si elles n'existent
   pas encore.

## Migration des donnees SQLite existantes vers PostgreSQL

Un script `migrate_data.py` est fourni pour transferer le contenu d'un
ancien fichier SQLite (`instance/mydatabase.db`) vers la base PostgreSQL
cible.

```bash
# 1. S'assurer que DATABASE_URL pointe vers la base PostgreSQL CIBLE.
# 2. Lancer la migration :
python migrate_data.py

# Si la base cible contient deja des donnees a effacer :
python migrate_data.py --force

# Avec un chemin SQLite explicite :
python migrate_data.py /chemin/vers/mydatabase.db
```

Le script preserve les IDs et recale les sequences PostgreSQL.

## Deploiement sur Render

1. Sur Render, creer une instance **PostgreSQL** (Dashboard > New >
   PostgreSQL). Noter le nom de la base.
2. Aller dans le service web Tir300 > Environment > "Add from Database"
   et selectionner la base PostgreSQL : Render injecte automatiquement
   `DATABASE_URL`.
3. S'assurer que les variables `SECRET_KEY` et `ADMIN_PASSWORD` sont
   bien definies cote Render.
4. Redeployer le service web. Au demarrage, les tables sont creees
   automatiquement si elles n'existent pas.
5. Pour migrer les donnees existantes vers la base Render :
   - Recuperer la "External Database URL" depuis le dashboard Render.
   - Exporter temporairement cette URL en local :
     `export DATABASE_URL="postgresql://..."`
   - Lancer `python migrate_data.py` depuis la machine locale.

Note : Render utilise historiquement le prefixe `postgres://` dans
`DATABASE_URL`. L'application le convertit automatiquement en
`postgresql://` (requis par SQLAlchemy 2.x).

## Notes de maintenance

- Le site sert `robots.txt`, `sitemap.xml`, `llms.txt` et `security.txt`
  depuis le dossier `static`.
- Les uploads (PDF, images de galerie, flyers) sont stockes sur le
  filesystem. Sur Render, sans Persistent Disk, ces fichiers sont
  ephemeres et disparaissent a chaque redeploiement. Prevoir un Disk
  Render attache aux dossiers `static/resultats_pdfs/`,
  `static/uploads/galerie/` et `static/event_images/`, ou migrer ces
  uploads vers un stockage externe (S3, Cloudflare R2, etc.).
- Les fichiers generes localement et caches Python ne sont pas
  versionnes.
