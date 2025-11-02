from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Avg, Q
import json
from .models import Student, Test, Question, Answer, TestResult, StudentActivity, StudentLogin

def index(request):
    """Asosiy sahifa - endi index.html ni asosiy papkadan oladi"""
    return render(request, 'index.html')  # O'zgartirildi

@csrf_exempt
def student_login_credentials(request):
    """Login va parol orqali tizimga kirish"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            print(f"Login attempt: {username}")
            
            if not username or not password:
                return JsonResponse({'success': False, 'error': "Iltimos, login va parolni kiriting!"})
            
            # Demo admin login
            if username == "admin" and password == "admin123":
                request.session['is_admin'] = True
                request.session['admin_name'] = "Admin User"
                return JsonResponse({
                    'success': True, 
                    'message': "Admin sifatida muvaffaqiyatli kirdingiz!",
                    'is_admin': True
                })
            
            # Student login
            try:
                student_login = StudentLogin.objects.select_related('student').get(username=username)
                
                if student_login.check_password(password):
                    student = student_login.student
                    
                    # Check if student is locked
                    if student.locked_until and student.locked_until > timezone.now():
                        lock_time = student.locked_until - timezone.now()
                        minutes = int(lock_time.total_seconds() // 60)
                        return JsonResponse({'success': False, 'error': f"Siz bloklangansiz! {minutes} daqiqadan keyin qayta urinib ko'ring."})
                    
                    # Successful login
                    student.login_attempts = 0
                    student.locked_until = None
                    student.is_online = True
                    student.save()
                    
                    request.session['student_id'] = student.id
                    request.session['student_name'] = f"{student.familya} {student.ism}"
                    request.session['is_admin'] = False
                    
                    # Log activity
                    StudentActivity.objects.create(
                        student=student,
                        activity_type='login',
                        details='Login/parol orqali tizimga kirdi'
                    )
                    
                    return JsonResponse({
                        'success': True, 
                        'message': f"Xush kelibsiz, {request.session['student_name']}!",
                        'is_admin': False
                    })
                else:
                    # Failed login
                    student = student_login.student
                    student.login_attempts += 1
                    
                    if student.login_attempts >= 3:
                        student.locked_until = timezone.now() + timezone.timedelta(minutes=5)
                    
                    student.save()
                    return JsonResponse({'success': False, 'error': "Noto'g'ri parol!"})
                
            except StudentLogin.DoesNotExist:
                return JsonResponse({'success': False, 'error': "Login topilmadi! Iltimos, admin bilan bog'laning."})
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Server xatosi: {str(e)}"})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def admin_dashboard(request):
    """Admin paneli"""
    if not request.session.get('is_admin'):
        messages.error(request, "Iltimos, avval tizimga kiring")
        return redirect('index')
    
    try:
        students = Student.objects.all()
        tests = Test.objects.all()
        test_results = TestResult.objects.all()
        
        context = {
            'admin_name': request.session.get('admin_name', 'Admin'),
            'students_count': students.count(),
            'tests_count': tests.count(),
            'active_tests_count': tests.filter(is_active=True).count(),
            'completed_tests_count': test_results.count(),
        }
        return render(request, 'admin.html', context)  # O'zgartirildi
    except Exception as e:
        print(f"Admin dashboard error: {str(e)}")
        context = {
            'admin_name': request.session.get('admin_name', 'Admin'),
            'students_count': 0,
            'tests_count': 0,
            'active_tests_count': 0,
            'completed_tests_count': 0,
        }
        return render(request, 'admin.html', context)  # O'zgartirildi

def student_dashboard(request):
    """Student paneli"""
    if not request.session.get('student_id'):
        messages.error(request, "Iltimos, avval tizimga kiring")
        return redirect('index')
    
    try:
        student_id = request.session['student_id']
        student = get_object_or_404(Student, id=student_id)
        
        # FAQAT FAOL TESTLARNI OLISH
        tests = Test.objects.filter(is_active=True).prefetch_related(
            'questions',
            'questions__answers'
        ).order_by('-created_at')
        
        # Student natijalarini olish
        student_results = TestResult.objects.filter(student=student).select_related('test')
        
        # Debug ma'lumotlari
        print(f"Found {tests.count()} active tests for student")
        for test in tests:
            print(f"Test: {test.title}, Questions: {test.questions.count()}")
        
        context = {
            'student_name': request.session.get('student_name', 'Student'),
            'student': student,
            'tests': tests,
            'student_results': student_results,
        }
        return render(request, 'student.html', context)  # O'zgartirildi
        
    except Exception as e:
        print(f"Student dashboard error: {str(e)}")
        # Agar xatolik bo'lsa, bo'sh testlar bilan ishlash
        context = {
            'student_name': request.session.get('student_name', 'Student'),
            'tests': [],
            'student_results': [],
        }
        return render(request, 'student.html', context)  # O'zgartirildi

def logout(request):
    """Chiqish"""
    student_id = request.session.get('student_id')
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            student.is_online = False
            student.save()
        except Student.DoesNotExist:
            pass
    
    request.session.flush()
    messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz")
    return redirect('index')

# API Views - Admin uchun
@csrf_exempt
def create_test(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Test yaratish
            test = Test.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                time_limit=data.get('time_limit', 60),
                max_score=data.get('max_score', 100),
                is_active=True  # HAR DOIM FAOL BO'LIB YARATILADI
            )
            
            # Savollar va javoblarni yaratish
            for question_data in data.get('questions', []):
                question = Question.objects.create(
                    test=test,
                    text=question_data['text'],
                    order=question_data.get('order', 0)
                )
                
                for answer_data in question_data.get('answers', []):
                    Answer.objects.create(
                        question=question,
                        text=answer_data['text'],
                        is_correct=answer_data.get('is_correct', False)
                    )
            
            return JsonResponse({
                'success': True, 
                'test_id': test.id,
                'message': f'"{test.title}" testi muvaffaqiyatli yaratildi!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def create_student_with_login(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Student yaratish
            student = Student.objects.create(
                familya=data['familya'],
                ism=data['ism'],
                group=data.get('group', ''),
                is_online=False
            )
            
            # Login ma'lumotlarini yaratish
            student_login = StudentLogin.objects.create(
                student=student,
                username=data['username']
            )
            student_login.set_password(data['password'])
            student_login.save()
            
            return JsonResponse({
                'success': True, 
                'student_id': student.id,
                'message': f"O'quvchi va login muvaffaqiyatli yaratildi!"
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def get_tests(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        tests = Test.objects.annotate(questions_count=Count('questions')).values(
            'id', 'title', 'description', 'time_limit', 'max_score', 'is_active', 'questions_count', 'created_at'
        ).order_by('-created_at')
        
        return JsonResponse({'success': True, 'tests': list(tests)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_students(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        students = Student.objects.all().values(
            'id', 'ism', 'familya', 'group', 'is_online', 'login_attempts', 'created_at'
        ).order_by('-created_at')
        
        return JsonResponse({'success': True, 'students': list(students)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_results(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        results = TestResult.objects.select_related('student', 'test').all().values(
            'id', 'student__ism', 'student__familya', 'test__title', 'score', 
            'correct_answers', 'total_questions', 'completed_at'
        ).order_by('-completed_at')
        
        return JsonResponse({'success': True, 'results': list(results)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_ranking(request):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        ranking = Student.objects.annotate(
            avg_score=Avg('testresult__score'),
            tests_taken=Count('testresult')
        ).filter(tests_taken__gt=0).order_by('-avg_score').values(
            'id', 'ism', 'familya', 'avg_score', 'tests_taken'
        )
        
        return JsonResponse({'success': True, 'ranking': list(ranking)})  # Tuzatildi: success True bo'lishi kerak
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def delete_student(request, student_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'DELETE':
        try:
            student = get_object_or_404(Student, id=student_id)
            
            # Login ma'lumotlarini ham o'chirish
            StudentLogin.objects.filter(student=student).delete()
            student.delete()
            
            return JsonResponse({'success': True, 'message': 'O\'quvchi muvaffaqiyatli o\'chirildi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def delete_test(request, test_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'DELETE':
        try:
            test = get_object_or_404(Test, id=test_id)
            test.delete()
            return JsonResponse({'success': True, 'message': 'Test muvaffaqiyatli o\'chirildi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def update_student(request, student_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            student = get_object_or_404(Student, id=student_id)
            
            student.familya = data.get('familya', student.familya)
            student.ism = data.get('ism', student.ism)
            student.group = data.get('group', student.group)
            student.save()
            
            # Login ma'lumotlarini yangilash
            if 'username' in data:
                student_login, created = StudentLogin.objects.get_or_create(student=student)
                student_login.username = data['username']
                
                if 'password' in data and data['password']:
                    student_login.set_password(data['password'])
                
                student_login.save()
            
            return JsonResponse({'success': True, 'message': 'O\'quvchi ma\'lumotlari yangilandi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def update_test(request, test_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            test = get_object_or_404(Test, id=test_id)
            
            test.title = data.get('title', test.title)
            test.description = data.get('description', test.description)
            test.time_limit = data.get('time_limit', test.time_limit)
            test.max_score = data.get('max_score', test.max_score)
            test.is_active = data.get('is_active', test.is_active)
            test.save()
            
            return JsonResponse({'success': True, 'message': 'Test ma\'lumotlari yangilandi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def get_student(request, student_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        student = get_object_or_404(Student, id=student_id)
        student_login = StudentLogin.objects.filter(student=student).first()
        
        student_data = {
            'id': student.id,
            'ism': student.ism,
            'familya': student.familya,
            'group': student.group,
            'is_online': student.is_online,
            'username': student_login.username if student_login else ''
        }
        
        return JsonResponse({'success': True, 'student': student_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_test(request, test_id):
    if not request.session.get('is_admin'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        test = get_object_or_404(Test, id=test_id)
        
        test_data = {
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'time_limit': test.time_limit,
            'max_score': test.max_score,
            'is_active': test.is_active,
            'questions': []
        }
        
        # Savollarni olish
        for question in test.questions.all().prefetch_related('answers'):
            question_data = {
                'id': question.id,
                'text': question.text,
                'order': question.order,
                'answers': []
            }
            
            # Javoblarni olish
            for answer in question.answers.all():
                question_data['answers'].append({
                    'id': answer.id,
                    'text': answer.text,
                    'is_correct': answer.is_correct
                })
            
            test_data['questions'].append(question_data)
        
        return JsonResponse({'success': True, 'test': test_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Student API Views
@csrf_exempt
def get_test_questions(request, test_id):
    if not request.session.get('student_id'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    try:
        test = get_object_or_404(Test, id=test_id, is_active=True)
        questions = Question.objects.filter(test=test).prefetch_related('answers')
        
        questions_data = []
        for question in questions:
            answers_data = []
            for answer in question.answers.all():
                answers_data.append({
                    'id': answer.id,
                    'text': answer.text
                    # is_correct ni yubormaymiz
                })
            
            questions_data.append({
                'id': question.id,
                'text': question.text,
                'order': question.order,
                'answers': answers_data
            })
        
        return JsonResponse({
            'success': True, 
            'questions': questions_data,
            'test_title': test.title,
            'time_limit': test.time_limit
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def submit_test(request):
    if not request.session.get('student_id'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = request.session['student_id']
            test_id = data['test_id']
            answers = data['answers']  # {question_id: answer_id}
            
            student = get_object_or_404(Student, id=student_id)
            test = get_object_or_404(Test, id=test_id)
            
            # Ball hisoblash
            total_questions = test.questions.count()
            correct_answers = 0
            
            for question_id, answer_id in answers.items():
                try:
                    question = Question.objects.get(id=question_id, test=test)
                    correct_answer = question.answers.filter(is_correct=True).first()
                    
                    if correct_answer and str(correct_answer.id) == str(answer_id):
                        correct_answers += 1
                except (Question.DoesNotExist, Answer.DoesNotExist):
                    continue
            
            score = (correct_answers / total_questions) * test.max_score if total_questions > 0 else 0
            
            # Natijani saqlash
            TestResult.objects.create(
                student=student,
                test=test,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_answers,
                answers_data=answers
            )
            
            # Faollikni log qilish
            StudentActivity.objects.create(
                student=student,
                activity_type='test_complete',
                details=f'"{test.title}" testini {score:.1f} ball bilan yakunladi'
            )

            return JsonResponse({
                'success': True,
                'score': round(score, 1),
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'message': f'Test muvaffaqiyatli yakunlandi! Siz {score:.1f} ball to\'pladingiz.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
def set_admin_session(request):
    """Demo admin uchun session o'rnatish"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['is_admin'] = data.get('is_admin', False)
            request.session['admin_name'] = data.get('admin_name', 'Admin')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})