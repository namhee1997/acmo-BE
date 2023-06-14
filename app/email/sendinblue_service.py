import sib_api_v3_sdk
from typing import Optional, Dict, Any, List, Union
from sib_api_v3_sdk.rest import ApiException
from pydantic import EmailStr
import textwrap
from app.config import config


class SendinblueService:
    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = config['SENDINBLUE_API_KEY']
        self.api = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        self.contact = sib_api_v3_sdk.ContactsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    def _send(
        self,
        emails_to: Union[List[str], str],
        sender: Optional[EmailStr] = None,
        text_content: Optional[str] = None,
        subject: Optional[str] = None,
        name: Optional[str] = None,
    ):
        try:
            if isinstance(emails_to, str):
                emails_to = [emails_to]

            if len(emails_to) == 0:
                raise Exception("Must have email to")
            email_sender = config['EMAIL_SENDER']
            # we can get sender from template id
            if sender:
                email_sender = sib_api_v3_sdk.SendSmtpEmailSender(
                    email=sender, name=name
                )
            to = [sib_api_v3_sdk.SendSmtpEmailTo(email=to) for to in emails_to]
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                sender=email_sender,
                to=to,
                text_content=text_content,
                subject=subject,
                html_content='content'
            )
            api_response = self.api.send_transac_email(send_smtp_email)
            return api_response
        except ApiException as ex:
            return ex

    def get_template(self, domain: Optional[str] = None):
        return ""

    def send_register_email(self, mail_to: EmailStr, password: str) -> Any:
        try:
            data = dict(password=password, url=config['HOSTING_URL'])
            resp = self._send(emails_to=[mail_to], template_id=1, params=data)
            return resp
        except Exception as ex:
            raise ex

    def send_forgot_email(self, mail_to: EmailStr, password: str) -> Any:
        try:
            data = dict(password=password, url=config['HOSTING_URL'])
            resp = self._send(emails_to=[mail_to], template_id=1, params=data)
            return resp
        except Exception as ex:
            raise ex

    def send_new_order_created_email(
        self, sender: str, brand_type: str, data: dict, domain: str = None
    ) -> Any:
        try:
            subject = None
            if "localhost" in domain or "test." in domain or "staging." in domain:
                subject = f"{domain}: {brand_type} - New Order"

            resp = self._send(
                sender=sender,
                subject=subject,
                emails_to=config['EMAIL_SENDER'],
                template_id=self.get_template(domain=domain),
                params=data,
            )
            return resp
        except Exception as ex:
            return None

    def send_welcome_email(
        self,
        sender: str,
        brand_type: str,
        email_to: str,
        data: dict,
        domain: str = None,
    ) -> Any:
        try:
            resp = self._send(
                sender=sender,
                emails_to=[email_to],
                template_id=self.get_template(domain=domain),
                params=data,
            )
            return resp
        except Exception as ex:
            return None

    def send_order_completed_email(
        self,
        sender: str,
        brand_type: str,
        email_to: str,
        subject: str,
        data: dict,
        domain: str = None,
    ) -> Any:
        try:
            resp = self._send(
                sender=sender,
                emails_to=email_to,
                subject=subject,
                template_id=self.get_template(domain=domain),
                params=data,
            )
            return resp
        except Exception as ex:
            return None

    def send_order_cancelled_email_to_team(
        self, sender: str, email_to: str, subject: str, data: dict
    ) -> Any:
        try:
            resp = self._send(
                sender=sender,
                emails_to=email_to,
                subject=subject,
                template_id=self.get_template(),
                params=data,
            )
            return resp
        except Exception as ex:
            pass

    def send_order_cancelled_email_to_customer(
        self, sender: str, email_to: str, data: dict
    ) -> Any:
        try:
            resp = self._send(
                sender=sender,
                emails_to=email_to,
                template_id=self.get_template(),
                params=data,
            )
            return resp
        except Exception as ex:
            raise ex

    def email_internal_alert(
        self,
        sender: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        subject: Optional[str] = None,
        err: Optional[str] = None,
    ) -> Any:
        try:
            from_mail = sender if sender else config['EMAIL_SENDER']
            resp = self._send(
                sender=from_mail,
                emails_to=config['EMAIL_RECEIVER'],
                subject=f"Viewpals:ERROR - {subject}"
                if from_mail == config['EMAIL_SENDER']
                else f"Streamingpals:ERROR - {subject}",
                text_content=textwrap.dedent(
                    f"""
                    PARAMS
                    {params}
                    ERROR
                    {err}
                """
                ),
            )
            return resp
        except Exception as e:
            pass

    def email_alert_internal_w_template(self, params: Optional[Dict[str, Any]] = None):
        try:
            resp = self._send(
                sender=config['EMAIL_SENDER'],
                emails_to=config['EMAIL_RECEIVER'],
                template_id=self.get_template(),
                params=params,
            )
            return resp
        except Exception as e:
            pass

    def send_confirm_payment_to_customer(
        self,
        brand_type: str,
        email_to: str,
        sender: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            from_mail = sender if sender else config['EMAIL_SENDER']
            resp = self._send(
                sender=from_mail,
                emails_to=email_to,
                template_id=self.get_template(),
                params=params,
            )
            return resp
        except Exception as e:
            pass

    def send_confirm_payment_to_team(
        self,
        total: str,
        email: str,
        create_date: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            resp = self._send(
                sender=config['EMAIL_RECEIVER'],
                emails_to=config['EMAIL_SENDER'],
                template_id=self.get_template(),
                params=dict(
                    total=total,
                    email=email,
                    create_date=create_date,
                    orders=textwrap.dedent(f"""{params}"""),
                ),
            )
            return resp
        except Exception as e:
            pass

    def create_contact(self, email):
        try:
            list_id = 4

            try:
                self.contact.get_contact_info(identifier=email)
                update_contact = sib_api_v3_sdk.UpdateContact(list_ids=[list_id])
                self.contact.update_contact(
                    identifier=email, update_contact=update_contact
                )
            except:
                _create_contact = sib_api_v3_sdk.CreateContact(
                    email=email, list_ids=[list_id]
                )
                resp = self.contact.create_contact(_create_contact)
                return resp
        except ApiException as e:
            return None

    def send_contact(
        self, email: str, subject: str, message: str, sender: str, name: str
    ):
        self._send(
            emails_to=[sender],
            sender=email,
            subject=subject,
            text_content=message,
            name=name,
        )

    def streamsocial_send_order(
        self,
        email_to: str,
        params: Dict[str, Any],
        domain: str,
    ):
        template_id = self.get_template(
            domain=domain,
        )
        self._send(
            emails_to=[email_to],
            sender=config['EMAIL_SENDER'],
            template_id=template_id,
            params=params,
        )

    def get_offer_contact_list(self, domain: str):
        return 38

    def add_offer_contact(self, email: str, domain: str):
        try:
            list_id = self.get_offer_contact_list(domain=domain)
            try:
                self.contact.get_contact_info(identifier=email)
                update_contact = sib_api_v3_sdk.UpdateContact(list_ids=[list_id])
                self.contact.update_contact(
                    identifier=email, update_contact=update_contact
                )
            except Exception as ex:
                _create_contact = sib_api_v3_sdk.CreateContact(
                    email=email, list_ids=[list_id]
                )
                self.contact.create_contact(_create_contact)
            return True
        except ApiException as e:
            return False
