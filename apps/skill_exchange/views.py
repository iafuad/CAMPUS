from django.http import HttpResponse


def index(request):
	return HttpResponse("Skill Exchange: index")


def post_list(request):
	return HttpResponse("Skill Exchange: post list")


def post_detail(request, post_id):
	return HttpResponse(f"Skill Exchange: post detail {post_id}")


def post_create(request):
	return HttpResponse("Skill Exchange: post create")


def match_list(request):
	return HttpResponse("Skill Exchange: match list")


def match_detail(request, match_id):
	return HttpResponse(f"Skill Exchange: match detail {match_id}")


def session_detail(request, session_id):
	return HttpResponse(f"Skill Exchange: session detail {session_id}")


def feedback_create(request, session_id):
	return HttpResponse(f"Skill Exchange: feedback create for session {session_id}")
