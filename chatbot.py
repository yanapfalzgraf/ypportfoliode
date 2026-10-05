"""Contact form and floating portfolio assistant for Streamlit."""

from __future__ import annotations

import html
import re
import smtplib
from email.message import EmailMessage

import streamlit as st


_INITIAL_MESSAGE = (
    "Hallo! Ich bin Yanas Portfolio-Assistent. "
    "Ich beantworte Fragen zu ihren Projekten, ihrer Erfahrung, "
    "ihren Kompetenzen und ihrer Arbeitsweise."
)

_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def init_chat_state() -> None:
    """Initializes the contact form and chat state."""
    st.session_state.setdefault("contact_form_open", False)
    st.session_state.setdefault(
        "portfolio_chat_messages",
        [{"role": "assistant", "content": _INITIAL_MESSAGE}],
    )


def create_chat_response(question: str) -> str:
    """Creates controlled responses about the portfolio."""
    normalized = " ".join(question.lower().split())

    if any(term in normalized for term in (
        "hallo", "hello", "hi", "guten tag", "hey")):
        return (
            "Hallo! Schön, dass du hier bist. "
            "Frag mich gerne nach Yanas Erfahrung, ausgewählten Projekten, digitaler Produktentwicklung, "
            "Business Analyse, Product Ownership, Data Analytics oder Kontaktmöglichkeiten."
        )

    if any(term in normalized for term in ("projekt", "projekte", "project", "projects", "portfolio")):
        return (
            "Yanas Portfolio zeigt über 10 Jahre Erfahrung in der digitalen Produktentwicklung "
            "und verbindet UX und Product Design mit Geschäftsanforderungen, Stakeholder Management und Technologie. "
            "Ihre Projekterfahrung umfasst unter anderem Murrelektronik, OPTIMA, MeaPuna und Mercedes-Benz "
            "sowie Data-Analytics-Projekte mit Power BI, Python und Streamlit."
        )

    if any(term in normalized for term in (
        "erfahrung", "beruf", "experience", "career", "senior",
        "product", "product management", "product owner", "product ownership",
        "business analysis", "ux", "ui"
    )):
        return (
            "Yana bringt über 10 Jahre Erfahrung in der digitalen Produktentwicklung mit, "
            "mit einem starken Hintergrund in UX, Product Design sowie komplexer B2B- und Enterprise-Software. "
            "Sie verbindet Nutzer- und Geschäftsbedürfnisse, Anforderungsanalyse, Stakeholder Management "
            "und technisches Verständnis mit einem Fokus auf Product Ownership, Business Analyse "
            "und datenbasierte Produktentwicklung."
        )

    if any(
        term in normalized
        for term in (
            "python",
            "sql",
            "power bi",
            "pandas",
            "data",
            "daten",
            "skill",
            "kompetenz",
            "competency",
            "competencies",
            "skills",
            "machine learning",
        )
    ):
        return (
            "Yanas Kernkompetenzen umfassen digitale Produktentwicklung, Business Analyse, "
            "Anforderungsanalyse, Stakeholder Management, Product Discovery, agile Produktentwicklung, "
            "User & Customer Insights, Product Analytics und datenbasierte Entscheidungsfindung. "
            "Weitere Kompetenzen sind UX & Interaction Design, Prototyping & Validierung, "
            "Power BI, SQL, Python und Datenvisualisierung."
)

    if any(term in normalized for term in (
        "end-to-end", "arbeitsweise", "prozess", "ansatz",
        "approach", "process", "workflow"
    )):
        return (
            "Yanas Arbeitsweise verbindet Produkt, Business und Daten. "
            "Sie beginnt mit dem Verständnis von Nutzerbedürfnissen, Stakeholder-Perspektiven und Geschäftszielen, "
            "strukturiert anschließend Anforderungen, Prozesse und verfügbare Daten und übersetzt Erkenntnisse "
            "in Produktkonzepte und konkrete Anforderungen. Annahmen werden mit Nutzern, Stakeholdern und Daten "
            "validiert und Produkte gemeinsam mit Entwicklungsteams kontinuierlich verbessert."
        )

    if any(term in normalized for term in (
    "kontakt", "contact", "email", "e-mail",
    "erreichen", "nachricht", "message", "reach"
    )):
        return (
            "Nutze den Button „Kontakt aufnehmen“ im Kontaktbereich. "
            "Über das Kontaktformular kannst du Yana direkt eine Nachricht senden."
        )

    if any(term in normalized for term in (
        "standort", "ort", "location", "based", "gaildorf"
    )):
        return "Yana lebt in Gaildorf, Deutschland."

    return (
         "Dazu habe ich aktuell keine spezifische Information im Portfolio. "
         "Frag mich gerne nach Yanas Erfahrung, Projekten, digitaler Produktentwicklung, "
         "Business Analyse, Product Ownership, Data Analytics oder Kontaktmöglichkeiten."
    )


def _required_secret(name: str) -> str:
    value = st.secrets.get(name)

    if value is None or str(value).strip() == "":
        raise KeyError(name)

    return str(value).strip()


def send_contact_email(
    *,
    name: str,
    sender_email: str,
    company: str,
    message: str,
) -> tuple[bool, str]:
    """Sends a contact request via SMTP."""
    try:
        smtp_host = _required_secret("SMTP_HOST")
        smtp_port = int(_required_secret("SMTP_PORT"))
        smtp_user = _required_secret("SMTP_USER")
        smtp_password = _required_secret("SMTP_PASSWORD")
        contact_email = _required_secret("CONTACT_EMAIL")

        use_ssl = bool(st.secrets.get("SMTP_USE_SSL", False))
        use_starttls = bool(st.secrets.get("SMTP_USE_STARTTLS", not use_ssl))

        mail = EmailMessage()
        mail["Subject"] = f"New portfolio inquiry from {name}"
        mail["From"] = smtp_user
        mail["To"] = contact_email
        mail["Reply-To"] = sender_email
        mail.set_content(
            f"""
New contact request via the portfolio

Name: {name}
Email: {sender_email}
Company: {company or "Not provided"}

Message:
{message}
""".strip()
        )

        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(mail)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                if use_starttls:
                    server.starttls()
                    server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(mail)

        return True, (
            "Thank you! Your message has been sent to Yana successfully. "
            "She can reply directly to the email address you provided."
        )

    except KeyError:
        return False, (
            "Email delivery is not fully configured yet. "
            "Please check the .streamlit/secrets.toml file."
        )
    except ValueError:
        return False, "SMTP_PORT must be a valid number."
    except (OSError, smtplib.SMTPException) as exc:
        return False, (
            "Your message could not be sent right now. "
            "Please try again later. "
            f"Technical details: {type(exc).__name__}"
        )


def _portrait_header(
    *,
    portrait_data_url: str | None,
    subtitle: str,
) -> None:
    safe_portrait = html.escape(portrait_data_url or "", quote=True)
    avatar_html = (
        f'<img src="{safe_portrait}" alt="Portrait of Yana">'
        if safe_portrait
        else '<span aria-hidden="true">YP</span>'
    )

    st.html(
        f"""
        <div class="portfolio-chat">
            <div class="portfolio-chat-header">
                <div class="portfolio-chat-avatar">
                    {avatar_html}
                    <span class="portfolio-chat-status" aria-hidden="true"></span>
                </div>
                <div>
                    <strong>Yana Pfalzgraf</strong>
                    <span>{html.escape(subtitle)}</span>
                </div>
            </div>
        </div>
        """
    )


@st.dialog("Yana kontaktieren", width="small")
def contact_form_dialog(portrait_data_url: str | None = None) -> None:
    """Displays the contact form."""
    init_chat_state()
    _portrait_header(
        portrait_data_url=portrait_data_url,
        subtitle="Direkte Nachricht senden",
    )

    st.markdown("### Nachricht senden")
    st.caption(
        "Pflichtfelder sind mit * gekennzeichnet. Deine Angaben werden ausschließlich "
        "zur Bearbeitung deiner Kontaktanfrage verwendet."
    )

    with st.form("portfolio_contact_form", clear_on_submit=False):
        name = st.text_input("Name *", max_chars=100)
        sender_email = st.text_input("E-Mail -Adresse *", max_chars=180)
        company = st.text_input("Unternehmen", max_chars=140)
        message = st.text_area(
            "Nachricht *",
            height=150,
            max_chars=3000,
            placeholder=(
                "Erzähle mir kurz von der Position, dem Projekt oder Thema, "
                "über das du sprechen möchtest..."
            ),
        )
        privacy_accepted = st.checkbox(
               "Ich stimme der Verarbeitung meiner Angaben zur Bearbeitung "
                "dieser Kontaktanfrage zu. *"
        )

        submitted = st.form_submit_button(
            "Nachricht senden →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        clean_name = name.strip()
        clean_email = sender_email.strip()
        clean_company = company.strip()
        clean_message = message.strip()

        if len(clean_name) < 2:
            st.error("Bitte gib deinen Namen ein.")
        elif not _EMAIL_PATTERN.match(clean_email):
            st.error("Bitte gib eine gültige E-Mail-Adresse ein.")
        elif len(clean_message) < 10:
            st.error("Bitte gib eine etwas ausführlichere Nachricht ein.")
        elif not privacy_accepted:
            st.error("Bitte bestätige, dass deine Angaben für diese Anfrage verarbeitet werden dürfen.")
        else:
            with st.spinner("Nachricht wird gesendet …"):
                success, feedback = send_contact_email(
                    name=clean_name,
                    sender_email=clean_email,
                    company=clean_company,
                    message=clean_message,
                )

            if success:
                st.success(feedback)
                st.balloons()
            else:
                st.error(feedback)

    st.divider()

    if st.button(
        "Schließen",
        key="close_contact_form",
        use_container_width=True,
    ):
        st.session_state["contact_form_open"] = False
        st.rerun()

    st.html(
        '<p class="portfolio-chat-note">'
        "Das Formular übermittelt nur die Informationen, die du ausdrücklich absendest."
        "</p>"
    )


def render_floating_chat(portrait_data_url: str | None = None) -> None:
    """Renders a floating portfolio assistant in the bottom-right corner."""
    init_chat_state()

    with st.popover(
        "💬 Fragen zu Yanas Portfolio?",
        key="floating_portfolio_chat",
        help="Portfolio-Assistent öffnen",
    ):
        _portrait_header(
            portrait_data_url=portrait_data_url,
            subtitle="Portfolio-Assistant · verfügbar",
        )

        history = st.container(height=300)
        with history:
            for message in st.session_state["portfolio_chat_messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        prompt = st.chat_input(
            "Stelle eine Frage zum Portfolio …",
            key="floating_portfolio_chat_input",
        )

        if prompt:
            st.session_state["portfolio_chat_messages"].append(
                {"role": "user", "content": prompt}
            )
            st.session_state["portfolio_chat_messages"].append(
                {"role": "assistant", "content": create_chat_response(prompt)}
            )
            st.rerun()

        if st.button(
            "Chat neu starten",
            key="reset_floating_portfolio_chat",
            use_container_width=True,
        ):
            st.session_state["portfolio_chat_messages"] = [
                {"role": "assistant", "content": _INITIAL_MESSAGE}
            ]
            st.rerun()

        st.html(
            '<p class="portfolio-chat-note">'
            "Dieser Assistent beantwortet Fragen auf Grundlage der Inhalte dieses Portfolios."
            "</p>"
        )
