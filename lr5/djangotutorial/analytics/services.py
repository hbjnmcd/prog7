from polls.models import Question, Choice

def get_poll_statistics(question_id: int) -> dict:
    question = Question.objects.get(id=question_id)
    choices = Choice.objects.filter(question=question)

    total_votes = sum(choice.votes for choice in choices)

    choices_data = []
    for choice in choices:
        percent = (choice.votes / total_votes * 100) if total_votes > 0 else 0
        choices_data.append({
            "id": choice.id,
            "text": choice.choice_text,
            "votes": choice.votes,
            "percent": round(percent, 2),
        })

    return {
        "poll_id": question.id,
        "question": question.question_text,
        "published_at": question.pub_date,
        "total_votes": total_votes,
        "choices": choices_data,
    }
