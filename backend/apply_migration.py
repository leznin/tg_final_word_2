#!/usr/bin/env python3
"""
Script to apply database migrations manually
"""

import pymysql
from pymysql import Error

def apply_migration():
    """Apply the delete_messages_enabled migration manually"""

    try:
        # Connect to database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='696578As',
            database='final',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = connection.cursor()

        # Add the delete_messages_enabled column
        alter_query = """
        ALTER TABLE chats
        ADD COLUMN delete_messages_enabled BOOLEAN NOT NULL DEFAULT FALSE
        """

        cursor.execute(alter_query)
        connection.commit()

        print("Migration applied successfully: Added delete_messages_enabled column")

    except Error as e:
        print(f"Error applying migration: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    apply_migration()
