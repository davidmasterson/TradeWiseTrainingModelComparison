

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT,
    first VARCHAR(50) NOT NULL,
    last VARCHAR(50) NOT NULL,
    user_name VARCHAR(13) NOT NULL,
    password VARCHAR(100) NOT NULL,
    alpaca_key VARCHAR(150),
    alpaca_secret VARCHAR(150),
    PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS metrics(
    id INT AUTO_INCREMENT,
    accuracy Decimal(10,2),
    error_rate Decimal(10,2),
    cumulative_correct_pred INT,
    cumulative_incorrect_pred INT,
    time_to_close_correct_pred INT,
    cumulative_profit DECIMAL(10,2),
    cumulative_loss DECIMAL(10,2),
    sector_bd_profit JSON,
    sector_bd_loss JSON,
    sector_bd_rec JSON,
    sector_bd_nrec JSON,
    date_of_metric DATE,
    user_id INT,
    PRIMARY KEY (id),
    CONSTRAINT users_metrics FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE TABLE IF NOT EXISTS manual_metrics(
    id INT AUTO_INCREMENT,
    accuracy DECIMAL(10,2),
    error_rate Decimal(10,2),
    cumulative_correct_pred INT,
    cumulative_incorrect_pred INT,
    time_to_close_correct_pred INT,
    cumulative_profit DECIMAL(10,2),
    cumulative_loss DECIMAL(10,2),
    sector_bd_profit JSON,
    sector_bd_loss JSON,
    sector_bd_rec JSON,
    date_of_metric DATE,
    user_id INT,
    PRIMARY KEY (id),
    CONSTRAINT users_manual_metrics FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE TABLE IF NOT EXISTS transactions(
    id INT AUTO_INCREMENT,
    symbol VARCHAR(50) NOT NULL,
    dp VARCHAR(50) NOT NULL,
    ppps DECIMAL(10,2) NOT NULL,
    qty INT NOT NULL,
    total_buy DECIMAL(10,2) NOT NULL,
    pstring VARCHAR(100) NOT NULL,
    ds VARCHAR(50),
    spps DECIMAL(10,2),
    tsp DECIMAL(10,2),
    sstring VARCHAR(100),
    expected DECIMAL(10,2) NOT NULL,
    proi DECIMAL(10,2),
    actual DECIMAL(10,2),
    tp1 DECIMAL(10,2) NOT NULL,
    sop DECIMAL(10,2) NOT NULL,
    prediction INT NOT NULL,
    result INT,
    user_id INT,
    PRIMARY KEY (id),
    CONSTRAINT users_transactions FOREIGN KEY (user_id) REFERENCES users(id)
)

CREATE TABLE IF NOT EXISTS user_preferences(
    id INT AUTO_INCREMENT,
    min_pps DECIMAL(10,2) NOT NULL,
    max_pps DECIMAL(10,2) NOT NULL,
    min_inv_per_sym DECIMAL(10,2) NOT NULL,
    max_inv_per_sym DECIMAL(10,2) NOT NULL,
    user_id INT,
    PRIMARY KEY (id),
    CONSTRAINT users_users_preferences FOREIGN KEY (user_id) REFERENCES users(id)
)