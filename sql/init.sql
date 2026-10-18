-- 生产环境 MySQL 建表脚本（SQLite 由 SQLAlchemy 自动建表，可不用此文件）
CREATE DATABASE IF NOT EXISTS film_api DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE film_api;

CREATE TABLE IF NOT EXISTS category (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  sort INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vod (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  sub_title   VARCHAR(255) DEFAULT '',
  type_name   VARCHAR(50)  DEFAULT '',
  region      VARCHAR(50)  DEFAULT '',
  language    VARCHAR(50)  DEFAULT '',
  year        VARCHAR(10)  DEFAULT '',
  score       FLOAT        DEFAULT 0,
  director    VARCHAR(255) DEFAULT '',
  actor       TEXT,
  remarks     VARCHAR(100) DEFAULT '',
  poster      VARCHAR(500) DEFAULT '',
  description TEXT,
  source_name VARCHAR(50)  DEFAULT '',
  source_url  VARCHAR(500) DEFAULT '',
  fingerprint VARCHAR(64) NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_vod_title (title),
  INDEX idx_vod_fingerprint (fingerprint)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vod_play (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  vod_id       INT NOT NULL,
  play_from    VARCHAR(50)  DEFAULT '',
  episode_name VARCHAR(200) DEFAULT '',
  play_url     VARCHAR(1000) DEFAULT '',
  INDEX idx_play_vod (vod_id),
  CONSTRAINT fk_play_vod FOREIGN KEY (vod_id) REFERENCES vod(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
