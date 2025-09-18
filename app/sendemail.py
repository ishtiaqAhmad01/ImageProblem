from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html

def send_otp_email(user, otp):
    subject = "🔑 Password Reset Request"
    from_email = "noreplypennywise@gmail.com"
    to = [user.email]

    text_content = f"Your OTP is {otp}. It will expire in 5 minutes."

    html_content = format_html(f"""
        <div style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 12px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50; text-align: center;">Password Reset Request</h2>
                <p style="font-size: 16px; color: #555;">
                    Dear <b>{user.first_name}</b>, <br><br>
                    You requested to reset your password. Use the OTP below to proceed:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 28px; font-weight: bold; color: #ffffff; background: #007bff; padding: 12px 24px; border-radius: 8px; letter-spacing: 4px;">
                        {otp}
                    </span>
                </div>
                <p style="font-size: 14px; color: #888; text-align: center;">
                    ⚠️ This OTP will expire in <b>5 minutes</b>. If you didn’t request this, please ignore this email.
                </p>
            </div>
            <p style="font-size: 12px; color: #aaa; text-align: center; margin-top: 15px;">
                &copy; {2025} PennyWise App — Lahore, Pakistan
            </p>
        </div>
    """)

    # Create email
    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("-----------------")


if __name__ == "__main__":
    send_otp_email("s2023065078@umt.edu.pk", 123121)