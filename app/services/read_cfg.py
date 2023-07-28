import tomllib


def read_cfg(path: str = "config.toml") -> dict:
    """Read config file

    Args:
        path (str, optional): Read config. Defaults to "config.toml".

    Returns:
        dict: Config dict
    """
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    return data


read_cfg()