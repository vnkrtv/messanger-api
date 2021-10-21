from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    Base class for app pydantic schemas
    """

    class Config:
        pass
        # extra = Extra.forbid
