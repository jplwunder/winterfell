from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = os.getenv("MAIL_PORT"),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates")
)

mail = FastMail(config = config)

def create_message(reciepients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=reciepients,
        subject=subject,
        body=body,
        subtype="html"
    )
    return message

def generate_confirmation_email(link: str) -> str:
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Confirme seu e-mail</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <!-- Container Principal -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 460px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          
          <!-- Banner / Topo -->
          <tr>
            <td align="center" style="padding: 36px 32px 12px 32px;">
              <div style="display: inline-block; width: 48px; height: 48px; line-height: 48px; background-color: #eff6ff; border-radius: 12px; font-size: 22px;">
                ✉️
              </div>
            </td>
          </tr>

          <!-- Conteúdo -->
          <tr>
            <td align="center" style="padding: 0 32px 36px 32px;">
              <h1 style="color: #0f172a; font-size: 20px; font-weight: 700; margin: 0 0 12px 0; text-align: center;">
                Confirme seu e-mail
              </h1>
              
              <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0 0 28px 0; text-align: center;">
                Falta pouco para concluir sua inscrição! Clique no botão abaixo para validar seu endereço de e-mail e ativar seu acesso.
              </p>

              <!-- Botão (compatível com vários clientes de e-mail) -->
              <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                <tr>
                  <td align="center" bgcolor="#2563eb" style="border-radius: 8px;">
                    <a href="{link}" target="_blank" style="display: inline-block; padding: 12px 28px; font-size: 14px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 8px; background-color: #2563eb;">
                      Confirmar E-mail
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Divisor -->
              <div style="border-top: 1px solid #f1f5f9; margin: 28px 0 20px 0;"></div>

              <p style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                Se você não criou uma conta ou não realizou a inscrição neste evento, basta ignorar este e-mail.
              </p>
            </td>
          </tr>
        </table>

        <!-- Rodapé fora do card -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 460px; margin-top: 20px;">
          <tr>
            <td align="center" style="color: #94a3b8; font-size: 12px;">
              <p style="margin: 0;">Dois ou Mais Eventos &bull; Todos os direitos reservados</p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""

def generate_ticket_email(
    user_name: str, 
    event_name: str, 
    event_date: str, 
    event_location: str, 
    ticket_code: str,
    qr_code_url: str = None
) -> str:
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Seu Ingresso - {event_name}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <!-- Container Principal -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 480px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          
          <!-- Banner Superior / Status -->
          <tr>
            <td align="center" style="background-color: #0f172a; padding: 28px 24px; text-align: center;">
              <span style="display: inline-block; background-color: rgba(16, 185, 129, 0.2); color: #10b981; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 4px 12px; border-radius: 9999px; margin-bottom: 8px;">
                Inscrição Confirmada
              </span>
              <h1 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0; line-height: 1.3;">
                {event_name}
              </h1>
            </td>
          </tr>

          <!-- Corpo do E-mail -->
          <tr>
            <td style="padding: 28px 28px 12px 28px;">
              <p style="color: #334155; font-size: 15px; margin: 0 0 20px 0;">
                Olá, <strong>{user_name}</strong>! Seu ingresso foi gerado com sucesso. Apresente este e-mail ou o código na entrada do evento.
              </p>

              <!-- Detalhes do Evento -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                <tr>
                  <td style="padding-bottom: 10px;">
                    <span style="color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 2px;">Data & Horário</span>
                    <span style="color: #0f172a; font-size: 14px; font-weight: 600;">📅 {event_date}</span>
                  </td>
                </tr>
                <tr>
                  <td>
                    <span style="color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 2px;">Local</span>
                    <span style="color: #0f172a; font-size: 14px; font-weight: 600;">📍 {event_location}</span>
                  </td>
                </tr>
              </table>

              <!-- Card do Ticket/QR Code -->
              <div style="border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px; text-align: center; background-color: #ffffff; margin-bottom: 20px;">
                <span style="color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 8px;">
                  Código do Ingresso
                </span>
                
                {"<img src='" + qr_code_url + "' alt='QR Code' width='140' height='140' style='margin: 8px auto 12px auto; display: block;' />" if qr_code_url else ""}

                <div style="font-family: monospace, Courier, monospace; font-size: 16px; font-weight: 700; color: #2563eb; background-color: #eff6ff; padding: 8px 12px; border-radius: 6px; word-break: break-all; display: inline-block;">
                  {ticket_code}
                </div>
              </div>

            </td>
          </tr>

          <!-- Divisor -->
          <tr>
            <td style="padding: 0 28px;">
              <div style="border-top: 1px solid #f1f5f9;"></div>
            </td>
          </tr>

          <!-- Rodapé do Card -->
          <tr>
            <td align="center" style="padding: 20px 28px 28px 28px;">
              <p style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                Guarde este e-mail com você. Se tiver qualquer dúvida, entre em contato com a organização do evento.
              </p>
            </td>
          </tr>

        </table>

        <!-- Rodapé Externo -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 480px; margin-top: 20px;">
          <tr>
            <td align="center" style="color: #94a3b8; font-size: 12px;">
              <p style="margin: 0;">Dois ou Mais Eventos &bull; Todos os direitos reservados</p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""

def generate_staff_added_email(
    user_name: str,
    event_name: str, 
    event_date: str, 
    event_location: str, 
    staff_role: str = "Apoio / Credenciamento"
) -> str:
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Acesso Staff - {event_name}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <!-- Container Principal -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 480px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
          
          <!-- Banner Superior / Distintivo de Staff -->
          <tr>
            <td align="center" style="background-color: #0f172a; padding: 28px 24px; text-align: center;">
              <span style="display: inline-block; background-color: rgba(99, 102, 241, 0.25); color: #818cf8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 4px 12px; border-radius: 9999px; margin-bottom: 8px;">
                Equipe de Organização &bull; Staff
              </span>
              <h1 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0; line-height: 1.3;">
                {event_name}
              </h1>
            </td>
          </tr>

          <!-- Corpo do E-mail -->
          <tr>
            <td style="padding: 28px 28px 12px 28px;">
              <p style="color: #334155; font-size: 15px; margin: 0 0 20px 0;">
                Olá, <strong>{user_name}</strong>! Você foi adicionado(a) como membro da equipe de <strong>Staff</strong> para este evento.
              </p>

              <!-- Bloco da Função/Cargo -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 16px; margin-bottom: 20px;">
                <tr>
                  <td>
                    <span style="color: #166534; font-size: 11px; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 2px;">Sua Função Atribuída</span>
                    <span style="color: #15803d; font-size: 15px; font-weight: 700;">🛡️ {staff_role}</span>
                  </td>
                </tr>
              </table>

              <!-- Detalhes do Evento -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                <tr>
                  <td style="padding-bottom: 10px;">
                    <span style="color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 2px;">Data & Horário</span>
                    <span style="color: #0f172a; font-size: 14px; font-weight: 600;">📅 {event_date}</span>
                  </td>
                </tr>
                <tr>
                  <td>
                    <span style="color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; display: block; margin-bottom: 2px;">Local</span>
                    <span style="color: #0f172a; font-size: 14px; font-weight: 600;">📍 {event_location}</span>
                  </td>
                </tr>
              </table>

              <!-- Instruções / Permissões -->
              <p style="color: #64748b; font-size: 13px; line-height: 1.5; margin: 0 0 20px 0;">
                A partir de agora, você possui privilégios de acesso ao painel do evento para auxiliar na validação de ingressos e gestão de participantes.
              </p>

            </td>
          </tr>

          <!-- Divisor -->
          <tr>
            <td style="padding: 0 28px;">
              <div style="border-top: 1px solid #f1f5f9;"></div>
            </td>
          </tr>

          <!-- Rodapé do Card -->
          <tr>
            <td align="center" style="padding: 20px 28px 28px 28px;">
              <p style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin: 0; text-align: center;">
                Dúvidas sobre sua atuação? Procure o organizador principal do evento.
              </p>
            </td>
          </tr>

        </table>

        <!-- Rodapé Externo -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 480px; margin-top: 20px;">
          <tr>
            <td align="center" style="color: #94a3b8; font-size: 12px;">
              <p style="margin: 0;">Dois ou Mais Eventos &bull; Painel Organizador</p>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>
</body>
</html>"""