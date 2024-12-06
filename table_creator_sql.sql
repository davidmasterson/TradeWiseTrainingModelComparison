CREATE TABLE `datasets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dataset_name` varchar(100) NOT NULL,
  `dataset_description` varchar(100) NOT NULL,
  `dataset_data` longblob NOT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dataset_name_UNIQUE` (`dataset_name`),
  KEY `dataset_user_id_idx` (`user_id`),
  CONSTRAINT `dataset_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `metrics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `accuracy` float NOT NULL,
  `error_rate` float NOT NULL,
  `cumulative_correct_pred` int NOT NULL,
  `cumulative_incorrect_pred` int NOT NULL,
  `time_to_close_correct_pred` int NOT NULL,
  `cumulative_profit` float NOT NULL,
  `cumulative_loss` float NOT NULL,
  `sector_bd_profit` json NOT NULL,
  `sector_bd_loss` json NOT NULL,
  `date_of_metric` date NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `metrics_user_id_idx` (`user_id`),
  CONSTRAINT `metrics_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `model_metrics_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_id` int NOT NULL,
  `accuracy` float NOT NULL,
  `precision` float NOT NULL,
  `recall` float NOT NULL,
  `f1_score` float NOT NULL,
  `top_features` json NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `model_metrics_history_model_id_idx` (`model_id`),
  CONSTRAINT `model_history_model_id` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `model_preprocessing_scripts` (
  `model_id` int NOT NULL,
  `preprocessing_script_id` int NOT NULL,
  PRIMARY KEY (`model_id`),
  UNIQUE KEY `model_id_UNIQUE` (`model_id`),
  KEY `model_preprocessing_preprocessing_script_id_idx` (`preprocessing_script_id`),
  CONSTRAINT `model_preprocessing_model_id` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `model_preprocessing_preprocessing_script_id` FOREIGN KEY (`preprocessing_script_id`) REFERENCES `preprocessing_scripts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `models` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(100) NOT NULL,
  `model_description` varchar(100) NOT NULL DEFAULT 'No Descrption Provided',
  `model_data` mediumblob,
  `user_id` int NOT NULL,
  `selected` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `model_name_UNIQUE` (`model_name`),
  KEY `models_user_id_idx` (`user_id`),
  CONSTRAINT `models_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `models_training_scripts` (
  `model_id` int NOT NULL,
  `training_script_id` int NOT NULL,
  PRIMARY KEY (`model_id`),
  UNIQUE KEY `model_id_UNIQUE` (`model_id`),
  KEY `model_training_script_training_script_id_idx` (`training_script_id`),
  CONSTRAINT `model_training_script_model_id` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `model_training_script_training_script_id` FOREIGN KEY (`training_script_id`) REFERENCES `training_scripts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `password_resets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `reset_token` varchar(255) NOT NULL,
  `expiration_time` datetime NOT NULL,
  `hashed_token` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `password_resets_user_id_idx` (`user_id`),
  CONSTRAINT `password_resets_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `pending_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_order_id` varchar(100) NOT NULL,
  `user_id` int NOT NULL,
  `side` varchar(10) NOT NULL,
  `purchase_string` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pending_orders_user_id_idx` (`user_id`),
  CONSTRAINT `pending_orders_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `preprocessing_scripts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `script_name` varchar(45) NOT NULL,
  `script_description` varchar(100) NOT NULL,
  `script_data` blob NOT NULL,
  `upload_date` datetime NOT NULL,
  `user_id` int NOT NULL,
  `preprocessed_data` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `script_name_UNIQUE` (`script_name`),
  KEY `preprocessing_scripts_user_id_idx` (`user_id`),
  CONSTRAINT `preprocessing_scripts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `progression_texts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `progression_text` varchar(150) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  CONSTRAINT `progtext_userid` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recommendations_scripts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(100) NOT NULL,
  `script` mediumblob NOT NULL,
  `user_id` int NOT NULL,
  `updated` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `recommender_user_id_idx` (`user_id`),
  CONSTRAINT `recommender_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recommended` (
  `id` int NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) NOT NULL,
  `price` float NOT NULL,
  `confidence` int NOT NULL,
  `user_id` int NOT NULL,
  `sector` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recommended_user_id_idx` (`user_id`),
  CONSTRAINT `recommended_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=867 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recommender_progress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `progress` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `progress_user_id_idx` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `trade_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `min_price` float DEFAULT NULL,
  `max_price` float DEFAULT NULL,
  `risk_tolerance` enum('low','medium','high') DEFAULT NULL,
  `confidence_threshold` int DEFAULT NULL,
  `min_total` float NOT NULL,
  `max_total` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trade_settings_user_id_idx` (`user_id`),
  CONSTRAINT `trade_settings_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `training_scripts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_type` varchar(100) NOT NULL,
  `script_name` varchar(100) NOT NULL,
  `script_description` varchar(100) NOT NULL,
  `script_data` blob NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `script_name_UNIQUE` (`script_name`),
  KEY `training_scripts_user_id_idx` (`user_id`),
  CONSTRAINT `training_scripts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) NOT NULL,
  `dp` date NOT NULL,
  `ppps` float NOT NULL,
  `qty` int NOT NULL,
  `total_buy` float NOT NULL,
  `pstring` varchar(200) NOT NULL,
  `ds` date DEFAULT NULL,
  `spps` float DEFAULT NULL,
  `tsp` float DEFAULT NULL,
  `sstring` varchar(200) DEFAULT NULL,
  `expected` float NOT NULL,
  `proi` float DEFAULT NULL,
  `actual` float DEFAULT NULL,
  `tp1` float NOT NULL,
  `sop` float NOT NULL,
  `confidence` int NOT NULL,
  `result` enum('profit','loss') DEFAULT NULL,
  `user_id` int NOT NULL,
  `sector` varchar(100) NOT NULL,
  `processed` tinyint NOT NULL DEFAULT '0',
  `pol_neu_open` int NOT NULL,
  `pol_pos_open` int NOT NULL,
  `pol_neg_open` int NOT NULL,
  `sa_neu_open` int NOT NULL,
  `sa_pos_open` int NOT NULL,
  `sa_neg_open` int NOT NULL,
  `pol_neu_close` int DEFAULT NULL,
  `pol_pos_close` int DEFAULT NULL,
  `pol_neg_close` int DEFAULT NULL,
  `sa_neu_close` int DEFAULT NULL,
  `sa_pos_close` int DEFAULT NULL,
  `sa_neg_close` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `transactions_user_id_idx` (`user_id`),
  CONSTRAINT `transactions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `user_roles` (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `user_role_role_id_idx` (`role_id`),
  CONSTRAINT `user_role_role_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `user_role_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first` varchar(50) NOT NULL,
  `last` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `user_name` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `alpaca_key` varchar(255) NOT NULL,
  `alpaca_secret` varchar(255) NOT NULL,
  `alpaca_endpoint` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_name_UNIQUE` (`user_name`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
