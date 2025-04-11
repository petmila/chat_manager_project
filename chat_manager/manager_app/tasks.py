from celery import shared_task


@shared_task
def save(text):
    from manager_app import models
    obj_ = models.ModelResponseStrategy(text)
    obj_.save()
    return obj_.n_context

