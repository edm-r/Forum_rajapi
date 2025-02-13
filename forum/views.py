from rest_framework import generics
from .models import Forum
from .serializers import ForumSerializer
from .authentication import MicroserviceTokenAuthentication
from rest_framework.permissions import IsAuthenticated

class ForumListCreateView(generics.ListCreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ForumRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    authentication_classes = [MicroserviceTokenAuthentication]
    permission_classes = [IsAuthenticated]