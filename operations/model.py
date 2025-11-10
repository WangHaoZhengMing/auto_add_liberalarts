from typing import Optional

class questionData:
    origin: str
    stem: str
    origin_from_our_bank: list[str]
    
    def __init__(self, origin: str, stem: str, origin_from_our_bank: Optional[list[str]] = None):
        self.origin = origin
        self.stem = stem
        self.origin_from_our_bank = origin_from_our_bank if origin_from_our_bank is not None else []

class question_page:
    name: str
    province: str
    grade: str
    year: int
    subject: str
    stemlist: list[questionData]

    def __init__(self, name: str, province: str, grade: str, year: int, subject: str, stemlist: list[questionData]):
        self.name = name
        self.province = province
        self.grade = grade
        self.year = year
        self.subject = subject
        self.stemlist = stemlist