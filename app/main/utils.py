from config.models import Config


def get_config(name, default=None):
    conf = Config.objects.filter(name=name).first()
    if conf is None:
        return default
    else:
        return conf.value
