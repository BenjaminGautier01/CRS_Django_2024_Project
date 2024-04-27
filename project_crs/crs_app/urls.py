from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('do', views.do, name='do'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('plot_chart', views.plot_chart, name='plot_chart'),
    path('print_patterns', views.print_patterns, name='print_patterns'),
    path('trade_proposal', views.trade_proposal, name='trade_proposal'),
    path('leave-message', views.leave_message, name='leave_message')
]
