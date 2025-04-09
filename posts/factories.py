from .models import Post

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content='', metadata=None):
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError("Invalid post type")

        if post_type == 'image' and ('file_size' not in metadata or not metadata['file_size']):
            raise ValueError("Image posts require 'file_size' in metadata")

        if post_type == 'video' and ('duration' not in metadata or not metadata['duration']):
            raise ValueError("Video posts require 'duration' in metadata")

        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata
        )