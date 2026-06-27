class ApprovalChain:
    def __init__(self, approvers):
        if not approvers:
            raise ValueError("at least one approver required")
        self.approvers = list(approvers)
        self.index = 0
        self.state = "PENDING"
        self.events: list = []

    def approve(self, who: str) -> None:
        raise NotImplementedError("implement approve per DOMAIN.md")

    def reject(self, who: str) -> None:
        raise NotImplementedError("implement reject per DOMAIN.md")
