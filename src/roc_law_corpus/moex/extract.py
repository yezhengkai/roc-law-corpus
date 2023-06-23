import re
import sys
from functools import reduce
from hashlib import sha256
from pathlib import Path

import orjson
import pdfplumber


def init_json_data(destination_json) -> list:
    """Initialize json_data"""
    if destination_json.exists():
        with open(destination_json, "rb") as rf:
            json_data = orjson.loads(rf.read())
    else:
        json_data = []
    return json_data


def check_data_in_json(json_data, sha256_digest) -> bool:
    """Check if data is already in json"""
    if json_data == []:
        in_json_data = False
    else:
        in_json_data = reduce(
            lambda x, y: x or y, map(lambda x: sha256_digest == x["sha256"], json_data)
        )
    return in_json_data


def clean_exam_content(content: str, num_page: int) -> str:
    # Substitute semantically equivalent string for unicode
    # \ue18c => (A)
    # \ue18d => (B)
    # \ue18e => (C)
    # \ue18f => (D)
    # \ue190 => (E)
    # \ue1293 => (一)
    # \ue12a => (二)
    # \ue12b => (三)
    content = (
        content.replace("\ue18c", "(A)")
        .replace("\ue18d", "(B)")
        .replace("\ue18e", "(C)")
        .replace("\ue18f", "(D)")
        .replace("\ue190", "(E)")
        .replace("\ue129", "(一)")
        .replace("\ue12a", "(二)")
        .replace("\ue12b", "(三)")
    )
    # Substitute empty string for description
    content = re.sub(rf"^[\s\S]*?頁次：\s*{num_page}－1\n", "", content)
    # Substitute empty string for "頁次：xx-xx\n"
    content = re.sub(rf"頁次：\s*{num_page}－\d+\s*\n", "", content)
    # Substitute empty string for "代號：xxxx"
    content = re.sub("代號：\s*\d+", "", content)
    return content


def extract_questions(content: str) -> list:
    questions = []
    for i, m in enumerate(
        re.finditer(r"^\d[\s\S]*?\n(?=\(A\))", content, re.MULTILINE), start=1
    ):
        segments = re.split(str(i), m.group(0), maxsplit=0)
        if len(segments) == 2:
            question = segments[-1]
        else:
            question = str(i) + segments[-1]
            for segment in segments[-2::-1]:
                if segment == "" or segment[-1] == "\n":
                    question = re.split(str(i), question, maxsplit=1)[-1]
                    break
                question = str(i) + segment + question
        questions.append(question)
    return questions


def extract_choices(
    content: str, questions: list, num_question: int
) -> tuple[list, list, list, list, list]:
    choices_A, choices_B, choices_C, choices_D, choices_E = [], [], [], [], []
    for i in range(num_question):
        if i == num_question - 1:
            choices = re.search(
                f"(?<={re.escape(questions[-1])})[\s\S]*", content
            ).group(0)
        else:
            choices = re.search(
                f"(?<={re.escape(questions[i])})[\s\S]*?(?=\d+{re.escape(questions[i+1])})",
                content,
            ).group(0)
        choice_A = (
            re.search("\(A\)[\s\S]*?(?=\(B\))", choices)
            .group(0)
            .replace("\n", "")
            .strip()
        )
        choice_B = (
            re.search("\(B\)[\s\S]*?(?=\(C\))", choices)
            .group(0)
            .replace("\n", "")
            .strip()
        )
        choice_C = (
            re.search("\(C\)[\s\S]*?(?=\(D\))", choices)
            .group(0)
            .replace("\n", "")
            .strip()
        )
        if "(E)" in choices:
            choice_D = (
                re.search("\(D\)[\s\S]*?(?=\(E\))", choices)
                .group(0)
                .replace("\n", "")
                .strip()
            )
            choice_E = (
                re.search("\(E\)[\s\S]*$", choices).group(0).replace("\n", "").strip()
            )
        else:
            choice_D = (
                re.search("\(D\)[\s\S]*$", choices).group(0).replace("\n", "").strip()
            )
            choice_E = ""
        choices_A.append(choice_A)
        choices_B.append(choice_B)
        choices_C.append(choice_C)
        choices_D.append(choice_D)
        choices_E.append(choice_E)
    return choices_A, choices_B, choices_C, choices_D, choices_E


def extract_answers(
    tables: list[list[list[str | None]]],
    choices_A: list,
    choices_B: list,
    choices_C: list,
    choices_D: list,
    choices_E: list,
) -> list[str]:
    answers = list(
        filter(
            lambda c: c.isupper(),
            (tables[i][1][j] for i in range(len(tables)) for j in range(1, 11)),
        )
    )

    for i, answer in enumerate(answers):
        answers[i] = ""
        for char_ABCDE in answer:
            if char_ABCDE == "A":
                answers[i] += choices_A[i] + "\n"
            elif char_ABCDE == "B":
                answers[i] += choices_B[i] + "\n"
            elif char_ABCDE == "C":
                answers[i] += choices_C[i] + "\n"
            elif char_ABCDE == "D":
                answers[i] += choices_D[i] + "\n"
            elif char_ABCDE == "E":
                answers[i] += choices_E[i]

    answers = list(map(lambda x: x.strip(), answers))  # clean up answers
    return answers


def extract_pdf_content(pdf_dir: str, destination_json: str):
    pdf_dir = Path(pdf_dir)
    destination_json = Path(destination_json)
    json_data = init_json_data(destination_json)

    # Multiple choice question（MC, MCQ）
    for file_q in pdf_dir.glob("*_question.pdf"):
        # Get the pdf path to the answer
        file_a = Path(re.sub(r"question(?=\.pdf$)", "answer", str(file_q)))
        exam = re.match("\S+(?=_question\.pdf$)", file_q.name).group(0)
        print(exam)

        sha256_digest = sha256(open(file_q, "rb").read()).hexdigest()
        in_json_data = check_data_in_json(json_data, sha256_digest)
        if in_json_data:
            # Append exams
            if not reduce(
                lambda x, y: x or y, map(lambda x: exam in x["exams"], json_data)
            ):
                list(filter(lambda x: sha256_digest in x["sha256"], json_data))[0][
                    "exams"
                ].append(exam)
            continue

        print("[Start] Extract questions and choices")
        reader = pdfplumber.open(file_q)
        num_page = len(reader.pages)

        content = ""
        for page in reader.pages:
            content += page.extract_text()
        content = clean_exam_content(content, num_page)

        questions = extract_questions(content)
        num_question = len(questions)

        choices_A, choices_B, choices_C, choices_D, choices_E = extract_choices(
            content, questions, num_question
        )
        # clean up questions
        questions = list(map(lambda x: x.replace("\n", "").strip(), questions))
        print("[End] Extract questions and choices")

        print("[Start] Extract answers")
        reader = pdfplumber.open(file_a)
        tables = reader.pages[0].extract_tables()
        answers = extract_answers(
            tables, choices_A, choices_B, choices_C, choices_D, choices_E
        )
        print("[End] Extract answers")

        print("[Start] Append QA to json data")
        qa_corpus = []
        for i in range(num_question):
            qa_corpus.append(
                {
                    "question": questions[i],
                    "choices": (
                        choices_A[i]
                        + "\n"
                        + choices_B[i]
                        + "\n"
                        + choices_C[i]
                        + "\n"
                        + choices_D[i]
                        + "\n"
                        + choices_E[i]
                    ).strip(),
                    "choice_A": choices_A[i],
                    "choice_B": choices_B[i],
                    "choice_C": choices_C[i],
                    "choice_D": choices_D[i],
                    "choice_E": choices_E[i],
                    "answer": answers[i],
                }
            )
        json_data.append({"sha256": sha256_digest, "exams": [exam], "qa": qa_corpus})
        print("[End] Append QA to json data")

    print("[Start] Dump QA to json file")
    with open(destination_json, "wb") as wf:
        wf.write(orjson.dumps(json_data, option=orjson.OPT_INDENT_2))
    print("[End] Dump QA to json file")


if __name__ == "__main__":
    extract_pdf_content(sys.argv[1], sys.argv[2])
