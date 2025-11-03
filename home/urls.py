# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/student-login/', views.student_login_credentials, name='student_login'),
    path('api/create-test/', views.create_test, name='create_test'),
    path('api/create-student/', views.create_student_with_login, name='create_student'),
    path('api/get-tests/', views.get_tests, name='get_tests'),
    path('api/get-students/', views.get_students, name='get_students'),
    path('api/get-results/', views.get_results, name='get_results'),
    path('api/get-ranking/', views.get_ranking, name='get_ranking'),
    path('api/delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('api/delete-test/<int:test_id>/', views.delete_test, name='delete_test'),
    path('api/update-student/<int:student_id>/', views.update_student, name='update_student'),
    path('api/update-test/<int:test_id>/', views.update_test, name='update_test'),
    path('api/get-student/<int:student_id>/', views.get_student, name='get_student'),
    path('api/get-test/<int:test_id>/', views.get_test, name='get_test'),
    path('api/get-all-students/', views.get_all_students, name='get_all_students'),
    
    # Student API
    path('api/get-test-questions/<int:test_id>/', views.get_test_questions, name='get_test_questions'),
    path('api/submit-test/', views.submit_test, name='submit_test'),
    path('api/get-student-results/', views.get_student_results, name='get_student_results'),
    path('api/get-student-ranking/', views.get_student_ranking, name='get_student_ranking'),
    path('api/get-student-activity/', views.get_student_activity, name='get_student_activity'),
    path('api/set-admin-session/', views.set_admin_session, name='set_admin_session'),
    
    path('health/', views.health_check, name='health_check'),
]