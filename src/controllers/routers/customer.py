"""
This module defines the router for handling customer-related operations, including wallet management.
"""

from fastapi import Depends, status
from pydantic import PositiveFloat

from src.controllers.routers import BaseRouter
from src.db.dao import BaseDAO
from src.db.dependencies import get_customer_dao
from src.db.models import Customer
from src.utils.responses.API_response import APIResponse
from src.utils.types import UuidStr

customers_router = BaseRouter[Customer](
    prefix="/customers",
    tags=["Customers"],
    name="Customer",
    model=Customer,
    get_dao=get_customer_dao,
).build_router()


@customers_router.put("/deduct/{id}")
async def deduct_money(
    id: UuidStr,
    amount: PositiveFloat,
    customer_dao: BaseDAO[Customer] = Depends(get_customer_dao),
) -> APIResponse:
    """
    Deducts a specified amount of money from the customer's wallet.

    Args:
        id (UuidStr): The UUID of the customer.
        amount (PositiveFloat): The amount to deduct.
        customer_dao (BaseDAO[Customer]): The data access object for customers.

    Returns:
        APIResponse: The response indicating success or failure.
    """
    try:
        customer = customer_dao.get_by_id(id)
        if not customer:
            return APIResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Customer not found",
            )
        curr_wallet = customer.wallet
        if curr_wallet < amount:
            return APIResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Not enough money in wallet",
                data={"wallet": curr_wallet},
            )
        new_wallet = curr_wallet - amount
        updated_customer = customer_dao.update(id, {"wallet": new_wallet})

        assert updated_customer is not None

        return APIResponse(
            status_code=status.HTTP_200_OK,
            message="Money deducted successfully",
            data=updated_customer.model_dump(),
        )
    except Exception as e:
        return APIResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e),
        )


@customers_router.put("/add_money/{id}")
async def add_money_to_wallet(
    id: UuidStr,
    money: PositiveFloat,
    dao: BaseDAO[Customer] = Depends(get_customer_dao),
) -> APIResponse:
    """
    Adds a specified amount of money to the customer's wallet.

    Args:
        id (UuidStr): The UUID of the customer.
        money (PositiveFloat): The amount of money to add.
        dao (BaseDAO): The data access object for customers.

    Returns:
        APIResponse: The response indicating success or failure.
    """
    # Get the customer by ID using the DAO
    customer = dao.get_by_id(id)
    if not customer:
        return APIResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Customer not found",
        )
    prev_money = customer.wallet
    # Add money to the wallet
    new_wallet_amount = prev_money + money
    updated_customer = dao.update(id, {"wallet": new_wallet_amount})
    if updated_customer:
        return APIResponse(
            status_code=status.HTTP_200_OK,
            message="Money added to wallet",
            data={"wallet": updated_customer.wallet},
        )
    return APIResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Failed to update wallet",
    )

# API Calls:

# GET /customers/
# Description: Retrieve all customers.
# Method: GET
# URL: http://localhost:8000/customers/

# POST /customers/
# Description: Create a new customer.
# Method: POST
# URL: http://localhost:8000/customers/
# Body:
# {
#     "name": "John Doe",
#     "email": "john.doe@example.com",
#     "wallet": 100.00
# }

# POST /customers/many
# Description: Create multiple new customers.
# Method: POST
# URL: http://localhost:8000/customers/many
# Body:
# [
#     {
#         "name": "Jane Smith",
#         "email": "jane.smith@example.com",
#         "wallet": 150.00
#     },
#     {
#         "name": "Alice Johnson",
#         "email": "alice.johnson@example.com",
#         "wallet": 200.00
#     }
# ]

# GET /customers/{id}
# Description: Retrieve a customer by ID.
# Method: GET
# URL: http://localhost:8000/customers/{id}

# PUT /customers/{id}
# Description: Update a customer by ID.
# Method: PUT
# URL: http://localhost:8000/customers/{id}
# Body:
# {
#     "email": "new.email@example.com",
#     "wallet": 120.00
# }

# DELETE /customers/{id}
# Description: Delete a customer by ID.
# Method: DELETE
# URL: http://localhost:8000/customers/{id}"

# PUT /customers/deduct_money/{id}
# Description: Deduct a specified amount of money from the customer's wallet.
# Method: PUT
# URL: http://localhost:8000/customers/{id}
# Body:
# {
#     "amount": 20.00
# }

# PUT /customers/add_money/{id}
# Description: Add a specified amount of money to the customer's wallet.
# Method: PUT
# URL: http://localhost:8000/customers/add_money/{id}
# Body:
# {
#     "money": 50.00
# }
