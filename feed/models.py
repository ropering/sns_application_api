from django.db import models
from account.models import User


class Feed(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    like_count = models.PositiveIntegerField(default=0)  # 좋아요 개수를 표시하기 위해 사용 (정수형, 0 이상)

    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    feed = models.ForeignKey(Feed, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.comment