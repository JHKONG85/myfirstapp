import streamlit as st
import random

# 상태 초기화
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.questions = []
    st.session_state.show_result = False
    st.session_state.finished = False

def generate_questions(num_questions=10):
    questions = []
    for _ in range(num_questions):
        a = random.randint(2, 9)
        b = random.randint(1, 9)
        answer = a * b
        wrong_choices = set()
        while len(wrong_choices) < 2:
            wrong = random.randint(1, 81)
            if wrong != answer:
                wrong_choices.add(wrong)
        choices = list(wrong_choices) + [answer]
        random.shuffle(choices)
        questions.append({
            'question': f"{a} × {b} = ?",
            'answer': answer,
            'choices': choices
        })
    return questions

def reset_quiz():
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.questions = generate_questions()
    st.session_state.show_result = False
    st.session_state.finished = False

st.title("🧮 구구단 퀴즈")

if not st.session_state.questions:
    reset_quiz()

if st.session_state.finished:
    st.success(f"퀴즈 완료! 점수: {st.session_state.score}/10 🎉")
    st.info("고생 많았어요! 다시 도전해보세요! 💪")
    if st.button("처음으로"):
        reset_quiz()
else:
    q = st.session_state.questions[st.session_state.question_index]
    st.subheader(f"문제 {st.session_state.question_index + 1}/10")
    st.write(q['question'])

    cols = st.columns(3)
    for i, choice in enumerate(q['choices']):
        if cols[i].button(str(choice)):
            if choice == q['answer']:
                st.session_state.score += 1
                st.session_state.show_result = True
                st.balloons()
                st.success("정답입니다! 🎉")
            else:
                st.session_state.show_result = True
                st.error("틀렸어요! 다시 도전해보세요! 💡")

            if st.session_state.question_index < 9:
                st.session_state.question_index += 1
            else:
                st.session_state.finished = True

            st.rerun()
