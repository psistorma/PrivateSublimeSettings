import functools as ft
import fn
from . import Basic


def askQuestions(showInputPanel, onDone, *questions, onChange=None, onCancel=None):
    questions = list(questions)
    if not questions:
        raise ValueError("questions is Empty!")

    qas = {}
    def _askCurQuestion():
        curQuestion = questions.pop()
        key = curQuestion["key"]
        init_text = curQuestion.get("init_text", "")
        title = curQuestion.get("title", key)
        pattern = curQuestion.get("pattern", None)
        answer_tempate = curQuestion.get("answer_tempate", None)
        default_dict = curQuestion.get("default_dict", None)

        def _oneQuestionDone(answer):
            if pattern is not None:
                transAnswer = Basic.promiseInput(pattern, answer, answer_tempate, default_dict)
                if transAnswer is None:
                    tip = "{title}:\n{info}\n{pattern}".format(
                        title=title,
                        info="It is not allowed!\nPlease input angin\nneeded pattern is:",
                        pattern=pattern)
                    showInputPanel(
                        _oneQuestionDone, tip, answer,
                        onChange=onChange, onCancel=onCancel)
                    return
                else:
                    answer = transAnswer

            qas[key] = answer

            if questions:
                _askCurQuestion()
            else:
                onDone(qas)

        showInputPanel(
            _oneQuestionDone, title, init_text,
            onChange=onChange, onCancel=onCancel)

    _askCurQuestion()

def fwAskQuestions(showInputPanel, onCancel):
    def decorator(f):
        @ft.wraps(f)
        def wrapper(*args, **kwds):
            questions = kwds.pop("questions", [])
            notify_question_cancel = kwds.pop("notify_question_cancel", True)
            if questions:
                askQuestions(
                    showInputPanel,
                    fn.F(f, *args, **kwds),
                    onCancel=onCancel if notify_question_cancel else None,
                    *questions)
            else:
                f(*args, **kwds)

        return wrapper

    return decorator
