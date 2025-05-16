class IntegrationGenerationError(Exception):
    """Exception, which raises during generation using integrations"""

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail
