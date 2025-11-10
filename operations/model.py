from typing import Optional

from operations.connect_browser import connect_to_browser_and_page

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

class muti_thread_config:
    ports: list[int]
    zujvanwang_catalogue_url: str
    zujvanwang_questions_urls: list[str]

    def __init__(self, ports: list[int], zujvanwang_catalogue_url: str, zujvanwang_questions_urls: Optional[list[str]] = None):
        self.ports = ports
        self.zujvanwang_catalogue_url = zujvanwang_catalogue_url
        self.zujvanwang_questions_urls = zujvanwang_questions_urls if zujvanwang_questions_urls is not None else []

    @classmethod
    async def create(cls, ports: list[int], zujvanwang_catalogue_url: str):
        browser, page = await connect_to_browser_and_page(port=2001, target_url=zujvanwang_catalogue_url, target_title="")
        zujvanwang_questions_urls =  await page.eval_on_selector_all(
            "ul.exam-list li a",  # 查找 <ul class="exam-list"> 中的 <a> 标签
            "elements => elements.map(el => 'https://zujuan.xkw.com' + el.getAttribute('href'))"  # 拼接基础 URL
        )
        if not zujvanwang_questions_urls:
            raise ValueError("Could not find any question URLs on the catalogue page.")
        return cls(ports, zujvanwang_catalogue_url, zujvanwang_questions_urls)