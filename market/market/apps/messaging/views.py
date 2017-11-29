from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import (DetailView,
                                  ListView,)

from extra_views import (CreateWithInlinesView)

from market.apps.board.models import Post
from market.apps.core.mixins import (CreateWithSenderMixin,
                                     OwnerRequiredMixin,
                                     SellerRequiredMixin)
from market.apps.core.models import UserProfile
from market.apps.messaging.forms import (MessageForm)
from market.apps.messaging.models import (Message)
from market.apps.social.models import SocialProfile

class MessageCreateView(CreateWithSenderMixin, CreateWithInlinesView):
    model = Message
    form_class = MessageForm
    template_name = 'messaging/message_form.html'

    def get_form(self, form_class):
        form = super().get_form(MessageForm)
        recipient = UserProfile.objects.filter(slug=self.kwargs['slug'])
        if len(recipient) > 0:
            form.fields['recipient'].queryset = recipient
        else:
            raise Http404("Invalid recipient attempted.")
        # Only objects owned by one of the two messengers can be discussed.
        form.fields['referenced_post'].queryset = Post.objects.filter(owner=recipient or self.request.profile).order_by('-modified')
        return form

    def get_success_url(self):
        messages.success(self.request, 'Message sent!', extra_tags='fa fa-check')
        return reverse('messaging:inbox')

class MessageDetailView(DetailView):
    model = Message
    template_name = 'messaging/message_detail.html'

    # Get's the communicator's social profile, if a seller.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = Message.objects.get(slug=self.kwargs['slug'])
        # If the message is for us, grab profile for the sender, otherwise the recipient
        if message.recipient == self.request.profile:
            context['in_inbox'] = True
            context['social_slug'] = (SocialProfile.objects.get(owner=message.sender)).slug
            # Other messages involving this person
            context['thread'] = Message.objects.filter(sender=message.sender, recipient=message.sender).order_by("-created")
        else:
            context['in_inbox'] = False
            context['social_slug'] = (SocialProfile.objects.get(owner=message.recipient)).slug
            # Other messages involving this person
            context['thread'] = Message.objects.filter(sender=message.recipient, recipient=message.recipient).order_by("-created")

        return context

# Returns a list of reviews for a specified user
class ReviewListView(ListView):
    model = Review
    template_name = 'messaging/review_list.html'
    paginate_by = 16

    def get_queryset(self, *args, **kwargs):
        user_profile = UserProfile.obects.get(slug=kwargs['slug'])
        if reviewee:
            return Review.objects.filter(reviewee=user_profile)
        else:
            raise Http404("Invalid Reviwee Searched.")
        
class ReviewCreateView(CreateWithSenderMixin, CreateWithInlinesView):
    model = Review
    form_class = ReviewForm
    template_name = 'messaging/message_form.html'

    def get_form(self, form_class):
        form = super().get_form(MessageForm)
        reviewee = UserProfile.objects.filter(slug=self.kwargs['slug'])
        if len(recipient) > 0:
            form.fields['reviewee'].queryset = reviewee
        else:
            raise Http404("Invalid Reviewee attempted.")
        return form

    def get_success_url(self):
        messages.success(self.request, 'Message sent!', extra_tags='fa fa-check')
        return reverse('messaging:inbox')

class ReviewDetailView(DetailView):
    model = Review
    template_name = 'messaging/review_detail.html'