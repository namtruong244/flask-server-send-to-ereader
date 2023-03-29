class Config:
    pass


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


app_config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
