from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Message
@login_required
def delete_user(request):
    if request.method == "POST":
        user = request.user
        logout(request)  # Log the user out before deleting
        user.delete()
        return redirect('account_deleted')  # Create this template/view or redirect as needed
    return render(request, 'messaging/delete_account_confirm.html')  # Confirmation page
["sender=request.user", "receiver"]
["Message.objects.filter", "select_related"]



def unread_inbox(request):
    user = request.user
    unread_messages = Message.unread.for_user(user)
    return render(request, 'messaging/inbox.html', {'unread_messages': unread_messages})
["Message.unread.unread_for_user"]
".only"
["cache_page"]
["cache_page", "60"]