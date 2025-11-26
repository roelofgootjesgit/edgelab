"""
config.py
=========

Environment-based configuration for EdgeLab.

Enables different settings per environment:
- Development: Local Parquet files
- Production: Cloud storage (S3 + PostgreSQL)
- Enterprise: Distributed multi-region

Usage:
    from config import Config
    
    storage_config = Config.get_storage_config()
    # Returns appropriate config based on STORAGE_TYPE env var

Environment Variables:
    STORAGE_TYPE    - 'local' (default) or 'cloud'
    DATA_PATH       - Local storage path (default: data/market_cache)
    CACHE_TTL_HOURS - Hours before cache refresh (default: 24)
    
    # Cloud-only (when STORAGE_TYPE=cloud):
    S3_BUCKET       - S3 bucket name
    PG_HOST         - PostgreSQL host
    PG_DATABASE     - PostgreSQL database name
    PG_USER         - PostgreSQL user
    PG_PASSWORD     - PostgreSQL password
    REDIS_URL       - Redis connection URL

Author: EdgeLab Development
Version: 1.0
"""

import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """
    Central configuration management.
    
    All settings loaded from environment variables with sensible defaults.
    This allows same codebase to run in any environment.
    """
    
    # ===================
    # Storage Settings
    # ===================
    
    # Storage backend: 'local' or 'cloud'
    STORAGE_TYPE: str = os.getenv('STORAGE_TYPE', 'local')
    
    # Local storage path (relative to project root)
    DATA_PATH: str = os.getenv('DATA_PATH', 'data/market_cache')
    
    # Cache time-to-live in hours
    CACHE_TTL_HOURS: int = int(os.getenv('CACHE_TTL_HOURS', '24'))
    
    # Maximum cache size in GB (for cleanup decisions)
    MAX_CACHE_SIZE_GB: int = int(os.getenv('MAX_CACHE_SIZE_GB', '50'))
    
    # ===================
    # Cloud Settings
    # ===================
    
    # S3 bucket for market data
    S3_BUCKET: str = os.getenv('S3_BUCKET', '')
    
    # PostgreSQL connection
    PG_HOST: str = os.getenv('PG_HOST', '')
    PG_DATABASE: str = os.getenv('PG_DATABASE', '')
    PG_USER: str = os.getenv('PG_USER', '')
    PG_PASSWORD: str = os.getenv('PG_PASSWORD', '')
    PG_PORT: int = int(os.getenv('PG_PORT', '5432'))
    
    # Redis cache
    REDIS_URL: str = os.getenv('REDIS_URL', '')
    
    # ===================
    # Application Settings
    # ===================
    
    # Flask settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Yahoo Finance settings
    YAHOO_RATE_LIMIT_DELAY: float = float(os.getenv('YAHOO_RATE_LIMIT_DELAY', '0.5'))
    
    # Anthropic API (for AI narratives)
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """
        Get storage configuration based on STORAGE_TYPE.
        
        Returns:
            Dictionary with all storage-related settings.
            Backend-specific keys included only when relevant.
        """
        config = {
            'storage_type': cls.STORAGE_TYPE,
            'base_path': cls.DATA_PATH,
            'cache_ttl_hours': cls.CACHE_TTL_HOURS,
            'max_cache_size_gb': cls.MAX_CACHE_SIZE_GB
        }
        
        # Add cloud config only if cloud storage selected
        if cls.STORAGE_TYPE == 'cloud':
            config.update({
                's3_bucket': cls.S3_BUCKET,
                'pg_host': cls.PG_HOST,
                'pg_database': cls.PG_DATABASE,
                'pg_user': cls.PG_USER,
                'pg_password': cls.PG_PASSWORD,
                'pg_port': cls.PG_PORT,
                'redis_url': cls.REDIS_URL
            })
        
        return config
    
    @classmethod
    def validate(cls) -> Dict[str, list]:
        """
        Validate configuration for current environment.
        
        Returns:
            Dictionary with 'errors' and 'warnings' lists.
            Empty lists mean configuration is valid.
        """
        errors = []
        warnings = []
        
        # Check storage type is valid
        if cls.STORAGE_TYPE not in ('local', 'cloud'):
            errors.append(f"Invalid STORAGE_TYPE: {cls.STORAGE_TYPE}. Must be 'local' or 'cloud'.")
        
        # Local storage validation
        if cls.STORAGE_TYPE == 'local':
            data_path = Path(cls.DATA_PATH)
            if not data_path.parent.exists():
                warnings.append(f"DATA_PATH parent directory does not exist: {data_path.parent}")
        
        # Cloud storage validation
        if cls.STORAGE_TYPE == 'cloud':
            if not cls.S3_BUCKET:
                errors.append("S3_BUCKET required for cloud storage")
            if not cls.PG_HOST:
                errors.append("PG_HOST required for cloud storage")
            if not cls.PG_DATABASE:
                errors.append("PG_DATABASE required for cloud storage")
            if not cls.PG_USER:
                errors.append("PG_USER required for cloud storage")
            if not cls.PG_PASSWORD:
                errors.append("PG_PASSWORD required for cloud storage")
        
        # General warnings
        if cls.SECRET_KEY == 'dev-secret-change-in-production':
            warnings.append("Using default SECRET_KEY. Set in production!")
        
        if not cls.ANTHROPIC_API_KEY:
            warnings.append("ANTHROPIC_API_KEY not set. AI narratives will be disabled.")
        
        return {'errors': errors, 'warnings': warnings}
    
    @classmethod
    def print_config(cls, hide_secrets: bool = True) -> None:
        """
        Print current configuration for debugging.
        
        Args:
            hide_secrets: If True, mask sensitive values
        """
        print("EdgeLab Configuration")
        print("=" * 40)
        print(f"STORAGE_TYPE:      {cls.STORAGE_TYPE}")
        print(f"DATA_PATH:         {cls.DATA_PATH}")
        print(f"CACHE_TTL_HOURS:   {cls.CACHE_TTL_HOURS}")
        print(f"MAX_CACHE_SIZE_GB: {cls.MAX_CACHE_SIZE_GB}")
        print(f"DEBUG:             {cls.DEBUG}")
        
        if cls.STORAGE_TYPE == 'cloud':
            print()
            print("Cloud Settings:")
            print(f"  S3_BUCKET:    {cls.S3_BUCKET}")
            print(f"  PG_HOST:      {cls.PG_HOST}")
            print(f"  PG_DATABASE:  {cls.PG_DATABASE}")
            print(f"  PG_USER:      {cls.PG_USER}")
            print(f"  PG_PASSWORD:  {'*****' if hide_secrets else cls.PG_PASSWORD}")
            print(f"  REDIS_URL:    {cls.REDIS_URL or 'Not configured'}")
        
        # Validation status
        validation = cls.validate()
        if validation['errors']:
            print()
            print("ERRORS:")
            for error in validation['errors']:
                print(f"  - {error}")
        if validation['warnings']:
            print()
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")


def get_storage_backend():
    """
    Factory function to get appropriate storage backend.
    
    Returns:
        DataStorage implementation based on config.
    
    Usage:
        from config import get_storage_backend
        storage = get_storage_backend()
        data = storage.get_data('XAUUSD', '15m', start, end)
    """
    from core.storage_interface import DataStorage
    
    config = Config.get_storage_config()
    storage_type = config['storage_type']
    
    if storage_type == 'local':
        from core.local_storage import LocalStorage
        return LocalStorage(config['base_path'])
    
    elif storage_type == 'cloud':
        from core.cloud_storage import CloudStorage
        return CloudStorage(config)
    
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")