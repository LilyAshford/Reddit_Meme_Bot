from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class RedditPost(Base):
    __tablename__ = 'reddit_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    upvotes = Column(Integer)
    url = Column(String)
    subreddit = Column(String)
    created_utc = Column(DateTime)

class Trend(Base):
    __tablename__ = 'trends'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    count = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

class MemeImage(Base):
    __tablename__ = 'meme_images'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    upvotes = Column(Integer)
    subreddit = Column(String)
    original_url = Column(String)
    image_data = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///reddit_memes.db', pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_to_db(posts, trends):
    db = SessionLocal()
    try:
        for post in posts:
            db_post = RedditPost(
            title=post['title'],
            upvotes=post['upvotes'],
            url=post['url'],
            subreddit=post['subreddit'],
            created_utc=datetime.fromtimestamp(post['created_utc'])
            )
            db.add(db_post)

        for word, count in trends:
            db_trend = Trend(word=word, count=count)
            db.add(db_trend)


    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while savong meme: {str(e)}", exc_info=True)
        raise e

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while saving meme: {str(e)}", exc_info=True)
        raise e

    finally:
        db.commit()
        logger.info("Successfully committed all changes to database")
        db.close()

def save_meme_to_db(post, watermarked_image):
    db = SessionLocal()
    try:
        watermarked_image.seek(0)
        image_data = watermarked_image.read()

        if not image_data:
            logger.error("No image data available to save")
            return False

        db_meme = MemeImage(
            title=post['title'],
            upvotes=post['upvotes'],
            subreddit=post['subreddit'],
            original_url=post['url'],
            image_data=watermarked_image.read()
            )
        db.add(db_meme)
        db.commit()
        logger.info("Successfully saved meme to database")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while savong meme: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while saving meme: {str(e)}", exc_info=True)
        raise e
    finally:
        db.close()