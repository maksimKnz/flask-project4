import csv
from models import db, Category, Meal

def add_to_database():
    with open("categories.tsv", "r") as tsv_file:
        read_tsv = csv.DictReader(tsv_file, delimiter='\t')
        for row in read_tsv:
            db.session.add(Category(**row))
    with open("meals.tsv", "r") as tsv_file:
        read_tsv = csv.DictReader(tsv_file, delimiter='\t')
        for row in read_tsv:
            db.session.add(Meal(**row))

    db.session.commit()
