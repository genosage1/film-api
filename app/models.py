from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Category(Base):
    """分类（动作片/喜剧片/连续剧…）"""
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Vod(Base):
    """影片主表"""
    __tablename__ = "vod"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    sub_title: Mapped[str] = mapped_column(String(255), default="")
    type_name: Mapped[str] = mapped_column(String(50), default="")   # 动作 / 喜剧 / 连续剧
    region: Mapped[str] = mapped_column(String(50), default="")      # 大陆 / 欧美
    language: Mapped[str] = mapped_column(String(50), default="")
    year: Mapped[str] = mapped_column(String(10), default="")       # 上映年份
    score: Mapped[float] = mapped_column(Float, default=0)         # 豆瓣评分
    director: Mapped[str] = mapped_column(String(255), default="")
    actor: Mapped[str] = mapped_column(Text, default="")
    remarks: Mapped[str] = mapped_column(String(100), default="")   # 最新：全24集 / HD
    poster: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source_name: Mapped[str] = mapped_column(String(50), default="")  # 来源站标识
    source_url: Mapped[str] = mapped_column(String(500), default="")  # 源详情页（去重/回源用）
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)   # md5(title+year+region) 去重
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    play_sources: Mapped[list["VodPlay"]] = relationship(back_populates="vod", cascade="all, delete-orphan")


class VodPlay(Base):
    """播放源：一部片多条线路，每条线路多集"""
    __tablename__ = "vod_play"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vod_id: Mapped[int] = mapped_column(ForeignKey("vod.id", ondelete="CASCADE"), index=True)
    play_from: Mapped[str] = mapped_column(String(50), default="")   # 线路名：线路1 / 高清
    episode_name: Mapped[str] = mapped_column(String(200), default="")  # 第01集 / 正片
    play_url: Mapped[str] = mapped_column(String(1000), default="")      # m3u8 / mp4

    vod: Mapped[Vod] = relationship(back_populates="play_sources")
