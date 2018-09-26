import pkgutil

__all__ = []
job_list = []
for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)

    try:
        job_list.append(getattr(module, "job"))
    except AttributeError:
        continue

    globals()[module_name] = module
    __all__.append(module_name)
