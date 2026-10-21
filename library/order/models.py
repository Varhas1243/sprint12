from authentication.models import CustomUser
from book.models import Book
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    end_at = models.DateTimeField(null=True, blank=True, default=None)
    plated_end_at = models.DateTimeField()

    def __str__(self):
        """
        Magic method is redefined to show all information about Order.
        :return: book id, book name, book description, book count, book authors
        """
        order = {
            'id': self.id,
            'user': self.user,
            'book': self.book,
            'created_at': str(self.created_at),
            'end_at': str(self.end_at) if self.end_at else None,
            'plated_end_at': str(self.plated_end_at),
        }
        return str(order)[1:-1]

    def __repr__(self):
        """
        This magic method is redefined to show class and id of Order object.
        :return: class, id
        """
        return f'{self.__class__.__name__}(id={self.id})'

    def to_dict(self):
        """
        :return: dict contains order id, book id, user id, order created_at, order end_at, order plated_end_at
        :Example:
        | {
        |   'id': 8,
        |   'book': 8,
        |   'user': 8',
        |   'created_at': 1509393504,
        |   'end_at': 1509393504,
        |   'plated_end_at': 1509402866,
        | }
        """
        return {
            'id': self.id,
            'book': self.book.id,
            'user': self.user.id,
            'created_at': int(self.created_at.timestamp()),
            'end_at': int(self.end_at.timestamp()) if self.end_at else None,
            'plated_end_at': int(self.plated_end_at.timestamp()),
        }

    @staticmethod
    def create(user, book, plated_end_at):
        """
        :param user: the user who took the book
        :type user: CustomUser
        :param book: the book they took
        :type book: Book
        :param plated_end_at: planned return of data
        :type plated_end_at: int (timestamp)
        :return: a new order object which is also written into the DB
        """
        if user.pk is None or book.pk is None:
            return None
        books_taken = Order.objects.filter(book=book, end_at__isnull=True).count()
        if books_taken >= book.count:
            return None
        return Order.objects.create(user=user, book=book, plated_end_at=plated_end_at)

    @staticmethod
    def get_by_id(order_id):
        """
        :param order_id:
        :type order_id: int
        :return:  the object of the order, according to the specified id or null in case of its absence
        """
        return Order.objects.filter(id=order_id).first()

    def update(self, plated_end_at=None, end_at=None):
        """
        Updates order in the database with the specified parameters.\n
        :param plated_end_at: new plated_end_at
        :type plated_end_at: int (timestamp)
        :param end_at: new end_at
        :type plated_end_at: int (timestamp)
        :return: None
        """
        if plated_end_at is not None:
            self.plated_end_at = plated_end_at
        if end_at is not None:
            self.end_at = end_at
        self.save()

    @staticmethod
    def get_all():
        """
        :return: all orders
        """
        return list(Order.objects.order_by('id'))

    @staticmethod
    def get_not_returned_books():
        """
        :return:  all orders that do not have a return date (end_at)
        """
        return list(Order.objects.filter(end_at__isnull=True).order_by('id'))

    @staticmethod
    def delete_by_id(order_id):
        """
        :param order_id: an id of a user to be deleted
        :type order_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """
        deleted_count, _ = Order.objects.filter(id=order_id).delete()
        return deleted_count > 0
