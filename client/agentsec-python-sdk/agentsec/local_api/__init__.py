__all__ = ["LocalApiServer"]


def __getattr__(name):
    if name == "LocalApiServer":
        from agentsec.local_api.server import LocalApiServer

        return LocalApiServer
    raise AttributeError(name)
