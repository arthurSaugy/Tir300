"""
Script de migration des donnees SQLite -> PostgreSQL.

Usage :
    1. S'assurer que DATABASE_URL pointe vers la base PostgreSQL CIBLE
       (variable d'environnement ou .env).
    2. Avoir le fichier SQLite source accessible (par defaut :
       instance/mydatabase.db).
    3. Executer :
           python migrate_data.py
       ou avec un chemin SQLite explicite :
           python migrate_data.py chemin/vers/mydatabase.db

Comportement :
    - Cree les tables sur PostgreSQL si elles n'existent pas.
    - Refuse de demarrer si une des tables cibles n'est pas vide,
      sauf si --force est passe (auquel cas elle est videe avant copie).
    - Copie ligne par ligne les enregistrements en preservant les IDs.
    - Recale les sequences PostgreSQL pour que les prochains INSERTs
      utilisent un ID superieur au maximum copie.
"""

from __future__ import annotations

import os
import sys
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine, select, text, inspect
from sqlalchemy.orm import sessionmaker

from models import db, Resultat, AgendaEntry, EventFlyer, GaleriePhoto


MODELS = [Resultat, AgendaEntry, EventFlyer, GaleriePhoto]


def normalize_pg_url(url: str) -> str:
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


def build_sqlite_url(sqlite_path: str) -> str:
    abs_path = os.path.abspath(sqlite_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Fichier SQLite introuvable : {abs_path}")
    # SQLite : 4 slashes pour un chemin absolu (sqlite:////chemin/abs)
    return f"sqlite:///{abs_path}"


def copy_table(model, src_session, dst_session) -> int:
    rows = src_session.execute(select(model)).scalars().all()
    count = 0
    for row in rows:
        # Construire un dict des colonnes (sans les attributs internes SQLAlchemy)
        data = {
            col.name: getattr(row, col.name)
            for col in model.__table__.columns
        }
        dst_session.add(model(**data))
        count += 1
    dst_session.commit()
    return count


def reset_pg_sequence(model, dst_session) -> None:
    """
    Recale la sequence d'auto-increment PostgreSQL apres une copie qui a
    preserve les IDs explicites. Sans ca, les prochains INSERTs sans ID
    pourraient generer des doublons de cle primaire.
    """
    table = model.__table__.name
    pk_col = next(iter(model.__table__.primary_key.columns)).name
    sql = text(
        f"SELECT setval(pg_get_serial_sequence(:t, :c), "
        f"COALESCE((SELECT MAX({pk_col}) FROM {table}), 1), "
        f"(SELECT MAX({pk_col}) IS NOT NULL FROM {table}))"
    )
    dst_session.execute(sql, {'t': table, 'c': pk_col})
    dst_session.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Migration SQLite -> PostgreSQL")
    parser.add_argument(
        'sqlite_path',
        nargs='?',
        default=os.path.join('instance', 'mydatabase.db'),
        help="Chemin vers le fichier SQLite source (defaut : instance/mydatabase.db)"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Vider les tables PostgreSQL existantes avant la copie."
    )
    args = parser.parse_args()

    pg_url = os.environ.get('DATABASE_URL')
    if not pg_url:
        print("ERREUR : DATABASE_URL doit pointer vers la base PostgreSQL cible.")
        return 1
    pg_url = normalize_pg_url(pg_url)

    if pg_url.startswith('sqlite'):
        print("ERREUR : DATABASE_URL pointe vers SQLite, pas PostgreSQL.")
        return 1

    sqlite_url = build_sqlite_url(args.sqlite_path)

    print(f"Source  : {sqlite_url}")
    print(f"Cible   : {pg_url}")
    print()

    src_engine = create_engine(sqlite_url)
    dst_engine = create_engine(pg_url)

    # Cree les tables sur PostgreSQL si necessaire.
    db.metadata.create_all(dst_engine)

    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)

    src_session = SrcSession()
    dst_session = DstSession()

    try:
        # Verifie l'etat des tables cibles
        inspector = inspect(dst_engine)
        non_empty = []
        for model in MODELS:
            if inspector.has_table(model.__table__.name):
                count = dst_session.execute(
                    text(f"SELECT COUNT(*) FROM {model.__table__.name}")
                ).scalar()
                if count and count > 0:
                    non_empty.append((model.__table__.name, count))

        if non_empty and not args.force:
            print("Les tables suivantes ne sont pas vides cote PostgreSQL :")
            for name, n in non_empty:
                print(f"  - {name} : {n} ligne(s)")
            print("Relance avec --force pour les vider avant la copie.")
            return 2

        if args.force and non_empty:
            print("Vidage des tables PostgreSQL non vides...")
            # On supprime dans l'ordre inverse pour eviter les soucis de FK
            for model in reversed(MODELS):
                dst_session.execute(text(f"DELETE FROM {model.__table__.name}"))
            dst_session.commit()

        # Copie
        for model in MODELS:
            n = copy_table(model, src_session, dst_session)
            print(f"  {model.__table__.name:20s} -> {n} ligne(s) copiee(s)")
            reset_pg_sequence(model, dst_session)

        print()
        print("Migration terminee avec succes.")
        return 0
    finally:
        src_session.close()
        dst_session.close()


if __name__ == '__main__':
    sys.exit(main())
