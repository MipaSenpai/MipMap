from endstone.plugin import Plugin


class Map(Plugin):
    api_version = "0.10"

    def on_load(self) -> None:
        self.logger.info("on_load is called!")

    def on_enable(self) -> None:
        self.logger.info("on_enable is called!")

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")