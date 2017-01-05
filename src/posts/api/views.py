from django.db.models import Q

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
    )

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,    
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView, 
    RetrieveUpdateAPIView,    
    )

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination
    
from posts.models import Post
from .permissions import IsOwnerOrReadOnly

from .serializers import (
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer, 
    )



class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        '''Called by CreateModelMixin when saving a new object instance.'''
        serializer.save(user=self.request.user)


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

class PostUpdatelAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        '''Change the user from the original user that submitted it to new user, 
        that updeted it'''
        serializer.save(user=self.request.user)

class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]

class PostListAPIView(ListAPIView): 
    serializer_class = PostListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'content', 'user__first_name']
    pagination_class = PostLimitOffsetPagination
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        'QuerySet' in which case 'QuerySet' specific behavior will be enabled.
        """
        queryset_list = Post.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query)|
                    Q(content__icontains=query)|
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query)
                    ).distinct()
        return queryset_list