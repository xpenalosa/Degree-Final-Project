from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class PublishedManager(models.Manager):

    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

class IncompleteObjectiveManager(models.Manager):

    def get_queryset(self):
        return super(IncompleteObjectiveManager, self).get_queryset().filter(completed=False)

class Post(models.Model):
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               related_name='blog_posts',
                               on_delete=models.CASCADE)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug])


class Comment(models.Model):

    post = models.ForeignKey(Post,
        related_name='comments',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)
   
    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class Objective(models.Model):
    
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    OPTIONAL = 1

    PRIORITY_CHOICES = (
        (CRITICAL, 'Critica'),
        (HIGH, 'Alta'),
        (NORMAL, 'Normal'),
        (LOW, 'Baixa'),
        (OPTIONAL, 'Opcional'),
    )

    description = models.CharField(max_length=80)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES,
                                                default=NORMAL)
    completed = models.BooleanField(default=False)
    time_estimated = models.DecimalField(max_digits=4,
                                         decimal_places=1)
    time_completed = models.DecimalField(max_digits=4,
                                         decimal_places=1,
                                         null=True)
    body = models.TextField()
    slug = models.SlugField(max_length=16)

    objects = models.Manager()
    incomplete = IncompleteObjectiveManager()

    class Meta:
        ordering = ('-priority', 'completed',)

    def __str__(self):
        s = self.description
        if self.completed:
            s += ' {}/{}'.format(self.time_completed,self.time_estimated)
        else:
            s += ' - {}'.format(self.get_priority())
        return s

    def get_priority(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority)

    def get_absolute_url(self):
        return reverse('blog:objectius_detail',
                             args=[self.slug])

