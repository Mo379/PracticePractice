from django.urls import path, include
from user import views


# Create your views here.
app_name = 'user'
urlpatterns = [
    # Pages
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path(
        'forgotpassword',
        views.ForgotPasswordView.as_view(),
        name='forgot-password'
    ),
    path(
        'pwdreset/<uidb64>/<token>',
        views.PwdResetView.as_view(),
        name='pwdreset'
    ),
    path(
        'deleteaccount/<uidb64>/<token>',
        views.DeleteAccountView.as_view(),
        name='deleteaccount'
    ),
    path('billing', views.BillingView.as_view(), name='billing'),
    path('security', views.SecurityView.as_view(), name='security'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    path('join', views.JoinView.as_view(), name='join'),
    # payments views
    path(
        'addpaymentmethod',
        views.AddPaymentMethodView.as_view(),
        name='addpaymentmethod'
    ),
    # actions
    path('_login', views._loginUser, name='_login'),
    path('_registerUser', views._registerUser, name='_register'),
    path('_updatepassword', views._updatepassword, name='_updatepassword'),
    path('_pwdreset_form', views._pwdreset_form, name='_pwdreset_form'),
    path('_pwdreset', views._pwdreset, name='_pwdreset'),
    path('_activate/<uidb64>/<token>', views._activate, name='_activate'),
    path('_logout', views._logoutUser, name='_logout'),
    #
    path('_deleteaccount_1', views._deleteaccount_1, name='_deleteaccount_1'),
    path('_deleteaccount_2', views._deleteaccount_2, name='_deleteaccount_2'),
    path('_logout', views._logoutUser, name='_logout'),
    path('_logout', views._logoutUser, name='_logout'),
    #
    path('_appearance', views._logoutUser, name='_appearance'),
    # actions - detail forms
    path('_accountdetails', views._accountdetails, name='_accountdetails'),
    path('_admindetails', views._admindetails, name='_admindetails'),
    path('_studentdetails', views._studentdetails, name='_studentdetails'),
    path(
        '_organisationdetails',
        views._organisationdetails,
        name='_organisationdetails'
    ),
    path('_educatordetails', views._educatordetails, name='_educatordetails'),
    path('_editordetails', views._editordetails, name='_editordetails'),
    path(
        '_affiliatedetails',
        views._affiliatedetails,
        name='_affiliatedetails'
    ),
    path(
        '_themechange',
        views._themechange,
        name='_themechange'
    ),
    path(
        '_languagechange',
        views._languagechange,
        name='_languagechange'
    ),
    path(
        '_mailchoiceschange',
        views._mailchoiceschange,
        name='_mailchoiceschange'
    ),
    # payment actions
    path(
        '_makedefaultpaymentmethod',
        views._makedefaultpaymentmethod,
        name='_makedefaultpaymentmethod'
    ),
    path(
        '_deletepaymentmethod',
        views._deletepaymentmethod,
        name='_deletepaymentmethod'
    ),
    path(
        '_create_checkout_session',
        views._create_checkout_session,
        name='_create_checkout_session'
    ),
]
