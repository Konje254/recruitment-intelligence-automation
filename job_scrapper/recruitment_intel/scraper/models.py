from django.db import models

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ScrapeRun(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="running")  # running|success|failed
    requested_limit = models.PositiveIntegerField(default=0)
    logs = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.platform.name} run #{self.id} ({self.status})"

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    website_url = models.URLField(blank=True, default="")
    email = models.EmailField(blank=True, default="")

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    title = models.CharField(max_length=300)
    location = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    # Many-to-many via a through table so we can keep source URLs per platform
    platforms = models.ManyToManyField(Platform, through="JobSource")

    normalized_key = models.CharField(max_length=600, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company.name}"

class JobSource(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    source_url = models.URLField()

    class Meta:
        unique_together = ("job", "platform", "source_url")
