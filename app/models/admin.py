from flask_admin.contrib.sqla import ModelView

class UserAdmin(ModelView):
    column_list = ('login', 'email', 'name', 'google_user', 'original_google_picture', 'about', 'picture', 'creation_date', 'last_login')
    column_filters = ('login', 'email', 'name', 'google_user', 'about')

class FavoriteAdmin(ModelView):
    column_list = ('data', 'user_id', 'starred')
    column_filters = ('starred', 'user_id')

class NoteAdmin(ModelView):
    column_list = ('content', 'creation_date', 'favorite_id')
    column_filters = ('content', 'favorite_id')
    
class PostAdmin(ModelView):
    column_list = ('title', 'content', 'guest_author', 'creation_date', 'user_id')
    column_filters = ('title', 'content', 'guest_author', 'user_id')

class CommentAdmin(ModelView):
    column_list = ('content', 'guest_author', 'creation_date', 'user_id', 'post_id')
    column_filters = ('content', 'guest_author', 'user_id', 'post_id') 

class NewsAdmin(ModelView):
    column_list = ('title', 'content', 'creation_date', 'user_id')
    column_filters = ('title', 'content', 'user_id')
    
class ReactionAdmin(ModelView):
    column_list = ('content', 'guest_author', 'creation_date', 'user_id', 'news_id')
    column_filters = ('content', 'guest_author', 'user_id', 'news_id')

class PostLikeItAdmin(ModelView):
    column_list = ('user_id', 'post_id')
    column_filters = ('user_id', 'post_id')

class PostHateItAdmin(ModelView):
    column_list = ('user_id', 'post_id')
    column_filters = ('user_id', 'post_id')
    
class CommentLikeItAdmin(ModelView):
    column_list = ('user_id', 'comment_id')
    column_filters = ('user_id', 'comment_id')

class CommentHateItAdmin(ModelView):
    column_list = ('user_id', 'comment_id')
    column_filters = ('user_id', 'comment_id')

class NewsLikeItAdmin(ModelView):
    column_list = ('user_id', 'news_id')
    column_filters = ('user_id', 'news_id')
    
class NewsHateItAdmin(ModelView):
    column_list = ('user_id', 'news_id')
    column_filters = ('user_id', 'news_id')

class ReactionLikeItAdmin(ModelView):
    column_list = ('user_id', 'reaction_id')
    column_filters = ('user_id', 'reaction_id')

class ReactionHateItAdmin(ModelView):
    column_list = ('user_id', 'reaction_id')
    column_filters = ('user_id', 'reaction_id')