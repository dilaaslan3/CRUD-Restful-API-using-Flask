from bson import ObjectId

from plugins.errors import DilaError


class PostService(object): #bir class bir yerden inherit ediliyorsa bu parametre olarak classa verilir ama hiçbir yerden inherit edilmiyorsa parametre olarak object verilir
    def __init__(self, db): #classımızın constructorıdır ilk parametresi mutlaka self olmalıdır, ikinci parametre olarak db yi verdik çünkü bu classın yapacağı iş dbye gitmek
        self.db = db

    def get_post(self, post_id, raise_exception=False):
        document = self.db.posts.find_one({
            "_id": ObjectId(post_id)
        })
        if raise_exception and not document:
            raise DilaError(
                err_msg="Document not found by given id: <{}>, in collection: <{}>".format(post_id, "posts"),
                err_code="errors.resourceNotFound",
                status_code=404
            )
        return document
