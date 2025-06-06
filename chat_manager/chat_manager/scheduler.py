from django_celery_beat.schedulers import DatabaseScheduler


class PatchedDatabaseScheduler(DatabaseScheduler):
    def apply_async(self, entry, producer=None, advance=True, **kwargs):
        periodic_task_id = entry.model.id

        if entry.args or entry.kwargs:
            task_kwargs = entry.kwargs.copy()
        else:
            task_kwargs = {}

        task_kwargs["periodic_task_id"] = periodic_task_id
        entry.kwargs = task_kwargs
        return super().apply_async(entry, producer=producer, advance=advance, **kwargs)
