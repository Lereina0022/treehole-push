drop database treehole_push;

CREATE DATABASE IF NOT EXISTS treehole_push CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE treehole_push;

CREATE TABLE IF NOT EXISTS subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    query_text VARCHAR(255) NOT NULL,
    rule_json JSON NOT NULL,
    is_active TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    pid BIGINT PRIMARY KEY,
    text TEXT,
    post_type VARCHAR(50),
    timestamp BIGINT,
    post_datetime DATETIME NULL,
    label INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    like_num INT DEFAULT 0,
    raw_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_posts_timestamp (timestamp),
    INDEX idx_posts_datetime (post_datetime)
);

CREATE TABLE IF NOT EXISTS push_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    pid BIGINT NOT NULL,
    subscription_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_push_sub FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
    CONSTRAINT fk_push_post FOREIGN KEY (pid) REFERENCES posts(pid) ON DELETE CASCADE,
    UNIQUE KEY uniq_pid_sub (pid, subscription_id),
    INDEX idx_push_status (status),
    INDEX idx_push_created_at (created_at)
);


INSERT INTO subscriptions (category_name, query_text, rule_json, is_active)
VALUES (
  '实习jd',
  '实习 产品',
  JSON_OBJECT(
    'mode', 'advanced',
    'groups', JSON_ARRAY(
      JSON_ARRAY('实习'),
      JSON_ARRAY('产品')
    ),
    'exclude', JSON_ARRAY()
  ),
  1
);

INSERT INTO subscriptions (category_name, query_text, rule_json, is_active)
VALUES (
  '课程签到',
  '考古学通论 签到',
  JSON_OBJECT(
    'mode', 'advanced',
    'groups', JSON_ARRAY(
      JSON_ARRAY('考古学通论'),
      JSON_ARRAY('签到', '打卡', '点名')
    ),
    'exclude', JSON_ARRAY()
  ),
  1
);