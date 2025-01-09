from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    app_name: str = "API"
    environment: str = "development"
    db_name: str 
    db_user: str 
    db_password: str 
    db_host: str 
    db_port: int = 3306
    aws_access_key: str
    aws_secret_key: str
    s3_bucket: str
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
