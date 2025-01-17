from supabase import Client

from src.db.dao import BaseDAO
from src.db.models import Inventory
from src.db.tables import SupabaseTables


class InventoryDAO(BaseDAO[Inventory]):
    """
    Data Access Object for managing Inventory items in the database.
    """

    def __init__(self, client: Client) -> None:
        super().__init__(client, SupabaseTables.INVENTORY, Inventory)
