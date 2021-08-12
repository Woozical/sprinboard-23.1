from models import db, Post, User, Tag, PostTag
from app import app
from random import randint

db.drop_all()
db.create_all()

users = [
    User(first_name='Sara', last_name='Sanders'),
    User(first_name='John', last_name='Doe'),
    User(first_name='Diane', last_name='Diedrich'),
    User(first_name='Robert', last_name='Reiner'),
    User(first_name='Michael', last_name='MacGillicudy'),
    User(first_name='Donald', last_name='Dunn'),
    User(first_name='Daniel', last_name='Dunn')
]

posts = [
    Post(title='My first puppy', content="Look at my puppy. Isn't he so cute?", poster_id=randint(1, len(users))),
    Post(title='Movie Review: Lighthouse', content="My dad didn't understand it, but I thought it waas great.", poster_id=randint(1, len(users))),
    Post(title='Oregon Trip', content="The fam and I went up to Oregon last week, it was pretty cool.", poster_id=randint(1, len(users))),
    Post(title='Back Propagation in Neural Nets', content="I couldn't tell you mathematically how they work, but I guess I understand it.", poster_id=randint(1, len(users))),
    Post(title='My latest tortoise', content="I just got another tortoise. Isn't she so cute?", poster_id=randint(1, len(users))),
    Post(title='When is TES6 coming?', content="Seriously, does anyone know? DM me if you've got the scoop.", poster_id=randint(1, len(users))),
    Post(title='Found something while cycling', content="It's a baby garter snake. He tried to bite me, but he was too small.", poster_id=randint(1, len(users))),
    Post(title='Teaching my cat how to skateboard', content="Everyone thought I was crazy, but I finally did it. Who's laughing now, huh?", poster_id=randint(1, len(users)))
]

tags = [
    Tag(name="winning"), Tag(name='pets'), Tag(name='summer'), Tag(name='science'), Tag(name='video games')
]

db.session.add_all(users)
db.session.commit()
db.session.add_all(posts)
db.session.commit()
db.session.add_all(tags)
db.session.commit()

posts[0].tags.append(tags[1])
posts[2].tags.append(tags[2])
posts[3].tags.append(tags[3])
posts[4].tags.append(tags[1])
posts[4].tags.append(tags[2])
posts[5].tags.append(tags[4])
posts[6].tags.append(tags[2])
posts[6].tags.append(tags[0])
posts[7].tags.append(tags[0])
posts[7].tags.append(tags[1])

db.session.add_all(posts)

db.session.commit()