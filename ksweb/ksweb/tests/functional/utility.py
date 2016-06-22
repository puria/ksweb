#  Utility Class for tests
from bson import ObjectId
from ksweb import model


def get_or_create_category_from_id(category_id):
    category = model.Category.query.get(_id=ObjectId(category_id))
    if not category:
        category = model.Category(
            _id=ObjectId(category_id),
            name='TestCategory'
        )
    return category


def get_or_create_category_from_name(category_name):
    category = model.Category.query.get(name=category_name)
    if not category:
        category = model.Category(
            name=category_name
        )
    return category


def create_qa(title, category_id, question, tooltip, link, type, answers):
    qa = model.Qa(
        title=title,
        category_id=category_id,
        question=question,
        tooltip=tooltip,
        link=link,
        type=type,
        answers=answers
    )
    return qa
