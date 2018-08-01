from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField('Date created')
    create_by = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category)

    def categories_as_string(self):
        cats_string = ""
        for category in self.categories.all():
            cats_string += category.name.title()
            cats_string += ", "
        return cats_string

    def __str__(self):
        return self.title
