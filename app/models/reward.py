from typing import Dict


class Reward:
  def __init__(self, quantity: int, appearances: int):
    self.quantity = quantity
    self.appearances = appearances

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      quantity= data.get('quantity'),
      appearances= data.get('appearances')
    )

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances
    }