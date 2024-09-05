from flask_admin import AdminIndexView
from app import admin, db, app
from datetime import datetime as dt
from werkzeug.security import check_password_hash
from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from app.models.admin import (UserAdmin, 
                              FavoriteAdmin, 
                              NoteAdmin, 
                              PostAdmin, 
                              PostLikeItAdmin, 
                              PostHateItAdmin, 
                              CommentAdmin, 
                              CommentLikeItAdmin, 
                              CommentHateItAdmin, 
                              NewsAdmin, 
                              NewsLikeItAdmin, 
                              NewsHateItAdmin, 
                              ReactionAdmin, 
                              ReactionLikeItAdmin, 
                              ReactionHateItAdmin, 
                              NewsletterAdmin
                              )
from app.models import (User, 
                        Post, 
                        PostLikeIt, 
                        PostHateIt, 
                        Comment, 
                        CommentLikeIt, 
                        CommentHateIt, 
                        Favorite, 
                        Note, 
                        News, 
                        NewsLikeIt, 
                        NewsHateIt, 
                        Reaction, 
                        ReactionLikeIt, 
                        ReactionHateIt, 
                        Newsletter
                        )
from app.utils import send_email

admin.add_view(UserAdmin(User, db.session))
admin.add_view(FavoriteAdmin(Favorite, db.session))
admin.add_view(NoteAdmin(Note, db.session))
admin.add_view(PostAdmin(Post, db.session))
admin.add_view(PostLikeItAdmin(PostLikeIt, db.session))
admin.add_view(PostHateItAdmin(PostHateIt, db.session))
admin.add_view(CommentAdmin(Comment, db.session))
admin.add_view(CommentLikeItAdmin(CommentLikeIt, db.session))
admin.add_view(CommentHateItAdmin(CommentHateIt, db.session))
admin.add_view(NewsAdmin(News, db.session))
admin.add_view(NewsLikeItAdmin(NewsLikeIt, db.session))
admin.add_view(NewsHateItAdmin(NewsHateIt, db.session))
admin.add_view(ReactionAdmin(Reaction, db.session))
admin.add_view(ReactionLikeItAdmin(ReactionLikeIt, db.session))
admin.add_view(ReactionHateItAdmin(ReactionHateIt, db.session))
admin.add_view(NewsletterAdmin(Newsletter, db.session))

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

class MyAdminIndexView(AdminIndexView):
    def __init__(self, *args, **kwargs):
        super(MyAdminIndexView, self).__init__(*args, **kwargs)
        self.template_mode = 'admin' 
        

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_user():
    return dict(date_and_time=dt.utcnow())


@app.route('/newsletter', methods=['POST'])
@login_required
def admin_newsletter():
    title = request.form['topic']
    content = request.form['content']
        
    all_users = User.query.all()
    email_addresses = [user.email for user in all_users]
        
    for single_email_adress in email_addresses:
        send_email(single_email_adress, title, content)
        
    new_newsletter = Newsletter(title=title, 
                                content=content, 
                                recipients=email_addresses)
    db.session.add(new_newsletter)
    db.session.commit()
    flash(f'Newsletter sent to {len(email_addresses)} recipients and saved in db.',
    'success')

        
    return redirect(url_for('admin.index'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'{dt.utcnow()} Logged in successfully.'
                  f'Welcome back {user.name if user.name else user.login}', 
                  'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('admin/admin_login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('admin_login'))