from typing import Dict


class Reward:
  def __init__(self, quantity: int, appearances: int, type: str):
    self.quantity = quantity
    self.appearances = appearances
    self.type = type

  def __eq__(self, other):
    return self.quantity == other.quantity and self.type == other.type

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      quantity=data.get('quantity'),
      appearances=data.get('appearances'),
      type=data.get('type')
    )

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "type": self.type
    }


class GoldReward(Reward):
  def __init__(self, reward_data):
    Reward.__init__(self, reward_data['quantity'], reward_data['appearances'], "gold")


class PotionsReward(Reward):
  def __init__(self, reward_data):
    Reward.__init__(self, reward_data['quantity'], reward_data['appearances'], "potions")


class GearReward(Reward):
  def __init__(self, reward_data):
    Reward.__init__(self, 1, reward_data['appearances'], "gear")
    self.quality = reward_data['quality']

  def __eq__(self, other):
    return super().__eq__(other) and self.quality == other.quality

  @classmethod
  def from_dict(cls, data: Dict):
    return cls({
      "quality": data.get('quality'),
      "appearances": data.get('appearances')
    })

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "quality": self.quality,
      "type": self.type
    }

class DustReward(Reward):
  def __init__(self, reward_data):
    Reward.__init__(self, reward_data['quantity'], reward_data['appearances'], "dust")
    self.quality = reward_data['quality']

  def __eq__(self, other):
    return super().__eq__(other) and self.quality == other.quality

  @classmethod
  def from_dict(cls, data: Dict):
    return cls({
      'quantity': data.get('quantity'),
      'quality': data.get('quality'),
      'appearances': data.get('appearances')
    })

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "quality": self.quality,
      "type": self.type
    }