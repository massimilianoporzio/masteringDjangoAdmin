
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "masteringAdmin.settings")
from django.utils import timezone
import django
django.setup()

from faker import factory,Faker
from sample_app.models import  Author, Question, Choice
from model_bakery.recipe import Recipe,foreign_key



fake = Faker()
for k in range(100):
    author = Recipe(Author,
                    name=fake.name(),
                    createdDate=fake.future_datetime(end_date="+30d",  tzinfo=timezone.get_current_timezone()),
                    updatedDate=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()), )

    question = Recipe(Question,
                      question_text=fake.sentence(nb_words=6, variable_nb_words=True),
                      pub_date=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()),
                      refAuthor=foreign_key(author),
                      createdDate=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()),
                      updatedDate=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()), )

    choice = Recipe(Choice,
                    question=foreign_key(question),
                    choice_text=fake.sentence(nb_words=1, variable_nb_words=True),
                    createdDate=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()),
                    updatedDate=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()), )

    choice.make()