-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,                      -- 用户名（唯一）
  nickname VARCHAR(50),                                      -- 昵称（可为空）
  avatar VARCHAR(255),                                       -- 头像URL或路径
  signature VARCHAR(255),                                    -- 个人签名
  password VARCHAR(255) NOT NULL,                            -- 密码（建议使用哈希存储）
  email VARCHAR(100),                                        -- 邮箱
  phone VARCHAR(20),                                         -- 手机号（支持国际号码）
  id_card VARCHAR(30) NOT NULL UNIQUE,                       -- 身份证号（唯一）
  real_name VARCHAR(100),                                    -- 真实姓名
  gender ENUM('男', '女', '未知') DEFAULT '未知',               -- 性别（枚举类型）
  age TINYINT UNSIGNED DEFAULT NULL,                         -- 年龄（最大255，无符号）
  user_type ENUM('passenger', 'admin', 'staff') DEFAULT 'passenger', -- 用户类型
  vip_level TINYINT DEFAULT 0 CHECK (vip_level BETWEEN 0 AND 4), -- VIP等级（0~4）
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP               -- 注册时间
);



-- 飞机型号信息
CREATE TABLE IF NOT EXISTS aircraft(
  aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
  model_name VARCHAR(50) NOT NULL COMMENT 'Boeing 737-800',
  business_capacity SMALLINT NOT NULL COMMENT '0',              -- 商务舱定员人数
  first_class_capacity SMALLINT NOT NULL COMMENT '0',           -- 头等舱定员人数
  economy_capacity SMALLINT NOT NULL COMMENT '0',             -- 经济舱定员人数
  UNIQUE (model_name)
);

-- 航线
CREATE TABLE IF NOT EXISTS routes (
  route_id INT AUTO_INCREMENT PRIMARY KEY,
  departure_city VARCHAR(50) NOT NULL,
  arrival_city VARCHAR(50) NOT NULL,
  distance_km INT,
  UNIQUE (departure_city, arrival_city)
);

-- 具体某次航班信息
CREATE TABLE IF NOT EXISTS flights (
  flight_id INT AUTO_INCREMENT PRIMARY KEY,
  flight_number VARCHAR(20) NOT NULL UNIQUE COMMENT 'CA1234',
  airline VARCHAR(50) NOT NULL COMMENT '所属航空公司',
  route_id INT NOT NULL COMMENT '航线ID（外键）',
  aircraft_id INT NOT NULL COMMENT '执飞机型ID（外键）',
  departure_time DATETIME NOT NULL COMMENT '预计起飞时间',
  arrival_time DATETIME NOT NULL COMMENT '预计到达时间',
  business_price DECIMAL(10,2) NOT NULL COMMENT '商务舱单价',
  economy_price DECIMAL(10,2) NOT NULL COMMENT '经济舱单价',
  first_class_price DECIMAL(10,2) NOT NULL COMMENT '头等舱单价',
  business_seats_available SMALLINT NOT NULL COMMENT '可售商务舱座位数',
  economy_seats_available SMALLINT NOT NULL COMMENT '可售经济舱座位数',
  first_class_seats_available SMALLINT NOT NULL COMMENT '可售头等舱座位数',
  status ENUM('计划中', '已起飞', '已到达', '延误', '取消') DEFAULT '计划中' COMMENT '航班状态',
  FOREIGN KEY (route_id) REFERENCES routes(route_id),
  FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id)
);

-- 完整订单信息
CREATE TABLE IF NOT EXISTS orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  flight_id INT NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  payment_status ENUM('待支付', '已支付', '已取消') DEFAULT '待支付',
  trip_status ENUM('待值机', '已值机待起飞', '已结束') DEFAULT '待值机',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  payment_method VARCHAR(50),
  order_number VARCHAR(50) NOT NULL UNIQUE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);

-- 订单乘机人信息
CREATE TABLE IF NOT EXISTS order_passengers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  passenger_name VARCHAR(100) NOT NULL,
  id_card VARCHAR(30) NOT NULL,
  phone VARCHAR(20),
  seat_class ENUM('经济舱', '商务舱', '头等舱') NOT NULL,         -- 严格限定三种舱类
  seat_number VARCHAR(10),
  price DECIMAL(10,2) NOT NULL,                               -- 从 flights 表中取对应舱位的价格
  booked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 通知表
CREATE TABLE IF NOT EXISTS notices (
  notice_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  type ENUM('info', 'warning', 'success', 'error') DEFAULT 'info',
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

-- 用户通知关联表
CREATE TABLE IF NOT EXISTS user_notices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  notice_id INT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  read_at DATETIME DEFAULT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (notice_id) REFERENCES notices(notice_id),
  UNIQUE KEY unique_user_notice (user_id, notice_id)
);