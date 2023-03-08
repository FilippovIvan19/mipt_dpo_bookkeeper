from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree
from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.view import View


class Bookkeeper:
    def __init__(self, view: AbstractView,
                 category_repo: AbstractRepository,
                 expense_repo: AbstractRepository,
                 budget_repo: AbstractRepository):
        self.view = view
        self.category_repo = category_repo
        self.expense_repo = expense_repo
        self.budget_repo = budget_repo

        self.view.register_expense_updater(self.update_expense)
        self.view.register_expense_deleter(self.delete_expense)
        self.view.register_expense_creator(self.create_expense)

        self.view.register_category_updater(self.update_category)
        self.view.register_category_deleter(self.delete_category)
        self.view.register_category_creator(self.create_category)

        self.view.register_budget_updater(self.budget_repo.update)
        self.view.register_budget_creator(self.budget_repo.add)

    def run(self):
        self.view.set_category_list(self.category_repo.get_all())
        self.view.set_expense_list(self.expense_repo.get_all())
        self.view.set_budget_list(self.budget_repo.get_all())
        self.view.run()

    def update_expense(self, expense: Expense):
        self.expense_repo.update(expense)
        self.view.set_expense_list(self.expense_repo.get_all())

    def delete_expense(self, pk: int):
        self.expense_repo.delete(pk)
        self.view.set_expense_list(self.expense_repo.get_all())

    def create_expense(self, expense: Expense) -> int:
        pk = self.expense_repo.add(expense)
        self.view.set_expense_list(self.expense_repo.get_all())
        return pk

    def update_category(self, category: Category):
        self.category_repo.update(category)
        self.view.set_category_list(self.category_repo.get_all())

    def delete_category(self, pk: int):
        self.category_repo.delete(pk)
        self.view.set_category_list(self.category_repo.get_all())

    def create_category(self, category: Category) -> int:
        pk = self.category_repo.add(category)
        self.view.set_category_list(self.category_repo.get_all())
        return pk


cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

view = View()
cat_repo = SQLiteRepository[Category]('database.db', Category)
exp_repo = SQLiteRepository[Expense]('database.db', Expense)
bud_repo = SQLiteRepository[Budget]('database.db', Budget)

bk = Bookkeeper(view, cat_repo, exp_repo, bud_repo)

Category.create_from_tree(read_tree(cats), bk.category_repo)
exp_repo.add(Expense(120, 1, comment='comment1'))
exp_repo.add(Expense(900, 7, comment='comment2'))
# bud_repo.add(Budget(1, None, 1000))
bud_repo.add(Budget(7, None, 7000))
bud_repo.add(Budget(30, None, 30000))


bk.run()
