import json

class ConfigLoader:
    def __init__(self, config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            self._config = json.load(f)

    def get_rename_dict(self):
        rename_dict = {
            old_name: new_name
            for new_name, info in self._config.items()
            for old_name in (info["raw_name"] if isinstance(info["raw_name"], list) else [info["raw_name"]])
        }
        return rename_dict

    def get_dtype_dict(self):
        dtype_dict = {
            col: info["dtype"]
            for col, info in self._config.items()
        }
        return dtype_dict