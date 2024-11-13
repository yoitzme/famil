import os
import zipfile
import tempfile
from datetime import datetime
from utils.database import get_db_connection
import shutil

def get_all_tables():
    """Get all tables from the database."""
    conn = get_db_connection()
    tables = []
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                """)
                tables = [row[0] for row in cur.fetchall()]
        finally:
            conn.close()
    return tables

def create_backup():
    """Create a backup of the database and settings."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    backup_filename = f"family_hub_backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Create backups directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Clean up old backups (keep last 5)
    existing_backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.zip')])
    while len(existing_backups) >= 5:
        os.remove(os.path.join(backup_dir, existing_backups.pop(0)))
    
    # Create temporary directory for backup files
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Backup database
            backup_database(temp_dir)
            
            # Backup settings
            backup_settings(temp_dir)
            
            # Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            return backup_path
        except Exception as e:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise Exception(f"Backup failed: {str(e)}")

def restore_backup(backup_file):
    """Restore from a backup file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restore database
            restore_database(temp_dir)
            
            # Restore settings
            restore_settings(temp_dir)
            
            return True
        except Exception as e:
            raise Exception(f"Restore failed: {str(e)}")
        finally:
            # Clean up temp files
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

def backup_database(temp_dir):
    """Backup database to SQL file."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Get all tables
                tables = get_all_tables()
                
                # Create schema file
                schema_file = os.path.join(temp_dir, "schema.sql")
                with open(schema_file, 'w') as f:
                    for table in tables:
                        # Get table schema including constraints and indexes
                        cur.execute(f"""
                            SELECT 
                                column_name, 
                                data_type, 
                                character_maximum_length,
                                column_default,
                                is_nullable
                            FROM information_schema.columns
                            WHERE table_name = '{table}'
                            ORDER BY ordinal_position
                        """)
                        columns = cur.fetchall()
                        
                        # Get primary key info
                        cur.execute(f"""
                            SELECT c.column_name
                            FROM information_schema.table_constraints tc
                            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
                            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                                AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                            WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table}';
                        """)
                        primary_keys = [pk[0] for pk in cur.fetchall()]
                        
                        # Write CREATE TABLE statement
                        f.write(f"-- Table: {table}\n")
                        f.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")
                        
                        # Write columns
                        column_defs = []
                        for col in columns:
                            col_name = col[0]
                            col_type = col[1]
                            col_length = col[2]
                            col_default = col[3]
                            col_nullable = col[4]
                            
                            col_def = f"    {col_name} {col_type}"
                            if col_length:
                                col_def += f"({col_length})"
                            if col_default:
                                col_def += f" DEFAULT {col_default}"
                            if col_nullable == 'NO':
                                col_def += " NOT NULL"
                            column_defs.append(col_def)
                        
                        # Add primary key constraint if exists
                        if primary_keys:
                            column_defs.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")
                        
                        f.write(',\n'.join(column_defs))
                        f.write("\n);\n\n")
                
                # Backup data
                for table in tables:
                    backup_file = os.path.join(temp_dir, f"{table}.sql")
                    with open(backup_file, 'w') as f:
                        cur.copy_expert(f"COPY {table} TO STDOUT", f)
        finally:
            conn.close()

def restore_database(temp_dir):
    """Restore database from SQL file."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # First, drop all existing tables
                cur.execute("""
                    DO $$ 
                    DECLARE 
                        r RECORD;
                    BEGIN
                        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                        END LOOP;
                    END $$;
                """)
                conn.commit()  # Commit the drops
                
                # Recreate schema first
                schema_file = os.path.join(temp_dir, "schema.sql")
                if os.path.exists(schema_file):
                    with open(schema_file, 'r') as f:
                        schema_sql = f.read()
                        # Split and execute each CREATE TABLE statement separately
                        for statement in schema_sql.split(';'):
                            if statement.strip():
                                cur.execute(statement + ';')
                    conn.commit()  # Commit the schema changes
                
                # Now restore data
                tables = get_all_tables()
                for table in tables:
                    backup_file = os.path.join(temp_dir, f"{table}.sql")
                    if os.path.exists(backup_file):
                        with open(backup_file, 'r') as f:
                            try:
                                cur.copy_expert(f"COPY {table} FROM STDIN", f)
                            except Exception as e:
                                raise Exception(f"Error restoring data for table {table}: {str(e)}")
                conn.commit()  # Commit the data
        except Exception as e:
            conn.rollback()  # Rollback on error
            raise Exception(f"Database restore failed: {str(e)}")
        finally:
            conn.close()

def backup_settings(temp_dir):
    """Backup settings files."""
    settings_dir = "config"
    if os.path.exists(settings_dir):
        settings_backup_dir = os.path.join(temp_dir, "config")
        os.makedirs(settings_backup_dir, exist_ok=True)
        for item in os.listdir(settings_dir):
            s = os.path.join(settings_dir, item)
            d = os.path.join(settings_backup_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)

def restore_settings(temp_dir):
    """Restore settings files."""
    settings_backup_dir = os.path.join(temp_dir, "config")
    if os.path.exists(settings_backup_dir):
        settings_dir = "config"
        # Clear existing settings
        if os.path.exists(settings_dir):
            shutil.rmtree(settings_dir)
        # Restore settings
        shutil.copytree(settings_backup_dir, settings_dir) 