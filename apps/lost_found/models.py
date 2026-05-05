from django.db import models
from django.conf import settings

# Create your models here.
class lost_and_found_status(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.status_name
    
class lost_and_found_category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.category_name
class lost_and_found_post(models.Model):
    post_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    lost_or_found_date = models.DateField()
    location = models.CharField(max_length=100)
    type = models.CharField(max_length=10)  # 'lost' or 'found'
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lost_and_found_posts')
    lost_and_found_status = models.ForeignKey(lost_and_found_status, on_delete=models.CASCADE)
    lost_and_found_category = models.ForeignKey(lost_and_found_category, on_delete=models.CASCADE)
    photos = models.ManyToManyField('media.Photo', blank=True, related_name='lost_and_found_posts')

    def __str__(self):
        return self.title
    
class claim_request_status(models.Model):
    claim_request_status_id = models.IntegerField(primary_key=True)
    claim_request_status_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.claim_request_status_name

class claim_request(models.Model):
    claim_id = models.IntegerField(primary_key=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claim_requests')
    claim_request_status = models.ForeignKey(claim_request_status, on_delete=models.CASCADE)
    lost_and_found_post = models.ForeignKey(lost_and_found_post, on_delete=models.CASCADE)

    def __str__(self):
        return f"Claim {self.claim_id} for Post {self.lost_and_found_post.title}"
    
class lost_and_found_match(models.Model):
    match_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=20)  
    created_at = models.DateTimeField(auto_now_add=True)

    lost_post = models.ForeignKey(lost_and_found_post, related_name='lost_post', on_delete=models.CASCADE)
    found_post = models.ForeignKey(lost_and_found_post, related_name='found_post', on_delete=models.CASCADE)
    claim_id = models.OneToOneField(claim_request, on_delete=models.CASCADE)

    def __str__(self):
        return f"Match {self.match_id} between Lost Post {self.lost_post.title} and Found Post {self.found_post.title}"
class claim_request_thread(models.Model):
    claim_id = models.OneToOneField(claim_request, on_delete=models.CASCADE, primary_key=True)
    thread_id = models.OneToOneField('threads.Thread', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)