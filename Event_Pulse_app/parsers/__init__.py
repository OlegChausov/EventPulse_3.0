import importlib
import pkgutil




# def collect_all_films():
#     films = []
#     package = __name__
#
#     for _, module_name, _ in pkgutil.iter_modules(__path__):
#         if module_name == "__init__":
#             continue
#
#         try:
#             module = importlib.import_module(f"{package}.{module_name}")
#             if hasattr(module, "fetch_and_parse"):
#                 result = module.fetch_and_parse()
#                 films.extend(result)
#         except Exception as e:
#             print(f"[ERROR] {module_name}: {e}")
#
#     return films


