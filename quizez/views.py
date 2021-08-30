from django.shortcuts import render
from .models import *
from django.views.generic import ListView
from django.http import JsonResponse
from questions.models import *
from results.models import *

# Create your views here.


class QuizListView(ListView):
	Model = Quiz
	template_name = 'quizez/main.html'
	context_object_name = "quiz"

	def get_queryset(self):
		return Quiz.objects.all()


def quiz_view(request, pk):
	quiz = Quiz.objects.get(pk = pk)
	return render(request, 'quizez/quiz.html', {'obj': quiz})


def quiz_data_view(request, pk):

	quiz = Quiz.objects.get(pk = pk)
	question = []

	for q in quiz.get_questions():
		answer = []
		for a in q.get_answers():
			answer.append(a.text)
		question.append({str(q) : answer})
	return JsonResponse({
		'data':question,
		'time':quiz.time,
		})

def save_quiz_view(request, pk):
	print(request.POST)

	if request.is_ajax():
		questions = []
		data = request.POST
		data_ = dict(data.lists())
		
		data_.pop('csrfmiddlewaretoken')

		for k in data_.keys():
			print("keys ", k)
			question = Question.objects.get(text = k)
			questions.append(question)
		print(questions)

		user = request.user

		quiz = Quiz.objects.get(pk = pk)
		score = 0
		multiplier = 100 / quiz.number_of_questions
		results = []
		correct_answer = None

		for q in questions:
			a_selected = request.POST.get(q.text)
			
			if a_selected != "":
				print(a_selected)
				questions_answers = Answer.objects.filter(question = q)

				for a in questions_answers:
					if a_selected == a.text:
						if a.correct:
							score += 1
							correct_answer = a.text
					else:
						if a.correct:
							correct_answer = a.text
				results.append({str(q) : {'correct_answer': correct_answer, 'answered': a_selected}})
			else:
				results.append({str(q): 'Not answered'})

		final_res = score * multiplier
		print(final_res)
		Result.objects.create(quiz = quiz, user = user, score=final_res)

		if final_res >= quiz.required_score_to_pass:
			return JsonResponse({'passed': True, 'score': final_res, 'results':results})
		else:
			return JsonResponse({'passed': False, 'score': final_res, 'results':results})



				


	