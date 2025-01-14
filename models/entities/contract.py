from typing import List

from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entities.base import Base


class Contract(Base):
    __tablename__ = 'contracts'

    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    remaining_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    signed: Mapped[bool] = mapped_column(default=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    commercial_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    client: Mapped["Client"] = relationship(back_populates="contracts")
    commercial: Mapped["User"] = relationship(
        back_populates="managed_contracts",
        foreign_keys=[commercial_id]
    )
    events: Mapped[List["Event"]] = relationship(back_populates="contract")

    def __repr__(self) -> str:
        return (
            f"Contract(id={self.id!r}, "
            f"client_id={self.client_id!r}, "
            f"total_amount={self.total_amount!r}, "
            f"remaining_amount={self.remaining_amount!r}, "
            f"signed={self.signed!r})"
        )
