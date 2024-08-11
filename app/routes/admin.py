from flask_admin.contrib.sqla import ModelView
from app import admin, db
from app.models.admin import UserAdmin, FavoriteAdmin, NoteAdmin, PostAdmin, PostLikeItAdmin, PostHateItAdmin, CommentAdmin, CommentLikeItAdmin, CommentHateItAdmin, NewsAdmin, NewsLikeItAdmin, NewsHateItAdmin, ReactionAdmin, ReactionLikeItAdmin, ReactionHateItAdmin
from app.models import User, Post, PostLikeIt, PostHateIt, Comment, CommentLikeIt, CommentHateIt, Favorite, Note, News, NewsLikeIt, NewsHateIt, Reaction, ReactionLikeIt, ReactionHateIt
    
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