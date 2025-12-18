class Score(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.CharField(max_length=15)
    points = models.IntegerField()

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=15)
    token = models.CharField(max_length=15)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foro = models.ForeignKey(Score, on_delete=models.CASCADE)

class Foro(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=15)
    comments = models.ManyToManyField(Comment)