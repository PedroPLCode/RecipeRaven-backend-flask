EMAIL_BODY = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome in Recipe Raven App!</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td align="center" style="padding: 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; padding: 20px;">
                    <tr>
                        <td style="text-align: center; padding-bottom: 20px;">
                            <h1 style="font-family: Arial, sans-serif; color: #333;">Welcome, {username}!</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
                            <p>Dziękujemy za zapisanie się do naszego newslettera, {username}. Cieszymy się, że jesteś z nami!</p>
                            <p>Oto, co przygotowaliśmy dla Ciebie w tym miesiącu:</p>
                            <ul>
                                <li>Nowe artykuły na blogu</li>
                                <li>Specjalne oferty i zniżki</li>
                                <li>Porady i wskazówki</li>
                            </ul>
                            <p>Życzymy miłego dnia!</p>
                            <p>Zespół <strong>Twojej Firmy</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://twojafirma.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""