from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters

from review.models import Review
from review.permissions import IsReviewAuthorOrReadOnly
from review.serializators import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["course"]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
