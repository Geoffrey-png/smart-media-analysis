import hashlib
import html
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from sqlalchemy.orm import Session

from app.algorithms.content_analyzer import analyze_content_payload, calculate_quality_score
from app.models.content import Content
from app.services.content_service import content_to_dict, join_tags


DEFAULT_NEWS_SOURCES = [
    {
        "key": "chinanews",
        "name": "中国新闻网",
        "url": "https://www.chinanews.com.cn/rss/scroll-news.xml",
    },
    {
        "key": "cctv_society",
        "name": "央视网社会新闻",
        "url": "http://www.cctv.com/program/rss/02/06/index.xml",
    },
    {
        "key": "bbc_zh",
        "name": "BBC中文",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
    },
    {
        "key": "bbc_world",
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    },
    {
        "key": "bbc_tech",
        "name": "BBC Technology",
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    },
    {
        "key": "bbc_business",
        "name": "BBC Business",
        "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
    },
    {
        "key": "bbc_sport",
        "name": "BBC Sport",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
    },
]


@dataclass
class CrawledNews:
    title: str
    link: str
    summary: str
    published_at: datetime | None
    source_name: str


class ParagraphExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_p = False
        self._buffer: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "p":
            self._in_p = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag.lower() == "p" and self._in_p:
            text = _clean_text("".join(self._buffer))
            if len(text) >= 30:
                self.paragraphs.append(text)
            self._in_p = False
            self._buffer = []

    def handle_data(self, data):
        if self._in_p:
            self._buffer.append(data)


def source_list() -> list[dict]:
    return DEFAULT_NEWS_SOURCES


def _clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _fetch_text(url: str, timeout: int = 10, max_bytes: int = 800_000) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 SmartMediaCrawler/1.0",
            "Accept": "text/html,application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "identity",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(max_bytes)
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="ignore")


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1].lower()


def _child_text(element, names: set[str]) -> str:
    for child in list(element):
        if _local_name(child.tag) in names:
            return _clean_text(child.text or "")
    return ""


def _entry_link(element) -> str:
    for child in list(element):
        local = _local_name(child.tag)
        if local == "link":
            href = child.attrib.get("href")
            if href:
                return href.strip()
            return (child.text or "").strip()
    return ""


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        return dt.replace(tzinfo=None)
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return None


def parse_feed(xml_text: str, source: dict) -> list[CrawledNews]:
    root = ET.fromstring(xml_text)
    entries = [item for item in root.iter() if _local_name(item.tag) in {"item", "entry"}]
    items: list[CrawledNews] = []
    for entry in entries:
        title = _child_text(entry, {"title"})
        link = _entry_link(entry)
        summary = _child_text(entry, {"description", "summary", "content", "encoded"})
        published = _child_text(entry, {"pubdate", "published", "updated", "date"})
        if not title or not link:
            continue
        items.append(
            CrawledNews(
                title=title,
                link=link,
                summary=summary,
                published_at=_parse_datetime(published),
                source_name=source["name"],
            )
        )
    return items


def fetch_article_text(url: str, fallback: str) -> str:
    try:
        html_text = _fetch_text(url, timeout=8)
    except Exception:
        return fallback

    extractor = ParagraphExtractor()
    try:
        extractor.feed(html_text)
    except Exception:
        return fallback
    text = "\n".join(extractor.paragraphs[:12]).strip()
    if len(text) < max(80, len(fallback)):
        return fallback
    return text[:6000]


def _news_external_id(link: str) -> str:
    return hashlib.sha1(link.encode("utf-8")).hexdigest()


def _create_content_from_news(db: Session, news: CrawledNews, fetch_full_text: bool) -> Content | None:
    link = news.link.strip()
    if db.query(Content).filter(Content.source_url == link).first():
        return None

    body = fetch_article_text(link, news.summary) if fetch_full_text else news.summary
    body = body or news.summary or news.title
    content = Content(
        title=news.title[:255],
        summary=news.summary[:500],
        content=body,
        author=news.source_name,
        source_name=news.source_name,
        source_url=link,
        content_type="article",
        status="published",
        publish_time=news.published_at or datetime.utcnow(),
        view_count=0,
        like_count=0,
        favorite_count=0,
        comment_count=0,
    )
    analysis = analyze_content_payload(content.title, content.content, content)
    content.summary = content.summary or analysis["summary"]
    content.category = analysis["category"]
    content.tags = join_tags(analysis["keywords"])
    content.sentiment = analysis["sentiment"]
    content.sensitive_words = join_tags(analysis["sensitive_words"])
    if analysis["sensitive_words"]:
        content.status = "pending"
    content.heat_score = analysis["heat_score"]
    content.quality_score = calculate_quality_score(content)
    # 没有独立 external_id 字段，用 source_url 去重；这里保留 hash 方便以后扩展。
    _news_external_id(link)
    db.add(content)
    return content


def import_news(
    db: Session,
    source_key: str = "all",
    limit: int = 20,
    fetch_full_text: bool = True,
    custom_url: str = "",
    custom_name: str = "自定义新闻源",
) -> dict:
    if source_key == "custom" and custom_url:
        selected_sources = [{"key": "custom", "name": custom_name or "自定义新闻源", "url": custom_url}]
    else:
        selected_sources = DEFAULT_NEWS_SOURCES if source_key == "all" else [s for s in DEFAULT_NEWS_SOURCES if s["key"] == source_key]
    if not selected_sources:
        return {"imported_count": 0, "skipped_count": 0, "items": [], "errors": [f"未知新闻源：{source_key}"]}

    imported: list[Content] = []
    skipped_count = 0
    errors: list[str] = []

    for source in selected_sources:
        if len(imported) >= limit:
            break
        try:
            feed_xml = _fetch_text(source["url"], timeout=10)
            feed_items = parse_feed(feed_xml, source)
        except Exception as exc:
            errors.append(f"{source['name']} 抓取失败：{exc}")
            continue

        for item in feed_items:
            if len(imported) >= limit:
                break
            try:
                # RSS 里有些相对链接，统一转成绝对地址。
                item.link = urljoin(source["url"], item.link)
                content = _create_content_from_news(db, item, fetch_full_text)
                if content is None:
                    skipped_count += 1
                    continue
                imported.append(content)
            except Exception as exc:
                errors.append(f"{item.title[:40]} 导入失败：{exc}")

    db.commit()
    for item in imported:
        db.refresh(item)

    return {
        "imported_count": len(imported),
        "skipped_count": skipped_count,
        "items": [content_to_dict(item) for item in imported],
        "errors": errors,
    }
