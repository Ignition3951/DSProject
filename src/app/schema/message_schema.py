from pydantic import BaseModel,Field
from typing import List

class MessageJson(BaseModel):
    upi_id: str = Field(title="upi_id",description="This is the transaction id which is present in the message")
    bank_name: str = Field(title="bank_name",description="This is the bank name which is present in the message")
    transaction_date: str = Field(title="transaction_date",description="This is the transaction date which is present in the message")
    currency: str = Field(title="currency",description="This is the currency which is present in the message")
    transaction_amount: str = Field(title="transaction_amount",description="This is the transaction amount which is present in the message")
    transaction_details: str = Field(title="transaction_details",description="This is the credited/debited which is present in the message")
