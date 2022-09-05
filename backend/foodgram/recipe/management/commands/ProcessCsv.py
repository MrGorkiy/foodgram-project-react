import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from recipe.models import Ingredient

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'ingredients.csv'), 'r', encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print(row)
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])