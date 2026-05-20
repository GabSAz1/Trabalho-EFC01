class NotificationService:
    def send_email(self, client: str, message: str) -> None:
        print(f"Email enviado para {client}: {message}")

    def send_sms(self, client: str, message: str) -> None:
        print(f"SMS enviado para {client}: {message}")

    def notify_manager(self, client: str) -> None:
        print(f"Notificacao enviada ao gerente de conta de {client}")