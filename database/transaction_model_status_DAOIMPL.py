from database import database_connection_utility as dcu
import logging


# CREATE TABLE transaction_model_status (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     transaction_id INT NOT NULL,         
#     model_name VARCHAR(255) NOT NULL,    
#     user_id INT NOT NULL,                
#     processed BOOLEAN NOT NULL DEFAULT 0, 
#     UNIQUE KEY (transaction_id, model_name, user_id),
#     FOREIGN KEY (transaction_id) REFERENCES (transactions.id),
#     FOREIGN KEY (user_id) REFERENCES (users.id)
# );


def check_all_models_processed(transaction_id, user_id, required_models):
    """
    Checks if all required models have processed a given transaction for a user.

    Args:
        transaction_id (int): The transaction ID to check.
        user_id (int): The ID of the user who owns the transaction.
        required_models (list): A list of model names that need to process the transaction.

    Returns:
        bool: True if all required models have processed the transaction, False otherwise.
    """
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    # Query to check the status of the transaction for all required models
    sql = """
    SELECT model_name, processed
    FROM transaction_model_status
    WHERE transaction_id = %s AND user_id = %s;
    """
    vals = [transaction_id, user_id]

    try:
        cur.execute(sql, vals)
        results = cur.fetchall()

        if not results:
            # No models have processed this transaction yet
            return False

        # Map results to a dictionary for easy lookup
        processed_models = {row[0]: row[1] for row in results}

        # Check if all required models have processed
        for model in required_models:
            if processed_models.get(model) != 1:  # Model not processed or missing
                return False

        return True
    except Exception as e:
        logging.error(f"Unable to check if all models {required_models} have processed "
                      f"transaction {transaction_id} for user {user_id} due to: {e}")
        return False  # Default to False in case of error
    finally:
        try:
            cur.close()
        except Exception as e:
            logging.warning(f"Error closing cursor: {e}")

        try:
            conn.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")

def mark_transaction_processed(transaction_id, model_name, user_id):
    """
    Mark a transaction as processed by a specific model for a given user.

    Args:
        transaction_id (int): The transaction ID.
        model_name (str): The name of the model that processed the transaction.
        user_id (int): The user ID.

    Returns:
        None
    """
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = """
    UPDATE transaction_model_status SET
    processed = 1
    WHERE transaction_id = %s
    AND model_name = %s
    AND user_id = %s
    """
    vals = [transaction_id, model_name, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
    except Exception as e:
        logging.error(f'Unable to insert ({transaction_id, model_name}) to transaction model status for user {user_id} due to {e}')
        return None
    finally:
        try:
            cur.close()
        except Exception as e:
            logging.warning(f"Error closing cursor: {e}")

        try:
            conn.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")

def get_transactions_needing_processing(user_id, required_models):
    """
    Retrieves transactions that have not been processed by all required models for a given user.

    Args:
        user_id (int): The ID of the user whose transactions are being checked.
        required_models (list): A list of model names that need to process the transactions.

    Returns:
        list: A list of transaction IDs that still need processing by some models.
    """
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    
    # Construct a query to fetch transactions missing required model processing
    sql = f"""
        SELECT t.*
        FROM transactions t
        LEFT JOIN transaction_model_status ms
        ON t.id = ms.transaction_id
        AND ms.user_id = t.user_id
        AND ms.model_name IN ({','.join(['%s'] * len(required_models))})
        WHERE t.user_id = %s
        AND t.processed = 0
        AND (ms.processed IS NULL OR ms.processed = 0);
        )
    """
    if isinstance(required_models, tuple):
        required_models = list(required_models)
    vals = [user_id] + required_models

    try:
        cur.execute(sql, vals)
        results = cur.fetchall()
        if results:
        # Extract transaction IDs from the query results
            return results
        return None
    except Exception as e:
        logging.error(f"Unable to fetch transactions needing processing for user {user_id} due to: {e}")
        return []
    finally:
        try:
            cur.close()
        except Exception as e:
            logging.warning(f"Error closing cursor: {e}")

        try:
            conn.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")

def insert_transaction_model_status_entries_for_all_unprocessed_by_this_model(new_model_name, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    add_model_sql = """
        INSERT INTO transaction_model_status (transaction_id, user_id, model_name, processed)
        SELECT t.id, t.user_id, %s AS model_name, 0 AS processed
        FROM transactions t
        WHERE t.user_id = %s
        ON DUPLICATE KEY UPDATE processed = VALUES(processed)
    """
    vals = [new_model_name, user_id]
    try:
        cur.execute(add_model_sql, vals)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding the new model: {e}")
    finally:
        cur.close()
        conn.close()

def insert_transaction_model_status_entries_for_all_processed_by_this_model(new_model_name, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    add_model_sql = """
        INSERT INTO transaction_model_status (transaction_id, user_id, model_name, processed)
        SELECT t.id, t.user_id, %s AS model_name, 1 AS processed
        FROM transactions t
        WHERE t.user_id = %s
        ON DUPLICATE KEY UPDATE processed = VALUES(processed)
    """
    vals = [new_model_name, user_id]
    try:
        cur.execute(add_model_sql, vals)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while adding the new model: {e}")
    finally:
        cur.close()
        conn.close()
        
def reselect_model_actions(model_name, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    try:
        # Step 1: Get all transaction IDs from the transactions table for the user
        get_transactions_sql = """
            SELECT id
            FROM transactions
            WHERE user_id = %s;
        """
        vals =[user_id]
        cur.execute(get_transactions_sql, vals)
        transaction_ids = {row[0] for row in cur.fetchall()}  # Use a set for easy comparison

        # Step 2: Get all processed transaction IDs for the model where processed = 1
        get_processed_sql = """
            SELECT transaction_id
            FROM transaction_model_status
            WHERE user_id = %s
            AND model_name = %s
            AND processed = 1;
        """
        vals = [user_id, model_name]
        cur.execute(get_processed_sql,vals)
        processed_ids = {row[0] for row in cur.fetchall()}  # Use a set for easy comparison
        
        # Step 4: Get all processed transaction IDs for the model where processed = 1
        get_unprocessed_sql = """
            SELECT transaction_id
            FROM transaction_model_status
            WHERE user_id = %s
            AND model_name = %s
            AND processed = 0;
        """
        vals = [user_id,model_name]
        cur.execute(get_unprocessed_sql, vals)
        tms_transaction_ids = {row[0] for row in cur.fetchall()}  # Use a set for easy comparison

        # Step 5: Find unprocessed transaction IDs (difference between transaction_ids and processed_ids)
        trans_table_unprocessed_ids = transaction_ids - processed_ids
        not_present_unprocessed_ids = trans_table_unprocessed_ids - tms_transaction_ids

        # Step 6: Insert missing entries as unprocessed (processed = 0) for the current model
        if not_present_unprocessed_ids:
            add_missing_sql = """
                INSERT INTO transaction_model_status (transaction_id, user_id, model_name, processed)
                VALUES (%s, %s, %s, 0);
            """
            for transaction_id in not_present_unprocessed_ids:
                cur.execute(add_missing_sql, (transaction_id, user_id, model_name))

        conn.commit()
        print(f"Successfully updated transaction_model_status for model '{model_name}'.")
    except Exception as e:
        print(f"Error reselecting model: {e}")
    finally:
        cur.close()
        conn.close()

def delete_specific_model_entries_for_user(model_name, user_id):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    sql = '''
            DELETE FROM transaction_model_status
            WHERE model_name = %s
            AND user_id = %s
        '''
    vals = [model_name, user_id]
    try:
        cur.execute(sql, vals)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while deleting models entries for model {model_name} and user {user_id}: {e}")
    finally:
        cur.close()
        conn.close()


def get_transaction_ids_unprocessed_for_user(user_id, model_name):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    get_unprocessed_sql = """
            SELECT transaction_id
            FROM transaction_model_status
            WHERE user_id = %s
            AND model_name = %s
            AND processed = 0;
        """
    vals = [user_id, model_name]
    try:
        cur.execute(get_unprocessed_sql, vals)
        results = cur.fetchall()
        if results:
        # Extract transaction IDs from the query results
            return results
        return None
    except Exception as e:
        logging.error(f"Unable to fetch transactions needing processing for user {user_id} due to: {e}")
        return []
    finally:
        try:
            cur.close()
        except Exception as e:
            logging.warning(f"Error closing cursor: {e}")

        try:
            conn.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")


def get_transaction_ids_unprocessed_for_user_by_model_and_uprocessed_in_transactions(user_id, model_name, required_models):
    conn = dcu.get_db_connection()
    cur = conn.cursor()
    get_unprocessed_sql = f"""
            SELECT * 
            FROM transactions as t
            LEFT JOIN transaction_model_status as tms
            ON t.id = tms.transaction_id
            WHERE tms.user_id = %s
            AND tms.model_name = %s
            AND tms.model_name IN ({','.join(['%s'] * len(required_models))})
            AND tms.processed = 0
            AND t.processed = 0;
        """
    vals = [user_id, model_name] + required_models
    try:
        cur.execute(get_unprocessed_sql, vals)
        results = cur.fetchall()
        if results:
        # Extract transaction IDs from the query results
            return results
        return None
    except Exception as e:
        logging.error(f"Unable to fetch transactions needing processing for user {user_id} due to: {e}")
        return []
    finally:
        try:
            cur.close()
        except Exception as e:
            logging.warning(f"Error closing cursor: {e}")

        try:
            conn.close()
        except Exception as e:
            logging.warning(f"Error closing connection: {e}")