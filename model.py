from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    first_name = db.Column(db.String(50), nullable=False, unique=False)

    last_name = db.Column(db.String(50), nullable=False, unique=True)

    username = db.Column(db.Text,
                        nullable=False,
                        unique=True)

    password = db.Column(db.Text,
                        nullable=False,
                        unique=True)     

    image_url = db.Column(db.Text, nullable=False, default='https://media.istockphoto.com/vectors/no-image-available-picture-vector-id1287465175')

    def review_information(user, firstName, lastName, imageUrl):

        if firstName != "":
            user.first_name = firstName
            db.session.commit()
        if lastName != "":
            user.last_name = lastName
            db.session.commit()
        if imageUrl != "":
            user.image_url = imageUrl
            db.session.commit()
    
    def delete_user(user):
        db.session.delete(user)
        db.session.commit()        

    def __repr__(self):
        u = self
        return f"<User id={u.id} first name={u.first_name} last name={u.last_name} username={u.username} password={u.password} image url={u.image_url}>"

class Post(db.Model):

    __tablename__ = "post"

    def __repr__(self):
        return f"<Post: Title: {self.title} Content: {self.content} Time Created: {self.created_at} User Id: {self.user_id}>"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)

    title = db.Column(db.Text, nullable=False, unique=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship("User",
                    backref=db.backref("post", cascade="all, delete")
                )

    def delete_user_post(post_id):
        post = Post.query.get(post_id)
        db.session.delete(post)
        db.session.commit()

    def edit_user_post(post_id, new_title, new_content, edit_tags):
        post = Post.query.get(post_id)

        if new_title != "":
            post.title = new_title
            db.session.commit()
        if new_content != "":
            post.content = new_content
            db.session.commit()

            date_time = datetime.now()
            date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
            post.created_at = date_time
            db.session.commit()

        if edit_tags != "":
            post.tags.clear()

            for t in edit_tags:
                tag = Tag.query.filter_by(name=t).first()
                if tag:
                    post.tags.append(tag)
                    db.session.commit()





class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer,
                    primary_key=True)

    name = db.Column(db.Text, nullable=False, unique=True)

    posts = db.relationship('Post', secondary="posttags", cascade="all, delete", backref="tags")

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name}>"

    def edit_tag(tag_id, new_tag):
        tag = Tag.query.get_or_404(tag_id.id)

        if new_tag != "":
            tag.name = new_tag
            db.session.commit()


class PostTag(db.Model):

    __tablename__ = 'posttags'

    post_id = db.Column(db.Integer,
                        db.ForeignKey('post.id'),
                        primary_key=True)

    tag_id = db.Column(db.Integer,
                        db.ForeignKey('tags.id'),
                        primary_key=True)

    def add_tags(new_post_title, new_tags):
        post = Post.query.filter_by(title=new_post_title).first()

        for t in new_tags:
            tag = Tag.query.filter_by(name=t).first()
            post.tags.append(tag)
            db.session.commit()
