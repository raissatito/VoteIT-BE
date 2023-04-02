from django.db import models
from auth_user.models import User

# Create your models here.
class VoteRoom(models.Model):
    room_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    participant = models.ManyToManyField(User, related_name='participant')
    is_private = models.BooleanField(default=False)

class VoteOption(models.Model):
    room = models.ForeignKey(VoteRoom, on_delete=models.CASCADE)
    vote_option = models.CharField(max_length=100)
    voter = models.ManyToManyField(User)
    vote_amount = models.IntegerField(default=0)

    class meta:
        unique_together = ('room', 'vote_option')
