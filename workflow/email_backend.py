import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class CustomSMTPEmailBackend(SMTPEmailBackend):
    """
    Custom SMTP email backend that handles self-signed certificates
    by using a custom SSL context that doesn't verify certificates.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create SSL context that doesn't verify certificates
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE
    
    @property
    def ssl_context(self):
        """Override the ssl_context property to use our custom context"""
        return self._ssl_context 