#!/usr/bin/env python3
"""
Database module for persistent storage of agent data and communications
Uses Supabase PostgreSQL with secure credential management
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

try:
    from .credential_manager import CredentialManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.credential_manager import CredentialManager

logger = logging.getLogger(__name__)

class SupabaseDatabaseManager:
    """Manages persistent storage using Supabase PostgreSQL"""
    
    def __init__(self):
        # Initialize credential manager
        self.cred_manager = CredentialManager()
        
        # Get database URL from keyring or environment
        self.db_url = self._get_database_url()
        if not self.db_url:
            raise ValueError("No Supabase database credentials found. Please run credential setup.")
        
        # Create connection pool
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 10, self.db_url)
        self._init_database()
    
    def _get_database_url(self) -> Optional[str]:
        """Get database URL from keyring or environment"""
        # First try keyring
        url = self.cred_manager.get_supabase_url()
        if url:
            logger.info("✅ Using Supabase credentials from keyring")
            return url
        
        # Fallback to environment variable
        url = os.getenv('SUPABASE_DB_URL')
        if url:
            logger.info("✅ Using Supabase credentials from environment")
            return url
        
        logger.warning("⚠️ No Supabase credentials found in keyring or environment")
        return None
    
    def _get_connection(self):
        """Get a connection from the pool"""
        return self.pool.getconn()
    
    def _return_connection(self, conn):
        """Return a connection to the pool"""
        self.pool.putconn(conn)
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    capabilities JSONB,
                    status VARCHAR(50) DEFAULT 'offline',
                    last_heartbeat TIMESTAMP,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Communications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communications (
                    id VARCHAR(255) PRIMARY KEY,
                    from_agent VARCHAR(255) NOT NULL,
                    to_agent VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    message_type VARCHAR(50) DEFAULT 'direct',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # System stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id SERIAL PRIMARY KEY,
                    total_communications INTEGER DEFAULT 0,
                    active_agents INTEGER DEFAULT 0,
                    api_calls INTEGER DEFAULT 0,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert initial system stats if not exists
            cursor.execute('SELECT COUNT(*) FROM system_stats')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO system_stats (total_communications, active_agents, api_calls)
                    VALUES (0, 0, 0)
                ''')
            
            conn.commit()
            logger.info("Supabase database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize database: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def register_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Register or update an agent"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agents 
                (id, name, description, capabilities, status, last_heartbeat, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    capabilities = EXCLUDED.capabilities,
                    status = EXCLUDED.status,
                    last_heartbeat = EXCLUDED.last_heartbeat,
                    updated_at = EXCLUDED.updated_at
            ''', (
                agent_data['id'],
                agent_data['name'],
                agent_data.get('description', ''),
                json.dumps(agent_data.get('capabilities', [])),
                'online',
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"Agent {agent_data['id']} registered/updated in Supabase")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to register agent: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def update_agent_heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat timestamp"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agents 
                SET last_heartbeat = %s, status = 'online', updated_at = %s
                WHERE id = %s
            ''', (datetime.now(), datetime.now(), agent_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM agents ORDER BY registered_at')
            rows = cursor.fetchall()
            
            agents = []
            for row in rows:
                agent = dict(row)
                # Parse capabilities JSON
                try:
                    agent['capabilities'] = json.loads(agent['capabilities']) if agent['capabilities'] else []
                except (json.JSONDecodeError, TypeError):
                    agent['capabilities'] = []
                
                # Convert timestamps to ISO format
                for field in ['last_heartbeat', 'registered_at', 'updated_at']:
                    if agent[field]:
                        agent[field] = agent[field].isoformat()
                
                agents.append(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def add_communication(self, comm_data: Dict[str, Any]) -> bool:
        """Add a communication to the log"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO communications 
                (id, from_agent, to_agent, message, message_type, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                comm_data['id'],
                comm_data['from_agent'],
                comm_data['to_agent'],
                comm_data['message'],
                comm_data.get('type', 'direct'),
                comm_data['timestamp']
            ))
            
            conn.commit()
            logger.info(f"Communication {comm_data['id']} added to Supabase")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to add communication: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_communications(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get communications from the log"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = 'SELECT * FROM communications ORDER BY timestamp DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            communications = []
            for row in rows:
                comm = dict(row)
                # Convert timestamp to ISO format
                if comm['timestamp']:
                    comm['timestamp'] = comm['timestamp'].isoformat()
                communications.append(comm)
            
            return communications
            
        except Exception as e:
            logger.error(f"Failed to get communications: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def update_system_stats(self, stats: Dict[str, Any]) -> bool:
        """Update system statistics"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE system_stats 
                SET total_communications = %s, active_agents = %s, api_calls = %s, last_update = %s
                WHERE id = 1
            ''', (
                stats.get('total_communications', 0),
                stats.get('active_agents', 0),
                stats.get('api_calls', 0),
                datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update system stats: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute('SELECT * FROM system_stats WHERE id = 1')
            row = cursor.fetchone()
            
            if row:
                stats = dict(row)
                # Convert timestamp to ISO format
                if stats['last_update']:
                    stats['last_update'] = stats['last_update'].isoformat()
                return stats
            else:
                return {
                    'total_communications': 0,
                    'active_agents': 0,
                    'api_calls': 0,
                    'last_update': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                'total_communications': 0,
                'active_agents': 0,
                'api_calls': 0,
                'last_update': datetime.now().isoformat()
            }
        finally:
            self._return_connection(conn)
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old communications and offline agents"""
        conn = self._get_connection()
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cursor = conn.cursor()
            
            # Remove old communications
            cursor.execute('''
                DELETE FROM communications 
                WHERE timestamp < %s
            ''', (cutoff_date,))
            
            comms_deleted = cursor.rowcount
            
            # Mark agents as offline if no heartbeat for 5 minutes
            offline_cutoff = datetime.now() - timedelta(minutes=5)
            cursor.execute('''
                UPDATE agents 
                SET status = 'offline' 
                WHERE last_heartbeat < %s AND status = 'online'
            ''', (offline_cutoff,))
            
            agents_offline = cursor.rowcount
            
            conn.commit()
            
            if comms_deleted > 0 or agents_offline > 0:
                logger.info(f"Cleanup: {comms_deleted} old communications deleted, {agents_offline} agents marked offline")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to cleanup old data: {e}")
        finally:
            self._return_connection(conn)
