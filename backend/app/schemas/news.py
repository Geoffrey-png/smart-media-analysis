from pydantic import BaseModel, Field


class NewsImportRequest(BaseModel):
    source_key: str = Field(default="all", description="新闻源 key，all 表示全部默认源")
    limit: int = Field(default=20, ge=1, le=100, description="最多导入数量")
    fetch_full_text: bool = Field(default=True, description="是否尝试抓取新闻详情页正文")
    custom_url: str = Field(default="", description="自定义 RSS 地址，source_key=custom 时生效")
    custom_name: str = Field(default="自定义新闻源", description="自定义新闻源名称")
