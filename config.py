class Config:
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False


app_config = {
    'dev': DevelopmentConfig,
    'prd': ProductionConfig
}
