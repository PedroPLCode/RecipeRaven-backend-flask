CREATE_USER_EMAIL_BODY = """
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
                            <p>Welcome in Recipe Raven App</p>
                            <p>Explore our app</p>
                            <ul>
                                <li>Advanced receipes search</li>
                                <li>Advanced user account features</li>
                                <li>News and Board</li>
                            </ul>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

CONFIRM_EMAIL_EMAIL_BODY = """
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
                            <p>Welcome in Recipe Raven App</p>
                            <p>Confirm your email address by clicking this link</p>
                            <p>{link}</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

DELETE_USER_EMAIL_BODY = """
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
                            <p>Recipe Raven App account deleted</p>
                            <p>Sad news {username}, but Your account was succesfully removed.</p>
                            <p>Hopefully you will be back someday.</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

RESET_PASSWORD_EMAIL_BODY = """
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
                            <p>Recipe Raven App password reset</p>
                            <p>{username}, reset your password by clicking this link</p>
                            <p>{link}</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

PASSWORD_CHANGED_EMAIL_BODY = """
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
                            <p>Recipe Raven App password changed</p>
                            <p>{username}, Your password was succesfully changed.</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

POST_COMMENT_EMAIL_BODY = """
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
                            <p>Recipe Raven App</p>
                            <p>{comment_author} just add a new comment to Your post {post_title}.</p>
                            <p>{post_comment}</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

NEWS_REACTION_EMAIL_BODY = """
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
                            <p>Recipe Raven App</p>
                            <p>{reaction_author} just add a new reaction to Your News {news_title}.</p>
                            <p>{news_reaction}</p>
                            <p>Have a nice day!</p>
                            <p>Team <strong>Receipe Raven</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-top: 20px;">
                            <a href="https://reciperaven.pl" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; font-family: Arial, sans-serif; border-radius: 5px;">Odwiedź naszą stronę</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""