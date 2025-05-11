from pgvector.django import CosineDistance

from manager_app import models


def similarity_search(embedding, chat_id):
    messages = models.Message.objects.filter(chat_id=chat_id,
                                                 timestamp__range=(first_date, last_date)).order_by('timestamp')

    files_with_distance = messages .annotate(
        distance=CosineDistance("embedding", embedding)
    ).order_by("distance")[:12]

    return files_with_distance