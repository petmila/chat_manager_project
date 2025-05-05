from pgvector.django import CosineDistance

from manager_app.models import MessageEmbedding


def search_embeddings(self, embedding, chat_id):

    user_files = MessageEmbedding.objects.filter()

    files_with_distance = user_files.annotate(
        distance=CosineDistance("embedding_clip_vit_l_14", embedding)
    ).order_by("distance")[:12]

    # Process and return the search results