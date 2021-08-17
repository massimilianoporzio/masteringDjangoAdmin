from django.db import models

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=200)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "The Authors"

    def __str__(self):
        return u'%s' % self.name

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    refAuthor = models.ForeignKey(Author, on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'[%s] : %s' % (self.refAuthor, self.question_text)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s : %s' % (self.question, self.choice_text)

# FA RIF A UNA VISTA SU DB NON UNA TABELLA DI CUI DJANGO HA IL CONTROLLO COMPLETO
class QuestionSummary(models.Model):
    month = models.DateField()
    nbQuestionsByMonth = models.IntegerField()

    class Meta:
        managed = False # VEDI COMMENTO
        db_table = 'app_questionsummary' #NOME DELLA VISTA (SU DB ora NON C'è)


# E' un PROXY - MI FA VEDERE AuthorAdmin un'altra volta
class AuthorClone(Author):
    class Meta:
        proxy=True
        verbose_name_plural = "The Authors clone"