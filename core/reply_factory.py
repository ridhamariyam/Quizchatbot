from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    if "reset_chat" in message.lower():
        reset_chat(session)
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session["current_question_id"] = 0
        session.save()
        return bot_responses

    current_question_id = session.get("current_question_id")

    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        question_text, options, next_question_id, _ = get_next_question(0)
        bot_responses.append(question_text)
        bot_responses.extend(options)
        session["current_question_id"] = next_question_id
        session.save()
        return bot_responses

    question_text, options, next_question_id, prev = get_next_question(current_question_id)

    

    if question_text:
        bot_responses.append(question_text)
        bot_responses.extend(options)

        if not session.get("user_answers"):
            session["user_answers"] = {}

        user_response = message.strip().lower()
        

        
        if not user_response:
            bot_responses.append(question_text)
            bot_responses.extend(options)
            return bot_responses

       
        
        success, error = record_current_answer(user_response, prev, session)
        if not success:
            bot_responses.append(error)

        session["current_question_id"] = next_question_id
        session.save()
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)
        session.clear()

    return bot_responses


def record_current_answer(user_response, current_question_text, session):
    user_answers = session.get("user_answers", {})
    
    user_answers[current_question_text] = user_response
    
    session["user_answers"] = user_answers
    session.save()

    return True, "Answer recorded successfully"


def get_next_question(current_question_id):
    if current_question_id is None:
        return BOT_WELCOME_MESSAGE, [], 0  # Initialize to the first question

    if current_question_id < len(PYTHON_QUESTION_LIST):
        current_question = PYTHON_QUESTION_LIST[current_question_id]
        question_text = current_question["question_text"]
        options = current_question.get("options", [])
        prev = None
        if current_question_id:
            prev = PYTHON_QUESTION_LIST[current_question_id - 1]['question_text']
        return question_text, options, current_question_id + 1, prev

    # No more questions, return final response
    return None, [], None, None


def reset_chat(session):
    session.clear()


def generate_final_response(session):
    user_answers = session.get("user_answers", {})
    correct_answers = 0

    final_response = ""  

    for question in PYTHON_QUESTION_LIST:
        question_text = question["question_text"]
        user_answer = user_answers.get(question_text, "").lower()
        correct_answer = question["answer"].lower()

        # final_response += f"Question: {question_text}\n"
        # final_response += f"Your Answer: {user_answer}\n"
        # final_response += f"Correct Answer: {correct_answer}\n\n"

        # Check if the user's answer matches any of the options
        if user_answer in [option.lower() for option in question.get("options", [])]:
            correct_answers += 1

    total_questions = len(PYTHON_QUESTION_LIST) - 1  # Adjust the total number of questions
    score_percentage = (correct_answers / total_questions) * 100

    final_response += f"You scored {correct_answers} out of {total_questions} questions ({score_percentage}%).\n"

    return final_response

